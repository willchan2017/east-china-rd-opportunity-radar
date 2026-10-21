import enum
import uuid
from datetime import date, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def uuid4_str() -> str:
    return str(uuid.uuid4())


class OpportunityStage(str, enum.Enum):
    S0 = "S0"
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"


class SignalCategory(str, enum.Enum):
    B = "B"
    R = "R"
    P = "P"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Company(Base, TimestampMixin):
    __tablename__ = "companies"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    unified_social_credit_code: Mapped[str | None] = mapped_column(String(32), unique=True)
    industry: Mapped[str] = mapped_column(String(100), index=True)
    province: Mapped[str] = mapped_column(String(32), index=True)
    city: Mapped[str | None] = mapped_column(String(64))
    website: Mapped[str | None] = mapped_column(String(500))
    rd_size: Mapped[int | None] = mapped_column(Integer)
    icp_tier: Mapped[str] = mapped_column(String(16), default="待评估", index=True)
    crm_status: Mapped[str] = mapped_column(String(32), default="未建档", index=True)
    sales_owner: Mapped[str | None] = mapped_column(String(100), index=True)
    current_stage: Mapped[OpportunityStage] = mapped_column(
        Enum(OpportunityStage, native_enum=False), default=OpportunityStage.S0, index=True
    )
    is_sample: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    aliases: Mapped[list["CompanyAlias"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )
    events: Mapped[list["Event"]] = relationship(back_populates="company", cascade="all, delete-orphan")


class CompanyAlias(Base, TimestampMixin):
    __tablename__ = "company_aliases"
    __table_args__ = (UniqueConstraint("company_id", "alias", name="uq_company_alias"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    alias: Mapped[str] = mapped_column(String(255), index=True)
    alias_type: Mapped[str] = mapped_column(String(32), default="简称")
    company: Mapped[Company] = relationship(back_populates="aliases")


class CompanyRelationship(Base, TimestampMixin):
    __tablename__ = "company_relationships"
    __table_args__ = (
        UniqueConstraint("source_company_id", "target_company_id", "relationship_type", name="uq_relationship"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    source_company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    target_company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    relationship_type: Mapped[str] = mapped_column(String(64))
    notes: Mapped[str | None] = mapped_column(Text)


class Source(Base, TimestampMixin):
    __tablename__ = "sources"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    source_type: Mapped[str] = mapped_column(String(32), index=True)
    base_url: Mapped[str | None] = mapped_column(String(500))
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class Event(Base, TimestampMixin):
    __tablename__ = "events"
    __table_args__ = (
        UniqueConstraint("company_id", "source_url", "event_title", name="uq_event_natural_key"),
        Index("ix_events_company_date", "company_id", "event_date"),
        Index("ix_events_type_date", "event_type", "event_date"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    source_id: Mapped[str | None] = mapped_column(ForeignKey("sources.id", ondelete="SET NULL"))
    event_date: Mapped[date] = mapped_column(Date, index=True)
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    event_title: Mapped[str] = mapped_column(String(500))
    event_description: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str] = mapped_column(String(1000))
    source_type: Mapped[str] = mapped_column(String(32), index=True)
    evidence_excerpt: Mapped[str] = mapped_column(Text)
    raw_evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    confidence_level: Mapped[str] = mapped_column(String(16), default="medium")
    verification_status: Mapped[str] = mapped_column(String(32), default="待核验", index=True)
    duplicate_group_id: Mapped[str | None] = mapped_column(String(36), index=True)
    is_sample: Mapped[bool] = mapped_column(Boolean, default=False)
    company: Mapped[Company] = relationship(back_populates="events")
    signals: Mapped[list["EventSignal"]] = relationship(cascade="all, delete-orphan")


class SignalDefinition(Base, TimestampMixin):
    __tablename__ = "signal_definitions"
    __table_args__ = (UniqueConstraint("code", "version", name="uq_signal_version"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    code: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(255))
    category: Mapped[SignalCategory] = mapped_column(Enum(SignalCategory, native_enum=False), index=True)
    description: Mapped[str] = mapped_column(Text)
    rule_config: Mapped[dict] = mapped_column(JSON, default=dict)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    version: Mapped[int] = mapped_column(Integer, default=1)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class EventSignal(Base, TimestampMixin):
    __tablename__ = "event_signals"
    __table_args__ = (UniqueConstraint("event_id", "signal_definition_id", name="uq_event_signal"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    event_id: Mapped[str] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), index=True)
    signal_definition_id: Mapped[str] = mapped_column(
        ForeignKey("signal_definitions.id", ondelete="CASCADE"), index=True
    )
    matched_evidence: Mapped[str] = mapped_column(Text)
    match_method: Mapped[str] = mapped_column(String(32), default="rule")
    confidence: Mapped[float | None] = mapped_column(Float)


class OpportunityAssessment(Base, TimestampMixin):
    __tablename__ = "opportunity_assessments"
    __table_args__ = (Index("ix_assessments_company_time", "company_id", "assessed_at"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    assessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    previous_stage: Mapped[OpportunityStage | None] = mapped_column(Enum(OpportunityStage, native_enum=False))
    stage: Mapped[OpportunityStage] = mapped_column(Enum(OpportunityStage, native_enum=False), index=True)
    rationale: Mapped[str] = mapped_column(Text)
    event_ids: Mapped[list] = mapped_column(JSON, default=list)
    assessor_type: Mapped[str] = mapped_column(String(32), default="manual")
    assessor_name: Mapped[str | None] = mapped_column(String(100))


class CollectionJob(Base, TimestampMixin):
    __tablename__ = "collection_jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    source_id: Mapped[str | None] = mapped_column(ForeignKey("sources.id", ondelete="SET NULL"), index=True)
    job_type: Mapped[str] = mapped_column(String(32), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    stats: Mapped[dict] = mapped_column(JSON, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text)


class SalesFeedback(Base, TimestampMixin):
    __tablename__ = "sales_feedback"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    event_id: Mapped[str | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"), index=True)
    feedback_type: Mapped[str] = mapped_column(String(32), index=True)
    content: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String(100))

