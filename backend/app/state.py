from typing import Dict, Any
from threading import RLock
import time

class OrderStore:
    def __init__(self):
        self._lock = RLock()
        self._data: Dict[str, Dict[str, Any]] = {}  # order_id -> order dict

    def add(self, order: Dict[str, Any]) -> None:
        with self._lock:
            self._data[order["order_id"]] = order

    def get_open(self):
        with self._lock:
            return [o for o in self._data.values() if o["status"] in ("accepted","open","modified")]

    def modify(self, oid: str, *, price: float | None, qty: int | None):
        with self._lock:
            o = self._data.get(oid)
            if not o: return None
            if price is not None: o["price"] = price
            if qty is not None: o["qty"] = qty
            o["status"] = "modified"
            o["updated_at"] = int(time.time()*1000)
            return o

    def cancel(self, oid: str):
        with self._lock:
            o = self._data.get(oid)
            if not o: return None
            o["status"] = "canceled"
            o["updated_at"] = int(time.time()*1000)
            return o

STORE = OrderStore()
