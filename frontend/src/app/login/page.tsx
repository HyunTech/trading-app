"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";

//const API = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";
const API = "https://trading-backend-ppqv.onrender.com"


export default function LoginPage() {
  const r = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      console.log("API =", API); // ← 실제로 호출되는 핸들러에서 찍기
      const res = await fetch(`${API}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`HTTP ${res.status} ${res.statusText} — ${txt}`);
      }

      const data = await res.json();
      localStorage.setItem("token", data.access_token);
      r.push("/dashboard");
    } catch (e: any) {
      console.error("Login error:", e);
      setErr(e?.message ?? "Failed to fetch");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-2xl shadow w-[360px] space-y-3">
        <h1 className="text-xl font-semibold mb-2">로그인</h1>

        <input
          className="w-full border rounded px-3 py-2"
          placeholder="아이디"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          className="w-full border rounded px-3 py-2"
          placeholder="비밀번호"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button className="w-full py-2 rounded bg-black text-white disabled:opacity-50" disabled={loading}>
          {loading ? "로그인 중..." : "로그인"}
        </button>

        {/* 현재 API 베이스 확인용(임시 표시) */}
        <p className="text-xs text-gray-500 break-all">API: {API}</p>

        {err && <div className="text-sm text-red-600">{String(err)}</div>}
      </form>
    </div>
  );
}
