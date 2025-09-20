"use client";
type Row = { symbol: string; name: string; qty: number; avg: number; current: number; pnl: number; pnlRate: number };

const cls = (n: number) => n > 0 ? "text-emerald-600" : n < 0 ? "text-red-600" : "text-gray-600";
const fm = (n: number) => n.toLocaleString();
const fr = (r: number) => `${(r * 100).toFixed(2)}%`;

export default function PositionTable({ title, rows, note }: { title: string; rows: Row[]; note?: string; }) {
    return (
        <div className="bg-white p-5 rounded-2xl shadow">
            <div className="flex items-end justify-between mb-3">
                <h2 className="text-lg font-semibold">{title}</h2>
                {note && <span className="text-xs text-gray-500">{note}</span>}
            </div>
            <div className="overflow-auto">
                <table className="min-w-full text-sm">
                    <thead className="text-gray-500">
                        <tr className="[&>th]:py-2 [&>th]:px-2 text-left">
                            <th className="w-36">종목명</th>
                            <th className="w-20 text-right">수량</th>
                            <th className="w-28 text-right">매수가</th>
                            <th className="w-28 text-right">현재가</th>
                            <th className="w-28 text-right">손익금액</th>
                            <th className="w-24 text-right">수익률</th>
                        </tr>
                    </thead>
                    <tbody className="[&>tr>td]:py-2 [&>tr>td]:px-2">
                        {rows.length === 0 ? (
                            <tr><td colSpan={6} className="text-center text-gray-400 py-6">보유 포지션이 없습니다.</td></tr>
                        ) : rows.map(r => (
                            <tr key={`${r.symbol}-${r.name}`} className="border-t">
                                <td><div className="font-medium">{r.name}</div><div className="text-xs text-gray-500">{r.symbol}</div></td>
                                <td className="text-right">{r.qty.toLocaleString()}</td>
                                <td className="text-right">{fm(r.avg)}</td>
                                <td className="text-right">{fm(r.current)}</td>
                                <td className={`text-right font-medium ${cls(r.pnl)}`}>{fm(r.pnl)}</td>
                                <td className={`text-right ${cls(r.pnl)}`}>{fr(r.pnlRate)}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
