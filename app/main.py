from fastapi import FastAPI
from app.db import Base,engine,Session
from app.models import ToolDefinition
from app.catalog import TOOLS
from app.mcp import router as mcp_router
from app.admin import router as admin_router
from sqlalchemy import select

app=FastAPI(title="Adobe Experience Platform Enterprise MCP Gateway",version="1.0.0")
app.include_router(mcp_router); app.include_router(admin_router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as c: await c.run_sync(Base.metadata.create_all)
    async with Session() as db:
        for spec in TOOLS:
            if not (await db.execute(select(ToolDefinition).where(ToolDefinition.name==spec["name"]))).scalar_one_or_none():
                db.add(ToolDefinition(**spec))
        await db.commit()

@app.get("/health")
async def health(): return {"status":"ok"}
