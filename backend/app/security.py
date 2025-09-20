from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

SECRET_KEY = "change-this-in-.env"
ACCESS_TOKEN_MINUTES = 12*60
ALGO = "HS256"
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(pw: str) -> str:
    return pwd_ctx.hash(pw)

def verify_password(pw: str, hashed: str) -> bool:
    return pwd_ctx.verify(pw, hashed)

def create_token(sub: str):
    exp = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    return jwt.encode({"sub": sub, "exp": exp}, SECRET_KEY, algorithm=ALGO)

def decode_token(tok: str) -> str:
    return jwt.decode(tok, SECRET_KEY, algorithms=[ALGO])["sub"]
