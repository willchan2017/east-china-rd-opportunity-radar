from datetime import date

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Company, Event, OpportunityAssessment, OpportunityStage, SignalCategory, SignalDefinition


SIGNALS = [
    ("B01", "融资或资本动作", SignalCategory.B, "企业完成融资、上市或重大资本动作", {"keywords": ["融资", "IPO", "定增"], "minimum_evidence": 1}),
    ("B02", "业务扩张", SignalCategory.B, "新基地、新产品线或业务规模明显扩张", {"keywords": ["基地", "量产", "扩产"], "minimum_evidence": 1}),
    ("R01", "研发组织扩张", SignalCategory.R, "研发团队、研发中心或跨区域协作规模扩大", {"keywords": ["研发中心", "研发招聘", "研发团队"], "minimum_evidence": 1}),
    ("R02", "工具链复杂度上升", SignalCategory.R, "多团队、多工具或合规要求带来研发管理压力", {"keywords": ["协同", "合规", "流程"], "minimum_evidence": 2}),
    ("P01", "明确招采", SignalCategory.P, "公开招标、采购公告或供应商征集", {"keywords": ["招标", "采购", "供应商"], "minimum_evidence": 1}),
    ("P02", "工具替换", SignalCategory.P, "公开证据显示现有研发工具升级或替换", {"keywords": ["Jira", "ALM", "研发管理平台"], "minimum_evidence": 1}),
]


def seed() -> None:
    with SessionLocal() as db:
        for code, name, category, description, rule_config in SIGNALS:
            if not db.scalar(select(SignalDefinition.id).where(SignalDefinition.code == code)):
                db.add(SignalDefinition(code=code, name=name, category=category, description=description, rule_config=rule_config))

        if not db.scalar(select(Company.id).where(Company.name == "华东精研科技（模拟）")):
            company = Company(
                name="华东精研科技（模拟）",
                industry="半导体与集成电路",
                province="上海",
                city="上海",
                rd_size=320,
                icp_tier="A",
                crm_status="未建档",
                current_stage=OpportunityStage.S2,
                is_sample=True,
            )
            db.add(company)
            db.flush()
            event = Event(
                company_id=company.id,
                event_date=date(2026, 9, 18),
                event_type="研发组织扩张",
                event_title="新增跨区域研发团队（模拟事件）",
                event_description="用于演示事件时间线与机会状态，不代表真实企业情报。",
                source_url="https://example.com/mock-radar-event",
                source_type="模拟数据",
                evidence_excerpt="模拟证据：企业计划扩大跨区域研发协作团队。",
                verification_status="模拟数据",
                confidence_level="low",
                is_sample=True,
            )
            db.add(event)
            db.flush()
            db.add(OpportunityAssessment(
                company_id=company.id,
                previous_stage=OpportunityStage.S1,
                stage=OpportunityStage.S2,
                rationale="模拟事件体现跨区域研发协作压力，仅用于产品演示。",
                event_ids=[event.id],
                assessor_type="manual",
                assessor_name="系统种子",
            ))
        db.commit()


if __name__ == "__main__":
    seed()

