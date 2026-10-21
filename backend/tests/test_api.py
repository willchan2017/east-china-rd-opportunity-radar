from datetime import date
from io import BytesIO

from openpyxl import Workbook


def company_payload(name="测试精密研发（模拟）"):
    return {"name": name, "industry": "工业自动化", "province": "江苏", "city": "苏州", "rd_size": 120, "icp_tier": "A", "aliases": [{"alias": "测试研发"}]}


def test_company_crud_and_filters(client):
    created = client.post("/api/v1/companies", json=company_payload())
    assert created.status_code == 201
    company_id = created.json()["id"]
    result = client.get("/api/v1/companies", params={"q": "测试研发", "province": "江苏", "rd_size_min": 100})
    assert result.status_code == 200
    assert result.json()["total"] == 1
    updated = client.patch(f"/api/v1/companies/{company_id}", json={"sales_owner": "王销售"})
    assert updated.json()["sales_owner"] == "王销售"


def test_event_and_assessment_history(client):
    company = client.post("/api/v1/companies", json=company_payload()).json()
    event = client.post("/api/v1/events", json={
        "company_id": company["id"], "event_date": str(date.today()), "event_type": "研发组织扩张",
        "event_title": "建立研发中心（模拟）", "event_description": "测试描述",
        "source_url": "https://example.com/evidence", "source_type": "手工导入", "evidence_excerpt": "测试证据原文",
    })
    assert event.status_code == 201
    assessment = client.post(f"/api/v1/companies/{company['id']}/assessments", json={
        "stage": "S2", "rationale": "存在研发组织扩张的模拟测试证据", "event_ids": [event.json()["id"]]
    })
    assert assessment.status_code == 201
    assert assessment.json()["previous_stage"] == "S0"
    assert client.get(f"/api/v1/companies/{company['id']}").json()["current_stage"] == "S2"


def test_excel_import_supports_universe_headers(client):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "半导体"
    sheet.append(["企业名称", "一级行业", "总部/华东研发地", "软件/嵌入式研发规模(估)", "销售优先级"])
    sheet.append(["导入企业（模拟）", "半导体与集成电路", "上海", "100+", "★★★★★"])
    stream = BytesIO(); workbook.save(stream)
    result = client.post("/api/v1/companies/import", files={"file": ("universe.xlsx", stream.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert result.status_code == 200
    assert result.json() == {"created": 1, "skipped": 0, "errors": []}
    imported = client.get("/api/v1/companies").json()["items"][0]
    assert imported["rd_size"] == 100
    assert imported["icp_tier"] == "A"


def test_ai_contract_rejects_unsupported_facts():
    from pydantic import ValidationError
    from app.schemas import AIEventExtraction
    try:
        AIEventExtraction(company_name="某企业", event_date=None, event_type=None, event_title="发生扩张", event_description=None, evidence_excerpt=None, source_url="https://example.com", business_impact=None, purchase_relevance=None, confidence_level="low")
        assert False, "expected validation error"
    except ValidationError:
        pass

