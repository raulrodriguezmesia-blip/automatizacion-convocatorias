"""initial multi-tenant schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-07-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tenants table
    op.create_table(
        "tenants",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("subdomain", sa.String(63), nullable=False),
        sa.Column("plan", sa.String(20), nullable=False, server_default="starter"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("config", sa.JSON(), nullable=True),
        sa.Column("schema_name", sa.String(63), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("subdomain", name="uq_tenant_subdomain"),
    )
    op.create_index("idx_tenant_active", "tenants", ["is_active"])

    # Tenant users
    op.create_table(
        "tenant_users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="member"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "email", name="uq_tenant_user_email"),
    )

    # Usage records
    op.create_table(
        "usage_records",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("period_month", sa.String(7), nullable=False),
        sa.Column("metric_type", sa.String(30), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unit_cost", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_usage_tenant_month", "usage_records", ["tenant_id", "period_month"])
    op.create_index("idx_usage_created", "usage_records", ["created_at"])

    # Templates
    op.create_table(
        "templates",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("version", sa.String(10), nullable=False, server_default="1.0.0"),
        sa.Column("author_tenant_id", sa.String(), nullable=True),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("downloads", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rating_avg", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["author_tenant_id"], ["tenants.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_template_category", "templates", ["category"])
    op.create_index("idx_template_published", "templates", ["is_published"])

    # Integrations
    op.create_table(
        "integrations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("config_schema", sa.JSON(), nullable=False),
        sa.Column("auth_type", sa.String(20), nullable=False, server_default="oauth2"),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("installs", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Tenant integrations
    op.create_table(
        "tenant_integrations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("integration_id", sa.String(), nullable=False),
        sa.Column("config", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("installed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ),
        sa.ForeignKeyConstraint(["integration_id"], ["integrations.id"], ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "integration_id", name="uq_tenant_integration"),
    )


def downgrade() -> None:
    op.drop_table("tenant_integrations")
    op.drop_table("integrations")
    op.drop_index("idx_template_published", table_name="templates")
    op.drop_index("idx_template_category", table_name="templates")
    op.drop_table("templates")
    op.drop_index("idx_usage_created", table_name="usage_records")
    op.drop_index("idx_usage_tenant_month", table_name="usage_records")
    op.drop_table("usage_records")
    op.drop_table("tenant_users")
    op.drop_index("idx_tenant_active", table_name="tenants")
    op.drop_table("tenants")