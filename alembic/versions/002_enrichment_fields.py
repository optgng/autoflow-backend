"""Add enrichment fields to transactions, contact_profiles, user_enrichment_rules, user_keys.

Revision ID: 002_enrichment
Revises: 001_initial
Create Date: 2026-03-23
"""
from alembic import op
import sqlalchemy as sa

revision = "002_enrichment"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enrichment columns on transactions
    op.add_column("transactions", sa.Column("enriched_category", sa.String(100), nullable=True), schema="finances")
    op.add_column("transactions", sa.Column("enriched_subcategory", sa.String(100), nullable=True), schema="finances")
    op.add_column("transactions", sa.Column("enriched_type", sa.String(50), nullable=True), schema="finances")
    op.add_column("transactions", sa.Column("income_type", sa.String(50), nullable=True), schema="finances")
    op.add_column("transactions", sa.Column("expense_type", sa.String(50), nullable=True), schema="finances")
    op.add_column("transactions", sa.Column("exclude_from_metrics", sa.Boolean(), nullable=False, server_default="false"), schema="finances")
    op.add_column("transactions", sa.Column("is_group_payment", sa.Boolean(), nullable=False, server_default="false"), schema="finances")
    op.add_column("transactions", sa.Column("net_amount", sa.Numeric(12, 2), nullable=True), schema="finances")
    op.add_column("transactions", sa.Column("linked_tx_id", sa.Integer(), sa.ForeignKey("finances.transactions.id"), nullable=True), schema="finances")
    op.add_column("transactions", sa.Column("enrichment_source", sa.String(20), nullable=True), schema="finances")
    op.add_column("transactions", sa.Column("enrichment_confidence", sa.Numeric(3, 2), nullable=True), schema="finances")
    op.add_column("transactions", sa.Column("review_status", sa.String(20), nullable=False, server_default="auto"), schema="finances")
    op.add_column("transactions", sa.Column("user_rule_id", sa.Integer(), nullable=True), schema="finances")
    op.add_column("transactions", sa.Column("enriched_at", sa.DateTime(timezone=True), nullable=True), schema="finances")
    op.add_column("transactions", sa.Column("contact_ref", sa.String(24), nullable=True), schema="finances")
    op.create_index("idx_transactions_review_status", "transactions", ["review_status"], schema="finances")
    op.create_index("idx_transactions_contact_ref", "transactions", ["contact_ref"], schema="finances")
    op.create_foreign_key(None, 'accounts', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'budgets', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'budgets', 'categories', ['category_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'categories', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'telegram_link_tokens', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'transactions', 'categories', ['category_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='SET NULL')
    op.create_foreign_key(None, 'transactions', 'accounts', ['account_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'transactions', 'users', ['user_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='CASCADE')
    op.create_foreign_key(None, 'transactions', 'accounts', ['target_account_id'], ['id'], source_schema='finances', referent_schema='finances', ondelete='SET NULL')
    op.create_index(op.f('ix_finances_transactions_external_id'), 'transactions', ['external_id'], unique=True, schema='finances')
    op.create_index(op.f('ix_finances_transactions_id'), 'transactions', ['id'], unique=False, schema='finances')

    # contact_profiles
    op.create_table(
        "contact_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("contact_ref", sa.String(24), nullable=False),
        sa.Column("relation_type", sa.String(30), nullable=False, server_default="unknown"),
        sa.Column("typical_amount_min", sa.Numeric(10, 2), nullable=True),
        sa.Column("typical_amount_max", sa.Numeric(10, 2), nullable=True),
        sa.Column("avg_frequency_days", sa.Integer(), nullable=True),
        sa.Column("last_seen_at", sa.Date(), nullable=True),
        sa.Column("tx_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("user_label", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.UniqueConstraint("telegram_id", "contact_ref", name="uq_contact_per_user"),
        schema="finances",
    )

    # user_enrichment_rules
    op.create_table(
        "user_enrichment_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("rule_type", sa.String(50), nullable=False),
        sa.Column("match_pattern", sa.String(200), nullable=False),
        sa.Column("action_json", sa.JSON(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        schema="finances",
    )

    # user_keys — isolated salt storage
    op.create_table(
        "user_keys",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False, unique=True, index=True),
        sa.Column("salt", sa.String(64), nullable=False),  # hex-encoded 32-byte salt
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="finances",
    )


def downgrade() -> None:
    op.drop_table("user_keys", schema="finances")
    op.drop_table("user_enrichment_rules", schema="finances")
    op.drop_table("contact_profiles", schema="finances")
    op.drop_index("idx_transactions_contact_ref", "transactions", schema="finances")
    op.drop_index("idx_transactions_review_status", "transactions", schema="finances")
    for col in [
        "contact_ref", "enriched_at", "user_rule_id", "review_status",
        "enrichment_confidence", "enrichment_source", "linked_tx_id",
        "net_amount", "is_group_payment", "exclude_from_metrics",
        "expense_type", "income_type", "enriched_type",
        "enriched_subcategory", "enriched_category",
    ]:
        op.drop_column("transactions", col, schema="finances")
