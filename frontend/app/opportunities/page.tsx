import Link from "next/link";
import { Card, PageHeader, StageBadge } from "@/components/ui";
import { getCompanies } from "@/lib/data";
const rank:Record<string,number>={S3:4,S2:3,S1:2,S0:1};
export default async function OpportunitiesPage(){const {items}=await getCompanies();const sorted=[...items].sort((a,b)=>rank[b.current_stage]-rank[a.current_stage]||(b.rd_size??0)-(a.rd_size??0));return <><PageHeader eyebrow="Opportunity Queue" title="机会排行榜" description="按证据阶段与研发规模排序，不展示或暗示未经校准的采购概率。"/><div className="mb-4 rounded-lg border border-blue-200 bg-blue-50 p-3 text-sm text-blue-800">排序用于销售排查优先级。S3 表示存在明确采购触发证据，不代表必然采购。</div><Card><div className="divide-y">{sorted.map((c,index)=><Link key={c.id} href={`/companies/${c.id}`} className="grid grid-cols-[52px_1fr_auto] items-center gap-4 p-5 hover:bg-paper"><span className="text-2xl font-light text-slate-300">{String(index+1).padStart(2,"0")}</span><div><p className="font-semibold">{c.name}</p><p className="mt-1 text-xs text-slate-500">{c.province} · {c.industry} · 研发约 {c.rd_size??"待核"} 人 · ICP {c.icp_tier}</p></div><StageBadge stage={c.current_stage}/></Link>)}</div></Card></>}

