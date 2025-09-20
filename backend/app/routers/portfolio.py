from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

# 임시 스텁: 프론트 연결을 위한 더미 데이터
DUMMY = {
    "kr": {"cash": 10000000, "equity": 10250000,
           "positions": [{"code":"005930","name":"삼성전자","qty":10,"avg":70000,"pl":25000}]},
    "us": {"cash": 5000, "equity": 5250,
           "positions": [{"ticker":"AAPL","name":"Apple","qty":2,"avg":180.0,"pl":50.0}]}
}

@router.get("/balances")
def get_balances(market: str):
    market = market.lower()
    if market not in DUMMY:
        raise HTTPException(400, "market must be 'kr' or 'us'")
    return DUMMY[market]
