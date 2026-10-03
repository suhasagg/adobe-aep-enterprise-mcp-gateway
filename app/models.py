import uuid
from datetime import datetime
from sqlalchemy import String,DateTime,Text,Boolean,UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID,JSONB
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy.sql import func
from app.db import Base
def uid(): return uuid.uuid4()

class ToolDefinition(Base):
    __tablename__="tool_definitions"
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid)
    name:Mapped[str]=mapped_column(String(160),unique=True,index=True)
    product:Mapped[str]=mapped_column(String(32),index=True)
    description:Mapped[str]=mapped_column(Text)
    method:Mapped[str]=mapped_column(String(12))
    path:Mapped[str]=mapped_column(String(512))
    input_schema:Mapped[dict]=mapped_column(JSONB,default=dict)
    risk:Mapped[str]=mapped_column(String(16),default="READ")
    enabled:Mapped[bool]=mapped_column(Boolean,default=True)

class ToolInvocation(Base):
    __tablename__="tool_invocations"
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid)
    tenant_id:Mapped[str]=mapped_column(String(128),index=True)
    principal_id:Mapped[str]=mapped_column(String(128),index=True)
    tool_name:Mapped[str]=mapped_column(String(160),index=True)
    idempotency_key:Mapped[str]=mapped_column(String(256),unique=True)
    request_hash:Mapped[str]=mapped_column(String(64))
    status:Mapped[str]=mapped_column(String(32),index=True)
    request:Mapped[dict]=mapped_column(JSONB)
    response:Mapped[dict|None]=mapped_column(JSONB,nullable=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())

class Approval(Base):
    __tablename__="approvals"
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid)
    invocation_id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),index=True)
    action_hash:Mapped[str]=mapped_column(String(64))
    status:Mapped[str]=mapped_column(String(24),default="PENDING")
    approver:Mapped[str|None]=mapped_column(String(128),nullable=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())

class AuditEvent(Base):
    __tablename__="audit_events"
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid)
    tenant_id:Mapped[str]=mapped_column(String(128),index=True)
    principal_id:Mapped[str]=mapped_column(String(128))
    event_type:Mapped[str]=mapped_column(String(96),index=True)
    data:Mapped[dict]=mapped_column(JSONB,default=dict)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
