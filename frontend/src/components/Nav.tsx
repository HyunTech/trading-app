"use client";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";

export default function Nav(){
  const router = useRouter();
  const path = usePathname();
  const logout = () => {
    localStorage.removeItem("token"); localStorage.removeItem("role");
    router.push("/login");
  };
  const Tab = ({href,label}:{href:string,label:string}) => (
    <Link href={href} className={`px-3 py-2 rounded ${path===href?"bg-black text-white":"border"}`}>{label}</Link>
  );
  return (
    <div className="flex items-center justify-between p-4 border-b bg-white sticky top-0 z-10">
      <div className="flex gap-2">
        <Tab href="/dashboard" label="대시보드" />
        <Tab href="/trade" label="주문" />
      </div>
      <button className="px-3 py-2 border rounded" onClick={logout}>로그아웃</button>
    </div>
  );
}
