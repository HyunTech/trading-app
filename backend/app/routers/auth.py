import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import AsyncSessionLocal
from ..models import User
from ..security import verify_password, create_token
from fastapi import APIRouter, HTTPException, Depends, Request
from ..security import verify_password, create_token, decode_token


logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginReq(BaseModel):
    username: str
    password: str

async def get_db():
    async with AsyncSessionLocal() as s:
        yield s

@router.post("/login")
async def login(req: LoginReq, db: AsyncSession = Depends(get_db)):
    try:
        user = (await db.execute(
            select(User).where(User.username == req.username)
        )).scalar_one_or_none()
        if not user or not verify_password(req.password, user.password_hash):
            raise HTTPException(401, "Invalid credentials")
        return {"access_token": create_token(str(user.id)), "role": user.role}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("[/auth/login] unexpected error")
        raise HTTPException(status_code=500, detail="server error")

# 토큰에서 사용자 식별자 꺼내기
def get_current_user(request: Request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Missing token")
    sub = decode_token(auth[7:])  # user_id
    return sub

# 라우트에서 권한 체크에 쓰는 더미 의존성 (필요시 role확장 가능)
def require_role(role: str):
    def dep(user_id: str = Depends(get_current_user)):
        # 여기서 role 검사를 추가로 하고 싶으면 DB조회 후 검사하면 됩니다.
        return user_id
    return dep