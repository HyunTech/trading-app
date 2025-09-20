# backend/app/routers/auth.py
from fastapi import APIRouter, HTTPException, Depends, Request, Query
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Literal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import AsyncSessionLocal
from ..models import User
from ..security import verify_password, create_token, decode_token, hash_password

router = APIRouter(prefix="/auth", tags=["auth"])

# ---- 공용 ----
ALLOWED_ROLES = {"admin", "trader", "analyst", "viewer", "member"}

class LoginReq(BaseModel):
    email: EmailStr
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

def get_current_user_id(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Missing token")
    return decode_token(auth[7:])  # returns user_id (str)

async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await db.get(User, int(user_id))
    if not user:
        raise HTTPException(401, "Invalid user")
    return user

def require_role(required: str):
    """
    required: 'admin' | 'trader' | 'analyst' | 'viewer' | 'member'
    admin은 모든 권한을 통과.
    """
    if required not in ALLOWED_ROLES:
        raise RuntimeError(f"Unknown role: {required}")
    async def dep(user: User = Depends(get_current_user)):
        if user.role != "admin" and user.role != required:
            raise HTTPException(403, f"{required} role required")
        return user
    return dep

# ---- 유저 관리 스키마 ----
class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Literal["admin","trader","analyst","viewer","member"] = "member"

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[Literal["admin","trader","analyst","viewer","member"]] = None

# ---- 관리자 전용 유저 관리 API ----

@router.get("/users", response_model=List[UserOut])
async def list_users(
    limit: int = 100,
    offset: int = 0,
    _admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    q = await db.execute(select(User).order_by(User.id).limit(limit).offset(offset))
    return q.scalars().all()

@router.post("/users", response_model=UserOut, status_code=201)
async def create_user(
    req: UserCreate,
    _admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    # 중복 체크
    dupe = (await db.execute(select(User).where((User.email == req.email) | (User.username == req.username)))).scalar_one_or_none()
    if dupe:
        raise HTTPException(409, "username or email already exists")

    if req.role not in ALLOWED_ROLES:
        raise HTTPException(400, "invalid role")

    u = User(
        username=req.username,
        email=req.email,
        password_hash=hash_password(req.password),
        role=req.role,
    )
    db.add(u)
    await db.commit()
    await db.refresh(u)
    return u

@router.patch("/users", response_model=UserOut)
async def update_user(
    # 식별자는 email 또는 username 중 하나 제공 (우선 email)
    email: Optional[EmailStr] = Query(default=None),
    username: Optional[str] = Query(default=None),
    req: UserUpdate = None,
    _admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    if not email and not username:
        raise HTTPException(400, "email or username is required to identify the user")

    q = select(User)
    if email:
        q = q.where(User.email == email)
    else:
        q = q.where(User.username == username)

    u = (await db.execute(q)).scalar_one_or_none()
    if not u:
        raise HTTPException(404, "user not found")

    # 변경사항 반영
    if req.username and req.username != u.username:
        # username 중복 체크
        dupe = (await db.execute(select(User).where(User.username == req.username))).scalar_one_or_none()
        if dupe:
            raise HTTPException(409, "username already exists")
        u.username = req.username

    if req.email and req.email != u.email:
        dupe = (await db.execute(select(User).where(User.email == req.email))).scalar_one_or_none()
        if dupe:
            raise HTTPException(409, "email already exists")
        u.email = req.email

    if req.password:
        u.password_hash = hash_password(req.password)

    if req.role:
        if req.role not in ALLOWED_ROLES:
            raise HTTPException(400, "invalid role")
        u.role = req.role

    await db.commit()
    await db.refresh(u)
    return u

@router.delete("/users", status_code=204)
async def delete_user(
    email: Optional[EmailStr] = Query(default=None),
    username: Optional[str] = Query(default=None),
    _admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    if not email and not username:
        raise HTTPException(400, "email or username is required to identify the user")

    q = select(User)
    if email:
        q = q.where(User.email == email)
    else:
        q = q.where(User.username == username)

    u = (await db.execute(q)).scalar_one_or_none()
    if not u:
        raise HTTPException(404, "user not found")

    await db.delete(u)
    await db.commit()
    return
