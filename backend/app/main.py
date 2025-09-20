from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import portfolio, orders, auth, metrics

app = FastAPI(title="Team Trading Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

@app.get("/ping")
def ping(): return {"ok": True}

app.include_router(auth.router)
app.include_router(portfolio.router)
app.include_router(orders.router)
app.include_router(metrics.router)
