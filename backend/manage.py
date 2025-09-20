# backend/manage.py
import asyncio
import typer
from typing import Optional
from sqlalchemy import select, delete
from app.db import AsyncSessionLocal
from app.models import User
from app.security import hash_password

cli = typer.Typer(help="Trading App User Admin CLI (offline)")

async def _get_user_by(db, email: Optional[str], username: Optional[str]):
    q = select(User)
    if email:
        q = q.where(User.email == email)
    elif username:
        q = q.where(User.username == username)
    else:
        raise typer.BadParameter("Provide --email or --username")
    return (await db.execute(q)).scalar_one_or_none()

@cli.command("list")
def list_users(limit: int = 200, offset: int = 0):
    """모든 사용자 나열"""
    async def run():
        async with AsyncSessionLocal() as db:
            res = await db.execute(select(User).order_by(User.id).limit(limit).offset(offset))
            users = res.scalars().all()
            for u in users:
                print(f"[{u.id}] {u.username:20} {u.email:30} role={u.role}")
    asyncio.run(run())

@cli.command("create")
def create_user(
    username: str,
    email: str,
    password: str,
    role: str = typer.Option("member", help="admin|trader|analyst|viewer|member"),
):
    """사용자 생성"""
    async def run():
        async with AsyncSessionLocal() as db:
            # 중복 체크
            res = await db.execute(select(User).where((User.email == email) | (User.username == username)))
            if res.scalar_one_or_none():
                raise typer.Exit(code=1)
            u = User(
                username=username,
                email=email,
                password_hash=hash_password(password),
                role=role,
            )
            db.add(u)
            await db.commit()
            await db.refresh(u)
            print(f"Created: id={u.id}, email={u.email}, role={u.role}")
    asyncio.run(run())

@cli.command("set-password")
def set_password(
    email: Optional[str] = None,
    username: Optional[str] = None,
    new_password: str = typer.Argument(..., help="새 비밀번호"),
):
    """비밀번호 변경"""
    async def run():
        async with AsyncSessionLocal() as db:
            u = await _get_user_by(db, email, username)
            if not u:
                print("user not found"); return
            u.password_hash = hash_password(new_password)
            await db.commit()
            print(f"Password updated for {u.email or u.username}")
    asyncio.run(run())

@cli.command("set-email")
def set_email(
    current_email: Optional[str] = None,
    username: Optional[str] = None,
    new_email: str = typer.Argument(...),
):
    """이메일 변경"""
    async def run():
        async with AsyncSessionLocal() as db:
            u = await _get_user_by(db, current_email, username)
            if not u:
                print("user not found"); return
            # 중복 체크
            res = await db.execute(select(User).where(User.email == new_email))
            if res.scalar_one_or_none():
                print("email already exists"); return
            u.email = new_email
            await db.commit()
            print(f"Email updated -> {new_email}")
    asyncio.run(run())

@cli.command("set-role")
def set_role(
    email: Optional[str] = None,
    username: Optional[str] = None,
    role: str = typer.Argument(..., help="admin|trader|analyst|viewer|member"),
):
    """권한 변경"""
    async def run():
        async with AsyncSessionLocal() as db:
            u = await _get_user_by(db, email, username)
            if not u:
                print("user not found"); return
            u.role = role
            await db.commit()
            print(f"Role updated -> {role}")
    asyncio.run(run())

@cli.command("delete")
def delete_user(email: Optional[str] = None, username: Optional[str] = None):
    """사용자 삭제"""
    async def run():
        async with AsyncSessionLocal() as db:
            u = await _get_user_by(db, email, username)
            if not u:
                print("user not found"); return
            await db.execute(delete(User).where(User.id == u.id))
            await db.commit()
            print("Deleted")
    asyncio.run(run())

if __name__ == "__main__":
    cli()
