import asyncio
from app.db import engine, Base, AsyncSessionLocal
from app.models import User
from app.security import hash_password

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as s:
        # 이미 있으면 건너뛰기
        existing = (await s.execute(__import__("sqlalchemy").select(User))).scalars().first()
        if not existing:
            s.add(User(email="admin@team.com", password_hash=hash_password("admin123"), role="admin"))
            await s.commit()

if __name__ == "__main__":
    asyncio.run(init())
