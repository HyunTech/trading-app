from sqlalchemy import Column, Integer, String
from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)  # 팀원이 원하면 계속 보유
    email = Column(String, unique=True, nullable=False)     # 이메일은 필수
    password_hash = Column(String, nullable=False)
    role = Column(String, default="member")
