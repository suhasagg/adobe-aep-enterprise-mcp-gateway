from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from app.db import Session
from app.models import Approval,ToolInvocation,AuditEvent
from app.security import authenticate
from app.adobe import AdobeClient

router=APIRouter(prefix="/v1")

@router.post("/approvals/{approval_id}/approve")
async def approve(approval_id:UUID,identity=Depends(authenticate)):
    async with Session() as db:
        a=(await db.execute(select(Approval).where(Approval.id==approval_id).with_for_update())).scalar_one_or_none()
        if not a: raise HTTPException(404,"approval not found")
        if a.status!="PENDING": raise HTTPException(409,"approval already resolved")
        inv=(await db.execute(select(ToolInvocation).where(ToolInvocation.id==a.invocation_id))).scalar_one()
        if inv.request_hash!=a.action_hash: raise HTTPException(409,"approved action hash mismatch")
        a.status="APPROVED"; a.approver=identity["principal_id"]; inv.status="STARTED"
        await db.commit()
        # In production enqueue execution after approval rather than holding request open.
        from app.models import ToolDefinition
        tool=(await db.execute(select(ToolDefinition).where(ToolDefinition.name==inv.tool_name))).scalar_one()
        try:
            inv.response=await AdobeClient().call(tool.method,tool.path,inv.request); inv.status="SUCCEEDED"
        except Exception as exc:
            inv.response={"error":type(exc).__name__}; inv.status="FAILED"
        db.add(AuditEvent(tenant_id=inv.tenant_id,principal_id=identity["principal_id"],
          event_type="APPROVAL_EXECUTED",data={"invocation_id":str(inv.id)}))
        await db.commit()
        return {"invocation_id":str(inv.id),"status":inv.status}
