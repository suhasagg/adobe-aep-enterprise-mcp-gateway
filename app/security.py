import hashlib,hmac,json
from fastapi import Header,HTTPException
from app.config import settings

async def authenticate(x_gateway_api_key:str=Header(...),x_principal_id:str=Header(...),
                       x_tenant_id:str=Header(...)):
    if not hmac.compare_digest(x_gateway_api_key,settings.gateway_api_key):
        raise HTTPException(401,"invalid gateway credential")
    return {"principal_id":x_principal_id,"tenant_id":x_tenant_id}

def canonical_hash(v:dict)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
