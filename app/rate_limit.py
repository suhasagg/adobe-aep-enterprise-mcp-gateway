import time
import redis.asyncio as redis
from app.config import settings
r=redis.from_url(settings.redis_url,decode_responses=True)
async def allow(key:str,limit:int=60,window:int=60)->bool:
    bucket=int(time.time()//window)
    k=f"rl:{key}:{bucket}"
    n=await r.incr(k)
    if n==1: await r.expire(k,window+2)
    return n<=limit
