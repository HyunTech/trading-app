"use client";
import { useEffect, useState } from "react";
import Nav from "@/components/Nav";
import PositionTable from "@/components/PositionTable";

type Perf = {
    since: string; cum_pnl: number; mtd_pnl: number; win_rate: number; avg_rr: number;
    benchmark: { name: string; ytd: number }; team_ytd: number; curve: { d: string; pnl: number }[]
};

const API = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
async function api(path: string, opts: RequestInit = {}) {
    const tok = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    const res = await fetch(`${API}${path}`, { headers: { "Content-Type": "application/json", ...(tok ? { Authorization: `Bearer ${tok}` } : {}) }, ...opts });
    if (!res.ok) throw new Error(await res.text()); return res.json();
}

// 백엔드 더미 → 표 행 변환 (현재가는 임시 계산: (매수총액+손익)/수량)
const toKRRows = (kr: any) => (kr?.positions ?? []).map((p: any) => {
    const qty = +p.qty || 0, avg = +p.avg || 0, pnl = +p.pl || 0;
    const cur = qty > 0 ? (avg * qty + pnl) / qty : avg;
    const rate = qty > 0 && avg > 0 ? pnl / (avg * qty) : 0;
    return { symbol: p.code, name: p.name, qty, avg, current: Math.round(cur), pnl, pnlRate: rate };
});
const toUSRows = (us: any) => (us?.positions ?? []).map((p: any) => {
    const qty = +p.qty || 0, avg = +p.avg || 0, pnl = +p.pl || 0;
    const cur = qty > 0 ? (avg * qty + pnl) / qty : avg;
    const rate = qty > 0 && avg > 0 ? pnl / (avg * qty) : 0;
    return { symbol: p.ticker, name: p.name, qty, avg, current: Math.round(cur * 100) / 100, pnl, pnlRate: rate };
});

export default function Dashboard() {
    const [kr, setKr] = useState<any>(null);
    const [us, setUs] = useState<any>(null);
    const [perf, setPerf] = useState<Perf | null>(null);
    const [err, setErr] = useState<string | null>(null);

    useEffect(() => {
        api("/portfolio/balances?market=kr").then(setKr).catch(e => setErr(String(e)));
        api("/portfolio/balances?market=us").then(setUs).catch(e => setErr(String(e)));
        api("/metrics/team-performance").then(setPerf).catch(e => setErr(String(e)));
    }, []);

    return (
        <div className="min-h-screen bg-gray-50">
            <Nav />
            <div className="p-6 grid gap-6 lg:grid-cols-3">
                <div className="lg:col-span-2 grid gap-6">
                    <PositionTable
                        title="국내 잔고"
                        rows={toKRRows(kr)}
                        note="현재가: 임시 계산값. 추후 키움 REST 실시간가로 대체"
                    />
                    <PositionTable
                        title="해외 잔고"
                        rows={toUSRows(us)}
                        note="현재가: 임시 계산값. 추후 실시간가로 교체"
                    />
                </div>

                <div className="bg-white p-5 rounded-2xl shadow">
                    <h2 className="text-lg font-semibold mb-3">팀 성과</h2>
                    {perf ? (
                        <div className="space-y-2 text-sm">
                            <div><b>누적 손익</b>: {perf.cum_pnl.toLocaleString()} 원</div>
                            <div><b>이달 손익</b>: {perf.mtd_pnl.toLocaleString()} 원</div>
                            <div><b>승률</b>: {(perf.win_rate * 100).toFixed(1)}%</div>
                            <div><b>평균 손익비</b>: {perf.avg_rr.toFixed(2)}</div>
                            <div><b>YTD</b>: {(perf.team_ytd * 100).toFixed(1)}% (벤치마크 {perf.benchmark.name}: {(perf.benchmark.ytd * 100).toFixed(1)}%)</div>
                            <div className="mt-3">
                                <div className="text-gray-500 mb-1">최근 10일 일손익</div>
                                <ul className="max-h-40 overflow-auto border rounded p-2">
                                    {perf.curve.map(c => (
                                        <li key={c.d} className="flex justify-between"><span>{c.d}</span><span>{c.pnl.toLocaleString()} 원</span></li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    ) : "로딩..."}
                </div>
            </div>
            {err && <div className="p-6 text-red-600 text-sm">Error: {err}</div>}
        </div>
    );
}
