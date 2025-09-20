from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import AsyncSessionLocal
from ..models import User
from ..security import verify_password, create_token, decode_token

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginReq(BaseModel):
    email: str
    password: str

async def get_db():
    async with AsyncSessionLocal() as s:
        yield s

@router.post("/login")
async def login(req: LoginReq, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.email == req.email))).scalar_one_or_none()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    return {"access_token": create_token(str(user.id)), "role": user.role}

def get_current_user(request: Request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "): raise HTTPException(401, "Missing token")
    sub = decode_token(auth[7:])
    return sub

def require_role(role: str):
    def dep(user_id = Depends(get_current_user)):
        # 간단 버전: role 확인 생략하거나 DB 조회로 확장 가능
        return user_id
    return dep
