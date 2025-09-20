"use client";
import { useState } from "react";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";

export default function Login(){
  const [email,setEmail]=useState("admin@team.com");
  const [password,setPassword]=useState("admin123");
  const [err,setErr]=useState<string|null>(null);
  const router = useRouter();
  async function onLogin(){
    setErr(null);
    try{
      const r = await api("/auth/login", { method:"POST", body: JSON.stringify({email,password})});
      localStorage.setItem("token", r.access_token);
      localStorage.setItem("role", r.role);
      router.push("/dashboard");
    }catch(e:any){ setErr(String(e)); }
  }
  return (
    <div className="h-screen flex items-center justify-center">
      <div className="w-full max-w-sm bg-white p-6 rounded-2xl shadow space-y-3">
        <h1 className="text-xl font-semibold">팀 로그인</h1>
        <input className="border p-2 rounded w-full" value={email} onChange={e=>setEmail(e.target.value)} />
        <input type="password" className="border p-2 rounded w-full" value={password} onChange={e=>setPassword(e.target.value)} />
        {err && <p className="text-red-600 text-sm">{err}</p>}
        <button className="w-full py-2 rounded bg-black text-white" onClick={onLogin}>로그인</button>
      </div>
    </div>
  );
}

