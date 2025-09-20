from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import time
from .auth import require_role
from ..state import STORE

router = APIRouter(prefix="/orders", tags=["orders"])

class OrderReq(BaseModel):
    market: str = Field(pattern="^(kr|us)$")
    symbol: str
    side: str = Field(pattern="^(buy|sell)$")
    qty: int = Field(gt=0)
    price: float | None = None
    order_type: str = Field(default="limit", pattern="^(limit|market)$")

class ModifyReq(BaseModel):
    price: float | None = None
    qty: int | None = None

@router.post("")
def place_order(req: OrderReq, _user=Depends(require_role("trader"))):
    if req.order_type == "limit" and req.price is None:
        raise HTTPException(400, "limit 주문은 price 필수")
    oid = f"SIM-{int(time.time()*1000)}"
    data = {"order_id": oid, "status": "accepted", **req.model_dump(), "created_at": int(time.time()*1000)}
    STORE.add(data)
    # TODO: 여기서 실제 키움 REST 호출로 교체 (성공 시 status/open 으로 업데이트)
    return data

@router.get("/open")
def list_open(_user=Depends(require_role("trader"))):
    return STORE.get_open()

@router.post("/{order_id}/modify")
def modify(order_id: str, req: ModifyReq, _user=Depends(require_role("trader"))):
    if req.price is None and req.qty is None:
        raise HTTPException(400, "price 또는 qty 중 하나는 필요")
    o = STORE.modify(order_id, price=req.price, qty=req.qty)
    if not o: raise HTTPException(404, "order not found")
    return o

@router.post("/{order_id}/cancel")
def cancel(order_id: str, _user=Depends(require_role("trader"))):
    o = STORE.cancel(order_id)
    if not o: raise HTTPException(404, "order not found")
    return o
