import time,httpx
from app.config import settings

class AdobeTokenProvider:
    def __init__(self): self.token=None; self.expires=0
    async def get(self):
        if self.token and time.time()<self.expires-60: return self.token
        async with httpx.AsyncClient(timeout=15) as c:
            r=await c.post(settings.adobe_ims_token_url,data={
              "grant_type":"client_credentials",
              "client_id":settings.adobe_client_id,
              "client_secret":settings.adobe_client_secret,
              "scope":settings.adobe_scopes})
            r.raise_for_status(); body=r.json()
        self.token=body["access_token"]; self.expires=time.time()+int(body.get("expires_in",3600))
        return self.token

tokens=AdobeTokenProvider()

class AdobeClient:
    async def call(self,method:str,path:str,params:dict):
        token=await tokens.get()
        headers={
          "Authorization":f"Bearer {token}",
          "x-api-key":settings.adobe_client_id,
          "x-gw-ims-org-id":settings.adobe_org_id,
          "x-sandbox-name":settings.adobe_sandbox_name,
          "Content-Type":"application/json"}
        url=settings.adobe_platform_base_url.rstrip("/")+"/"+path.lstrip("/")
        async with httpx.AsyncClient(timeout=30) as c:
            if method.upper()=="GET":
                r=await c.get(url,headers=headers,params=params)
            else:
                r=await c.request(method,url,headers=headers,json=params)
            r.raise_for_status()
            return r.json() if r.content else {}
