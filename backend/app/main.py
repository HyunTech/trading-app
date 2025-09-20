from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import portfolio, orders, auth, metrics  # 네 라우터 임포트

app = FastAPI(title="Team Trading Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
def ping():
    return {"ok": True}

app.include_router(auth.router)
app.include_router(portfolio.router)
app.include_router(orders.router)
app.include_router(metrics.router)