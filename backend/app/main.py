# backend/app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from .routers import portfolio, orders, auth, metrics
from .db import AsyncSessionLocal, engine
from .models import Base, User          # ★ Base 추가 (create_all 에 필요)
from .security import hash_password      # 기본 계정 생성에 사용

app = FastAPI(title="Team Trading Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_origin_regex=r"^https://.*\.vercel\.app$",
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

@app.on_event("startup")
async def bootstrap_db():
    # 1) 모든 테이블 생성 (없으면 생성, 있으면 유지)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # 2) users.username 컬럼 보정 (없으면 추가 + 인덱스 + 데이터 채우기)
        cols = [row[1] for row in (await conn.execute(text("PRAGMA table_info(users)")))]
        if "username" not in cols:
            await conn.execute(text("ALTER TABLE users ADD COLUMN username TEXT"))
            await conn.execute(text("UPDATE users SET username = COALESCE(username, email)"))
            await conn.execute(text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users(username)"
            ))

    # 3) 기본 관리자 계정이 하나도 없으면 생성
    async with AsyncSessionLocal() as db:  # type: AsyncSession
        exists = (await db.execute(select(User).limit(1))).scalar_one_or_none()
        if not exists:
            admin = User(username="admin", password_hash=hash_password("admin123!"), role="admin")
            db.add(admin)
            await db.commit()
            print("[bootstrap] default admin created: admin / admin123!")

@app.get("/ping")
def ping():
    return {"ok": True}

app.include_router(auth.router)
app.include_router(portfolio.router)
app.include_router(orders.router)
app.include_router(metrics.router)
