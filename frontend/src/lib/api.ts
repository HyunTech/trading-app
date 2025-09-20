export const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export function getToken(){
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

export async function api(path: string, opts: RequestInit = {}) {
  const headers: Record<string,string> = { "Content-Type": "application/json", ...(opts.headers as any || {}) };
  const tok = getToken();
  if (tok) headers["Authorization"] = `Bearer ${tok}`;

  const res = await fetch(`${API_BASE}${path}`, { ...opts, headers });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
