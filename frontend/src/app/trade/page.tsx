"use client";
import { useEffect, useState } from "react";
import Nav from "@/components/Nav";

const API = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
async function api(path:string, opts:RequestInit={}) {
  const tok = typeof window!=="undefined" ? localStorage.getItem("token") : null;
  const res = await fetch(`${API}${path}`, {
    headers: {"Content-Type":"application/json", ...(tok?{Authorization:`Bearer ${tok}`}:{})},
    ...opts
  });
  if(!res.ok) throw new Error(await res.text()); return res.json();
}

type Order = { order_id:string; status:string; market:"kr"|"us"; symbol:string; side:"buy"|"sell"; qty:number; price?:number; order_type:"limit"|"market" };

export default function Trade(){
  const [loggedIn, setLoggedIn] = useState<boolean| null>(null);
  useEffect(()=>{ setLoggedIn(!!localStorage.getItem("token")); }, []);

  // 주문 폼
  const [market, setMarket] = useState<"kr"|"us">("kr");
  const [symbol, setSymbol] = useState("005930");
  const [qty, setQty] = useState("1");
  const [orderType, setOrderType] = useState<"limit"|"market">("limit");
  const [price, setPrice] = useState("70000");

  const [err, setErr] = useState<string|null>(null);
  const [resp, setResp] = useState<any>(null);

  // 미체결
  const [openOrders, setOpenOrders] = useState<Order[]>([]);
  const [modPrice, setModPrice] = useState(""); const [modQty, setModQty] = useState("");
  async function refreshOpen(){ try{ setOpenOrders(await api("/orders/open")); }catch(e:any){ setErr(String(e)); } }
  useEffect(()=>{ if(loggedIn) refreshOpen(); }, [loggedIn]);

  function validate(){
    const q = Number(qty); if(!symbol.trim()) return "종목코드를 입력하세요.";
    if(!Number.isFinite(q)||q<=0) return "수량은 1 이상의 숫자여야 합니다.";
    if(orderType==="limit"){ const p=Number(price); if(!Number.isFinite(p)||p<=0) return "지정가 가격은 0보다 커야 합니다."; }
    return null;
  }
  async function place(side:"buy"|"sell"){
    setErr(null);
    if(!loggedIn) return setErr("로그인이 필요합니다.");
    const v = validate(); if(v) return setErr(v);
    const body:any = { market, symbol:symbol.trim(), qty:Number(qty), order_type:orderType, side };
    if(orderType==="limit") body.price=Number(price);
    try{ const r=await api("/orders",{method:"POST", body:JSON.stringify(body)}); setResp(r); await refreshOpen(); }
    catch(e:any){ setErr(String(e)); }
  }
  async function modify(id:string){
    const payload:any={}; if(modPrice) payload.price=Number(modPrice); if(modQty) payload.qty=Number(modQty);
    if(!payload.price && !payload.qty) return setErr("정정 가격 또는 수량 중 하나는 입력하세요.");
    try{ await api(`/orders/${id}/modify`,{method:"POST", body:JSON.stringify(payload)}); setModPrice(""); setModQty(""); await refreshOpen(); }
    catch(e:any){ setErr(String(e)); }
  }
  async function cancel(id:string){ try{ await api(`/orders/${id}/cancel`,{method:"POST"}); await refreshOpen(); } catch(e:any){ setErr(String(e)); } }

  return (
    <div className="min-h-screen bg-gray-50">
      <Nav/>
      <div className="p-6 grid gap-6 lg:grid-cols-2">
        <div className="bg-white p-5 rounded-2xl shadow">
          <h2 className="text-lg font-semibold mb-3">주문 입력</h2>
          {loggedIn===false && <p className="text-sm text-orange-600 mb-2">로그인 후 이용하세요 (/login)</p>}
          <div className="flex flex-wrap gap-2 items-center">
            <label className="text-sm text-gray-600">시장</label>
            <select className="border p-2 rounded" value={market} onChange={e=>setMarket(e.target.value as any)}>
              <option value="kr">KR(국내)</option><option value="us">US(해외)</option>
            </select>
            <label className="text-sm text-gray-600 ml-2">종목/티커</label>
            <input className="border p-2 rounded w-32" value={symbol} onChange={e=>setSymbol(e.target.value)} placeholder="005930/AAPL"/>
            <label className="text-sm text-gray-600 ml-2">수량</label>
            <input className="border p-2 rounded w-24" value={qty} onChange={e=>setQty(e.target.value)} inputMode="numeric"/>
            <label className="text-sm text-gray-600 ml-2">유형</label>
            <select className="border p-2 rounded" value={orderType} onChange={e=>setOrderType(e.target.value as any)}>
              <option value="limit">지정가</option><option value="market">시장가</option>
            </select>
            <label className="text-sm text-gray-600 ml-2">가격</label>
            <input className="border p-2 rounded w-28 disabled:bg-gray-100" value={price} onChange={e=>setPrice(e.target.value)}
                   disabled={orderType==="market"} placeholder={orderType==="market"?"시장가":"가격"} inputMode="numeric"/>
            <div className="flex gap-2 ml-2">
              <button className="px-4 py-2 rounded bg-black text-white disabled:opacity-50" onClick={()=>place("buy")} disabled={!loggedIn}>매수</button>
              <button className="px-4 py-2 rounded border disabled:opacity-50" onClick={()=>place("sell")} disabled={!loggedIn}>매도</button>
            </div>
          </div>
          {err && <p className="text-red-600 text-sm mt-3">Error: {String(err)}</p>}
          {resp && <pre className="text-xs bg-gray-50 p-3 rounded mt-3">{JSON.stringify(resp,null,2)}</pre>}
        </div>

        <div className="bg-white p-5 rounded-2xl shadow">
          <h2 className="text-lg font-semibold mb-3">미체결/열린 주문</h2>
          <div className="flex gap-2 mb-3">
            <input className="border p-2 rounded w-32" placeholder="정정가격" value={modPrice} onChange={e=>setModPrice(e.target.value)}/>
            <input className="border p-2 rounded w-24" placeholder="정정수량" value={modQty} onChange={e=>setModQty(e.target.value)}/>
            <button className="px-3 py-2 rounded border" onClick={refreshOpen}>새로고침</button>
          </div>
          <div className="space-y-2">
            {openOrders.length===0 && <div className="text-sm text-gray-500">열린 주문이 없습니다.</div>}
            {openOrders.map(o=>(
              <div key={o.order_id} className="border rounded p-3 flex items-center justify-between">
                <div className="text-sm">
                  <div><b>{o.symbol}</b> {o.side.toUpperCase()} x{o.qty} @ {o.price ?? "-"} ({o.order_type})</div>
                  <div className="text-gray-500">id: {o.order_id} · status: {o.status} · {o.market.toUpperCase()}</div>
                </div>
                <div className="flex gap-2">
                  <button className="px-3 py-1 rounded border" onClick={()=>modify(o.order_id)}>정정</button>
                  <button className="px-3 py-1 rounded border" onClick={()=>cancel(o.order_id)}>취소</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
