"""initial M1 schema

Revision ID: 0001_initial
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("companies",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("unified_social_credit_code", sa.String(32)),
        sa.Column("industry", sa.String(100), nullable=False),
        sa.Column("province", sa.String(32), nullable=False),
        sa.Column("city", sa.String(64)), sa.Column("website", sa.String(500)),
        sa.Column("rd_size", sa.Integer()), sa.Column("icp_tier", sa.String(16), nullable=False),
        sa.Column("crm_status", sa.String(32), nullable=False), sa.Column("sales_owner", sa.String(100)),
        sa.Column("current_stage", sa.String(2), nullable=False), sa.Column("is_sample", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("name"), sa.UniqueConstraint("unified_social_credit_code"))
    for column in ["name", "industry", "province", "icp_tier", "crm_status", "sales_owner", "current_stage", "is_sample"]:
        op.create_index(f"ix_companies_{column}", "companies", [column])
    op.create_table("company_aliases",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("company_id", sa.String(36), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("alias", sa.String(255), nullable=False), sa.Column("alias_type", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("company_id", "alias", name="uq_company_alias"))
    op.create_index("ix_company_aliases_company_id", "company_aliases", ["company_id"]); op.create_index("ix_company_aliases_alias", "company_aliases", ["alias"])
    op.create_table("company_relationships",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("source_company_id", sa.String(36), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_company_id", sa.String(36), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False), sa.Column("relationship_type", sa.String(64), nullable=False), sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("source_company_id", "target_company_id", "relationship_type", name="uq_relationship"))
    op.create_table("sources",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("name", sa.String(255), unique=True, nullable=False), sa.Column("source_type", sa.String(32), nullable=False),
        sa.Column("base_url", sa.String(500)), sa.Column("config", sa.JSON(), nullable=False), sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("events",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("company_id", sa.String(36), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_id", sa.String(36), sa.ForeignKey("sources.id", ondelete="SET NULL")), sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("discovered_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("event_title", sa.String(500), nullable=False), sa.Column("event_description", sa.Text(), nullable=False), sa.Column("source_url", sa.String(1000), nullable=False),
        sa.Column("source_type", sa.String(32), nullable=False), sa.Column("evidence_excerpt", sa.Text(), nullable=False), sa.Column("raw_evidence", sa.JSON(), nullable=False),
        sa.Column("confidence_level", sa.String(16), nullable=False), sa.Column("verification_status", sa.String(32), nullable=False),
        sa.Column("duplicate_group_id", sa.String(36)), sa.Column("is_sample", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("company_id", "source_url", "event_title", name="uq_event_natural_key"))
    op.create_index("ix_events_company_date", "events", ["company_id", "event_date"]); op.create_index("ix_events_type_date", "events", ["event_type", "event_date"])
    for c in ["company_id", "event_date", "discovered_at", "event_type", "source_type", "verification_status", "duplicate_group_id"]: op.create_index(f"ix_events_{c}", "events", [c])
    op.create_table("signal_definitions",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("code", sa.String(32), nullable=False), sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(1), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("rule_config", sa.JSON(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False), sa.Column("version", sa.Integer(), nullable=False), sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("code", "version", name="uq_signal_version"))
    op.create_index("ix_signal_definitions_code", "signal_definitions", ["code"]); op.create_index("ix_signal_definitions_category", "signal_definitions", ["category"])
    op.create_table("event_signals",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("event_id", sa.String(36), sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("signal_definition_id", sa.String(36), sa.ForeignKey("signal_definitions.id", ondelete="CASCADE"), nullable=False), sa.Column("matched_evidence", sa.Text(), nullable=False),
        sa.Column("match_method", sa.String(32), nullable=False), sa.Column("confidence", sa.Float()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("event_id", "signal_definition_id", name="uq_event_signal"))
    op.create_table("opportunity_assessments",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("company_id", sa.String(36), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("assessed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("previous_stage", sa.String(2)), sa.Column("stage", sa.String(2), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False), sa.Column("event_ids", sa.JSON(), nullable=False), sa.Column("assessor_type", sa.String(32), nullable=False), sa.Column("assessor_name", sa.String(100)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_assessments_company_time", "opportunity_assessments", ["company_id", "assessed_at"])
    op.create_table("collection_jobs",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("source_id", sa.String(36), sa.ForeignKey("sources.id", ondelete="SET NULL")),
        sa.Column("job_type", sa.String(32), nullable=False), sa.Column("status", sa.String(32), nullable=False), sa.Column("started_at", sa.DateTime(timezone=True)), sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("retry_count", sa.Integer(), nullable=False), sa.Column("stats", sa.JSON(), nullable=False), sa.Column("error_message", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("sales_feedback",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("company_id", sa.String(36), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_id", sa.String(36), sa.ForeignKey("events.id", ondelete="SET NULL")), sa.Column("feedback_type", sa.String(32), nullable=False), sa.Column("content", sa.Text(), nullable=False), sa.Column("author", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))


def downgrade() -> None:
    for table in ["sales_feedback", "collection_jobs", "opportunity_assessments", "event_signals", "signal_definitions", "events", "sources", "company_relationships", "company_aliases", "companies"]:
        op.drop_table(table)

