"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function LoginPage() {
  const r = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    const res = await fetch(`${API}/auth/login`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) { setErr(await res.text()); return; }
    const data = await res.json();
    localStorage.setItem("token", data.access_token);
    r.push("/dashboard");
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <form onSubmit={onSubmit} className="bg-white p-6 rounded-2xl shadow w-[360px] space-y-3">
        <h1 className="text-xl font-semibold mb-2">로그인</h1>
        <input className="w-full border rounded px-3 py-2"
               placeholder="아이디"
               value={username} onChange={e=>setUsername(e.target.value)} />
        <input className="w-full border rounded px-3 py-2"
               placeholder="비밀번호" type="password"
               value={password} onChange={e=>setPassword(e.target.value)} />
        <button className="w-full py-2 rounded bg-black text-white">로그인</button>
        {err && <div className="text-sm text-red-600">{String(err)}</div>}
      </form>
    </div>
  );
}
