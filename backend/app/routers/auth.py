from sqlalchemy import select
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import AsyncSessionLocal
from ..models import User
from ..security import verify_password, create_token

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