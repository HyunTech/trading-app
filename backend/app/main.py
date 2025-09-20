from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from .db import AsyncSessionLocal, engine
from .models import Base, User
from .security import hash_password
import logging

logger = logging.getLogger("uvicorn.error")

app = FastAPI(title="Team Trading Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_origin_regex=r"^https://.*\.vercel\.app$",
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

@app.on_event("startup")
async def bootstrap_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 기본 관리자 계정(이메일 필수)
    async with AsyncSessionLocal() as db:
        exist = (await db.execute(select(User).where(User.email == "admin@example.com"))).scalar_one_or_none()
        if not exist:
            admin = User(
                username="admin",
                email="admin@example.com",
                password_hash=hash_password("admin123!"),
                role="admin",
            )
            db.add(admin)
            await db.commit()
            logger.info("seeded admin: admin@example.com / admin123!")

@app.get("/ping")
def ping():
    return {"ok": True}

from .routers import portfolio, orders, auth, metrics
app.include_router(auth.router)
app.include_router(portfolio.router)
app.include_router(orders.router)
app.include_router(metrics.router)
