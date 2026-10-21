import { Badge, Card, PageHeader } from "@/components/ui";
const rules=[
  {code:"B01",category:"B",name:"融资或资本动作",desc:"企业完成融资、上市或重大资本动作",keywords:["融资","IPO","定增"]},
  {code:"B02",category:"B",name:"业务扩张",desc:"新基地、新产品线或业务规模明显扩张",keywords:["基地","量产","扩产"]},
  {code:"R01",category:"R",name:"研发组织扩张",desc:"研发团队、研发中心或跨区域协作规模扩大",keywords:["研发中心","研发招聘"]},
  {code:"R02",category:"R",name:"工具链复杂度上升",desc:"多团队、多工具或合规要求带来研发管理压力",keywords:["协同","合规","流程"]},
  {code:"P01",category:"P",name:"明确招采",desc:"公开招标、采购公告或供应商征集",keywords:["招标","采购","供应商"]},
  {code:"P02",category:"P",name:"工具替换",desc:"现有研发工具升级或替换的公开证据",keywords:["Jira","ALM","研发管理平台"]},
];
export default function SignalsPage(){return <><PageHeader eyebrow="Rule Configuration" title="信号规则管理" description="B 业务拐点、R 研发管理压力、P 采购触发。规则独立存储并支持版本化，避免全部硬编码在 AI Prompt 中。"/><div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{rules.map(r=><Card key={r.code} className="p-5"><div className="flex items-center justify-between"><Badge tone={r.category==="B"?"blue":r.category==="R"?"amber":"red"}>{r.code}</Badge><span className="text-xs text-emerald-600">已启用 · v1</span></div><h2 className="mt-5 font-semibold">{r.name}</h2><p className="mt-2 min-h-10 text-sm leading-5 text-slate-500">{r.desc}</p><div className="mt-5 flex flex-wrap gap-2">{r.keywords.map(k=><span key={k} className="rounded bg-paper px-2 py-1 text-xs text-slate-600">{k}</span>)}</div></Card>)}</div></>}

