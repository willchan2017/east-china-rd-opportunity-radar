import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/sidebar";
export const metadata: Metadata = { title: "华东研发机会雷达", description: "面向先进制造企业的研发采购机会雷达" };
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="zh-CN"><body><Sidebar/><main className="min-h-screen lg:ml-64"><header className="flex h-16 items-center justify-between border-b bg-white/80 px-6 backdrop-blur"><span className="text-sm font-medium lg:hidden">华东研发机会雷达</span><span className="ml-auto rounded-full border px-3 py-1 text-xs text-slate-500">数据口径：公开证据 · 人工核验优先</span></header><div className="mx-auto max-w-[1480px] p-6 lg:p-8">{children}</div></main></body></html>}

