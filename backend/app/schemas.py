from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from app.models import OpportunityStage, SignalCategory


class AliasCreate(BaseModel):
    alias: str = Field(min_length=1, max_length=255)
    alias_type: str = Field(default="简称", max_length=32)


class AliasRead(AliasCreate):
    id: str
    model_config = ConfigDict(from_attributes=True)


class CompanyBase(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    unified_social_credit_code: str | None = Field(default=None, max_length=32)
    industry: str = Field(min_length=1, max_length=100)
    province: str = Field(min_length=1, max_length=32)
    city: str | None = Field(default=None, max_length=64)
    website: str | None = Field(default=None, max_length=500)
    rd_size: int | None = Field(default=None, ge=0)
    icp_tier: str = Field(default="待评估", max_length=16)
    crm_status: str = Field(default="未建档", max_length=32)
    sales_owner: str | None = Field(default=None, max_length=100)


class CompanyCreate(CompanyBase):
    aliases: list[AliasCreate] = []


class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    industry: str | None = Field(default=None, min_length=1, max_length=100)
    province: str | None = Field(default=None, min_length=1, max_length=32)
    city: str | None = None
    website: str | None = None
    rd_size: int | None = Field(default=None, ge=0)
    icp_tier: str | None = None
    crm_status: str | None = None
    sales_owner: str | None = None


class CompanyRead(CompanyBase):
    id: str
    current_stage: OpportunityStage
    is_sample: bool
    aliases: list[AliasRead] = []
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CompanyList(BaseModel):
    items: list[CompanyRead]
    total: int
    page: int
    page_size: int


class EventBase(BaseModel):
    company_id: str
    event_date: date
    event_type: str = Field(min_length=1, max_length=64)
    event_title: str = Field(min_length=2, max_length=500)
    event_description: str = Field(min_length=1)
    source_url: HttpUrl
    source_type: str = Field(min_length=1, max_length=32)
    evidence_excerpt: str = Field(min_length=1)
    confidence_level: Literal["low", "medium", "high"] = "medium"
    verification_status: str = Field(default="待核验", max_length=32)
    duplicate_group_id: str | None = None


class EventCreate(EventBase):
    raw_evidence: dict = {}
    is_sample: bool = False


class EventRead(BaseModel):
    id: str
    company_id: str
    event_date: date
    discovered_at: datetime
    event_type: str
    event_title: str
    event_description: str
    source_url: str
    source_type: str
    evidence_excerpt: str
    confidence_level: str
    verification_status: str
    duplicate_group_id: str | None
    is_sample: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class EventList(BaseModel):
    items: list[EventRead]
    total: int


class AssessmentCreate(BaseModel):
    stage: OpportunityStage
    rationale: str = Field(min_length=5)
    event_ids: list[str] = []
    assessor_type: Literal["manual", "rule", "ai_assisted"] = "manual"
    assessor_name: str | None = None


class AssessmentRead(AssessmentCreate):
    id: str
    company_id: str
    previous_stage: OpportunityStage | None
    assessed_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SignalDefinitionRead(BaseModel):
    id: str
    code: str
    name: str
    category: SignalCategory
    description: str
    rule_config: dict
    weight: float
    version: int
    enabled: bool
    model_config = ConfigDict(from_attributes=True)


class DashboardSummary(BaseModel):
    company_count: int
    event_count: int
    verified_event_count: int
    stage_counts: dict[str, int]
    province_counts: dict[str, int]
    sample_data: bool


class AIEventExtraction(BaseModel):
    """M1 validation contract only; provider integration is scheduled for M2."""

    company_name: str | None
    event_date: date | None
    event_type: str | None
    event_title: str | None
    event_description: str | None
    evidence_excerpt: str | None
    source_url: HttpUrl
    business_impact: str | None
    purchase_relevance: str | None
    confidence_level: Literal["low", "medium", "high"]
    insufficient_evidence: bool = False

    @model_validator(mode="after")
    def require_evidence_for_facts(self):
        factual_fields = [self.company_name, self.event_title, self.event_description]
        if any(factual_fields) and not self.evidence_excerpt:
            raise ValueError("存在企业事实时必须提供原文证据")
        return self


class ImportResult(BaseModel):
    created: int
    skipped: int
    errors: list[str]

