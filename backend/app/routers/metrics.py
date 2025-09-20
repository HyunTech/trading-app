from fastapi import APIRouter, Depends
from .auth import require_role

router = APIRouter(prefix="/metrics", tags=["metrics"])

# 간단 더미: 누적 손익, 월간 손익, 벤치마크 대비, 최근 10일 곡선
@router.get("/team-performance")
def team_performance(_user=Depends(require_role("viewer"))):
    return {
        "since": "2025-01-01",
        "cum_pnl": 12500000,         # 누적 손익(원)
        "mtd_pnl": 850000,           # 이달 손익(원)
        "win_rate": 0.58,            # 승률
        "avg_rr": 1.35,              # 평균 손익비
        "benchmark": {"name":"KOSPI", "ytd": 0.072},  # 연초대비 벤치마크
        "team_ytd": 0.106,           # 팀 연초대비 수익률
        "curve": [                    # 최근 10영업일 곡선 (일자/일손익)
            {"d":"2025-09-05","pnl":120000},
            {"d":"2025-09-08","pnl":-50000},
            {"d":"2025-09-09","pnl":240000},
            {"d":"2025-09-10","pnl":-30000},
            {"d":"2025-09-11","pnl":90000},
            {"d":"2025-09-12","pnl":110000},
            {"d":"2025-09-15","pnl":-20000},
            {"d":"2025-09-16","pnl":70000},
            {"d":"2025-09-17","pnl":-10000},
            {"d":"2025-09-18","pnl":160000},
        ],
    }
