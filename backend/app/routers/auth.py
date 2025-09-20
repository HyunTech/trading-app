from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import AsyncSessionLocal
from ..models import User
from ..security import verify_password, create_token, decode_token

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginReq(BaseModel):
    username: str
    password: str

async def get_db():
    async with AsyncSessionLocal() as s:
        yield s

@router.post("/login")
async def login(req: LoginReq, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.username == req.username))).scalar_one_or_none()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    return {"access_token": create_token(str(user.id)), "role": user.role}

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Missing token")
    user_id = decode_token(auth[7:])
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(401, "User not found")
    return user

def require_role(required: str):
    levels = {"viewer":0,"trader":1,"admin":2}
    def dep(user: User = Depends(get_current_user)):
        if levels[user.role] < levels[required]:
            raise HTTPException(403, "Forbidden")
        return user
    return dep