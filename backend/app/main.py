from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .routers import portfolio, orders, auth, metrics

app = FastAPI(title="Team Trading Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",            # ← 로컬 프론트
    ],
    allow_origin_regex=r"^https://.*\.vercel\.app$",  # ← 모든 vercel 배포 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
def ping():
    return {"ok": True}

# (임시 디버그: 현재 요청의 Origin 확인용 — 필요 없으면 지워도 됨)
@app.get("/debug/origin")
def debug_origin(request: Request):
    return {
        "origin": request.headers.get("origin"),
        "host": request.headers.get("host"),
    }

app.include_router(auth.router)
app.include_router(portfolio.router)
app.include_router(orders.router)
app.include_router(metrics.router)
