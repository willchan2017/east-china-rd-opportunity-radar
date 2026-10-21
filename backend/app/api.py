import io

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app import models, schemas, services
from app.database import get_db

router = APIRouter(prefix="/api/v1")


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/dashboard", response_model=schemas.DashboardSummary)
def get_dashboard(db: Session = Depends(get_db)):
    return services.dashboard_summary(db)


@router.post("/companies", response_model=schemas.CompanyRead, status_code=status.HTTP_201_CREATED)
def create_company(payload: schemas.CompanyCreate, db: Session = Depends(get_db)):
    aliases = [models.CompanyAlias(**alias.model_dump()) for alias in payload.aliases]
    company = models.Company(**payload.model_dump(exclude={"aliases"}), aliases=aliases)
    db.add(company)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="企业名称或统一社会信用代码已存在") from exc
    db.refresh(company)
    return company


@router.get("/companies", response_model=schemas.CompanyList)
def list_companies(
    q: str | None = None,
    province: str | None = None,
    industry: str | None = None,
    icp_tier: str | None = None,
    stage: models.OpportunityStage | None = None,
    rd_size_min: int | None = Query(default=None, ge=0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    base = services.company_query(q, province, industry, icp_tier, stage, rd_size_min)
    total = db.scalar(select(func.count()).select_from(base.order_by(None).subquery())) or 0
    items = db.scalars(base.order_by(models.Company.updated_at.desc()).offset((page - 1) * page_size).limit(page_size)).unique().all()
    return schemas.CompanyList(items=items, total=total, page=page, page_size=page_size)


@router.get("/companies/export")
def download_companies(db: Session = Depends(get_db)):
    companies = db.scalars(select(models.Company).order_by(models.Company.name)).all()
    content = services.export_companies(companies)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="companies.xlsx"'},
    )


@router.post("/companies/import", response_model=schemas.ImportResult)
async def upload_companies(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not (file.filename or "").lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="仅支持 .xlsx 文件")
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="文件不得超过 10MB")
    try:
        return services.import_companies(db, content)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="无法读取 Excel 文件") from exc


@router.get("/companies/{company_id}", response_model=schemas.CompanyRead)
def get_company(company_id: str, db: Session = Depends(get_db)):
    company = db.scalar(
        select(models.Company).options(selectinload(models.Company.aliases)).where(models.Company.id == company_id)
    )
    if not company:
        raise HTTPException(status_code=404, detail="企业不存在")
    return company


@router.patch("/companies/{company_id}", response_model=schemas.CompanyRead)
def update_company(company_id: str, payload: schemas.CompanyUpdate, db: Session = Depends(get_db)):
    company = db.get(models.Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="企业不存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(company, key, value)
    db.commit()
    db.refresh(company)
    return company


@router.post("/companies/{company_id}/aliases", response_model=schemas.AliasRead, status_code=201)
def create_alias(company_id: str, payload: schemas.AliasCreate, db: Session = Depends(get_db)):
    if not db.get(models.Company, company_id):
        raise HTTPException(status_code=404, detail="企业不存在")
    alias = models.CompanyAlias(company_id=company_id, **payload.model_dump())
    db.add(alias)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="别名已存在") from exc
    db.refresh(alias)
    return alias


@router.post("/events", response_model=schemas.EventRead, status_code=201)
def create_event(payload: schemas.EventCreate, db: Session = Depends(get_db)):
    if not db.get(models.Company, payload.company_id):
        raise HTTPException(status_code=404, detail="企业不存在")
    event_data = payload.model_dump()
    event_data["source_url"] = str(payload.source_url)
    event = models.Event(**event_data)
    db.add(event)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="疑似重复事件") from exc
    db.refresh(event)
    return event


@router.get("/events", response_model=schemas.EventList)
def list_events(
    company_id: str | None = None,
    event_type: str | None = None,
    verification_status: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    statement = select(models.Event)
    count_statement = select(func.count(models.Event.id))
    for condition in [
        models.Event.company_id == company_id if company_id else None,
        models.Event.event_type == event_type if event_type else None,
        models.Event.verification_status == verification_status if verification_status else None,
    ]:
        if condition is not None:
            statement = statement.where(condition)
            count_statement = count_statement.where(condition)
    items = db.scalars(statement.order_by(models.Event.event_date.desc()).limit(limit)).all()
    return schemas.EventList(items=items, total=db.scalar(count_statement) or 0)


@router.get("/companies/{company_id}/assessments", response_model=list[schemas.AssessmentRead])
def list_assessments(company_id: str, db: Session = Depends(get_db)):
    return db.scalars(
        select(models.OpportunityAssessment)
        .where(models.OpportunityAssessment.company_id == company_id)
        .order_by(models.OpportunityAssessment.assessed_at.desc())
    ).all()


@router.post("/companies/{company_id}/assessments", response_model=schemas.AssessmentRead, status_code=201)
def create_assessment(company_id: str, payload: schemas.AssessmentCreate, db: Session = Depends(get_db)):
    company = db.get(models.Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="企业不存在")
    known_event_ids = set(db.scalars(select(models.Event.id).where(models.Event.company_id == company_id)).all())
    if not set(payload.event_ids).issubset(known_event_ids):
        raise HTTPException(status_code=422, detail="关联事件必须属于当前企业")
    assessment = models.OpportunityAssessment(
        company_id=company_id,
        previous_stage=company.current_stage,
        **payload.model_dump(),
    )
    company.current_stage = payload.stage
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@router.get("/signals", response_model=list[schemas.SignalDefinitionRead])
def list_signals(db: Session = Depends(get_db)):
    return db.scalars(select(models.SignalDefinition).order_by(models.SignalDefinition.code)).all()


@router.get("/opportunities", response_model=list[schemas.CompanyRead])
def opportunity_ranking(limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)):
    stage_order = {models.OpportunityStage.S3: 4, models.OpportunityStage.S2: 3, models.OpportunityStage.S1: 2, models.OpportunityStage.S0: 1}
    companies = db.scalars(select(models.Company).options(selectinload(models.Company.aliases))).unique().all()
    return sorted(companies, key=lambda item: (stage_order[item.current_stage], item.rd_size or 0), reverse=True)[:limit]

