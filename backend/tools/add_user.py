import argparse, asyncio
from sqlalchemy import select
from app.db import AsyncSessionLocal
from app.models import User
from passlib.hash import bcrypt

def hash_password(pw: str) -> str:
    return bcrypt.hash(pw)

async def main():
    p = argparse.ArgumentParser()
    p.add_argument("--username", required=True)
    p.add_argument("--password", required=True)
    p.add_argument("--role", default="trader", choices=["admin","trader","viewer"])
    args = p.parse_args()

    async with AsyncSessionLocal() as db:
        exists = (await db.execute(select(User).where(User.username == args.username))).scalar_one_or_none()
        if exists:
            print(f"[X] 이미 존재: {args.username}"); return
        u = User(username=args.username, password_hash=hash_password(args.password), role=args.role)
        db.add(u); await db.commit()
        print(f"[✓] 생성 완료: {args.username} ({args.role})")

if __name__ == "__main__":
    asyncio.run(main())