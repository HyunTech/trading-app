import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from .db import AsyncSessionLocal, engine
from .models import Base, User
from .security import hash_password

logger = logging.getLogger("uvicorn.error")  # Render에서 보이는 로거

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
        logger.info("[bootstrap] create_all done")

        cols = [row[1] for row in (await conn.execute(text("PRAGMA table_info(users)")))]
        logger.info("[bootstrap] users columns: %s", cols)
        if "username" not in cols:
            await conn.execute(text("ALTER TABLE users ADD COLUMN username TEXT"))
            await conn.execute(text("UPDATE users SET username = COALESCE(username, email)"))
            await conn.execute(text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users(username)"
            ))
            logger.info("[bootstrap] username column added & indexed")

    async with AsyncSessionLocal() as db:
        exists = (await db.execute(select(User).limit(1))).scalar_one_or_none()
        if not exists:
            admin = User(username="admin", password_hash=hash_password("admin123!"), role="admin")
            db.add(admin)
            await db.commit()
            logger.info("[bootstrap] default admin created: admin / admin123!")

@app.get("/ping")
def ping():
    return {"ok": True}

# 임시 디버그: 현재 DB 컬럼과 유저 수 확인
@app.get("/debug/db")
async def debug_db():
    async with engine.begin() as conn:
        cols = [row[1] for row in (await conn.execute(text("PRAGMA table_info(users)")))]
    async with AsyncSessionLocal() as db:
        total = (await db.execute(text("SELECT COUNT(*) FROM users"))).scalar()
    return {"users_columns": cols, "users_total": total}

from .routers import portfolio, orders, auth, metrics
app.include_router(auth.router)
app.include_router(portfolio.router)
app.include_router(orders.router)
app.include_router(metrics.router)
