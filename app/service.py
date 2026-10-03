from sqlalchemy import select
from app.models import ToolDefinition,ToolInvocation,Approval,AuditEvent
from app.security import canonical_hash
from app.policy import PolicyEngine
from app.adobe import AdobeClient
from app.rate_limit import allow

class Gateway:
    def __init__(self,db):
        self.db=db; self.policy=PolicyEngine(); self.adobe=AdobeClient()

    async def list_tools(self):
        return (await self.db.execute(select(ToolDefinition).where(ToolDefinition.enabled.is_(True)))).scalars().all()

    async def invoke(self,tool_name,args,idem,identity):
        if not await allow(f"{identity['tenant_id']}:{identity['principal_id']}"):
            raise RuntimeError("RATE_LIMITED")
        tool=(await self.db.execute(select(ToolDefinition).where(
            ToolDefinition.name==tool_name,ToolDefinition.enabled.is_(True)))).scalar_one_or_none()
        if not tool: raise LookupError("tool not found")
        decision=self.policy.evaluate(risk=tool.risk,principal=identity["principal_id"],tenant=identity["tenant_id"])
        if not decision.allowed: raise PermissionError(decision.reason)
        existing=(await self.db.execute(select(ToolInvocation).where(ToolInvocation.idempotency_key==idem))).scalar_one_or_none()
        if existing: return {"status":existing.status,"invocation_id":str(existing.id),"response":existing.response}
        inv=ToolInvocation(tenant_id=identity["tenant_id"],principal_id=identity["principal_id"],
          tool_name=tool.name,idempotency_key=idem,request_hash=canonical_hash(args),
          request=args,status="PENDING_APPROVAL" if decision.approval_required else "STARTED")
        self.db.add(inv); await self.db.flush()
        self.db.add(AuditEvent(tenant_id=identity["tenant_id"],principal_id=identity["principal_id"],
          event_type="TOOL_REQUESTED",data={"invocation_id":str(inv.id),"tool":tool.name}))
        if decision.approval_required:
            self.db.add(Approval(invocation_id=inv.id,action_hash=inv.request_hash))
            await self.db.commit()
            return {"status":"PENDING_APPROVAL","invocation_id":str(inv.id)}
        await self.db.commit()
        try:
            response=await self.adobe.call(tool.method,tool.path,args)
            inv.status="SUCCEEDED"; inv.response=response
        except Exception as exc:
            inv.status="FAILED"; inv.response={"error":type(exc).__name__}
        await self.db.commit()
        return {"status":inv.status,"invocation_id":str(inv.id),"response":inv.response}
