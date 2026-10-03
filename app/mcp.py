from typing import Any
from fastapi import APIRouter,Depends,Header,HTTPException
from pydantic import BaseModel
from app.db import Session
from app.security import authenticate
from app.service import Gateway

router=APIRouter()

class RPC(BaseModel):
    jsonrpc:str="2.0"
    id:str|int|None=None
    method:str
    params:dict[str,Any]={}

@router.post("/mcp")
async def mcp(req:RPC,identity=Depends(authenticate),x_idempotency_key:str|None=Header(None)):
    async with Session() as db:
        g=Gateway(db)
        if req.method=="initialize":
            result={"protocolVersion":"2025-06-18","capabilities":{"tools":{}},"serverInfo":{"name":"aep-enterprise-gateway","version":"1.0.0"}}
        elif req.method=="tools/list":
            tools=await g.list_tools()
            result={"tools":[{"name":t.name,"description":t.description,"inputSchema":t.input_schema} for t in tools]}
        elif req.method=="tools/call":
            try:
                idem=x_idempotency_key or req.params.get("idempotencyKey")
                if not idem: raise HTTPException(400,"idempotency key required")
                out=await g.invoke(req.params["name"],req.params.get("arguments",{}),idem,identity)
                result={"content":[{"type":"text","text":str(out)}],"structuredContent":out}
            except LookupError as e: raise HTTPException(404,str(e))
            except PermissionError as e: raise HTTPException(403,str(e))
            except RuntimeError as e: raise HTTPException(429,str(e))
        else:
            return {"jsonrpc":"2.0","id":req.id,"error":{"code":-32601,"message":"method not found"}}
        return {"jsonrpc":"2.0","id":req.id,"result":result}
