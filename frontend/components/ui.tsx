import { type HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export function Card({className, ...props}: HTMLAttributes<HTMLDivElement>) { return <div className={cn("rounded-xl border bg-white shadow-panel", className)} {...props}/>; }
export function Badge({children, tone="neutral"}: {children: React.ReactNode; tone?: "neutral"|"green"|"amber"|"red"|"blue"}) {
  const tones={neutral:"bg-slate-100 text-slate-700",green:"bg-emerald-50 text-emerald-700",amber:"bg-amber-50 text-amber-700",red:"bg-red-50 text-red-700",blue:"bg-blue-50 text-blue-700"};
  return <span className={cn("inline-flex rounded-md px-2 py-1 text-xs font-medium", tones[tone])}>{children}</span>;
}
export function PageHeader({eyebrow,title,description,action}:{eyebrow:string;title:string;description:string;action?:React.ReactNode}) { return <div className="mb-7 flex items-end justify-between gap-4"><div><p className="mb-2 text-xs font-bold uppercase tracking-[.2em] text-forest/60">{eyebrow}</p><h1 className="text-3xl font-semibold tracking-tight">{title}</h1><p className="mt-2 max-w-3xl text-sm text-slate-500">{description}</p></div>{action}</div>; }
export function StageBadge({stage}:{stage:string}) { const map:Record<string,[string,string]>={S0:["长期观察","neutral"],S1:["业务拐点","blue"],S2:["研发压力","amber"],S3:["采购触发","red"]}; const [label,tone]=map[stage]??[stage,"neutral"]; return <Badge tone={tone as "neutral"|"blue"|"amber"|"red"}>{stage} · {label}</Badge>; }

