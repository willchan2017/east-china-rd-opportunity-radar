import type { Company, EventItem } from "./types";

export const sampleCompanies: Company[] = [
  { id: "sample-1", name: "华东精研科技（模拟）", industry: "半导体与集成电路", province: "上海", city: "上海", rd_size: 320, icp_tier: "A", crm_status: "未建档", current_stage: "S2", is_sample: true },
  { id: "sample-2", name: "江南智驱系统（模拟）", industry: "汽车电子与智能汽车", province: "江苏", city: "苏州", rd_size: 180, icp_tier: "A", crm_status: "跟进中", sales_owner: "演示销售", current_stage: "S3", is_sample: true },
  { id: "sample-3", name: "钱塘机器人实验室（模拟）", industry: "机器人与智能装备", province: "浙江", city: "杭州", rd_size: 95, icp_tier: "B", crm_status: "未建档", current_stage: "S1", is_sample: true },
];
export const sampleEvents: EventItem[] = [
  { id: "event-1", company_id: "sample-1", event_date: "2026-09-18", event_type: "研发组织扩张", event_title: "新增跨区域研发团队（模拟事件）", event_description: "用于演示事件时间线，不代表真实企业情报。", source_url: "https://example.com/mock-radar-event", source_type: "模拟数据", evidence_excerpt: "模拟证据：企业计划扩大跨区域研发协作团队。", confidence_level: "low", verification_status: "模拟数据", is_sample: true },
  { id: "event-2", company_id: "sample-2", event_date: "2026-10-02", event_type: "工具替换", event_title: "启动研发工具评估（模拟事件）", event_description: "用于展示明确采购触发状态。", source_url: "https://example.com/mock-tool-review", source_type: "模拟数据", evidence_excerpt: "模拟证据：公开采购需求中提到研发管理平台评估。", confidence_level: "low", verification_status: "模拟数据", is_sample: true },
];

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";
async function safeFetch<T>(path: string, fallback: T): Promise<T> {
  try { const response = await fetch(`${API_URL}${path}`, { cache: "no-store" }); return response.ok ? await response.json() as T : fallback; }
  catch { return fallback; }
}
export async function getCompanies() { return safeFetch<{items: Company[]; total: number}>("/companies?page_size=100", {items: sampleCompanies, total: sampleCompanies.length}); }
export async function getCompany(id: string) { return safeFetch<Company>(`/companies/${id}`, sampleCompanies.find(c => c.id === id) ?? sampleCompanies[0]); }
export async function getEvents(companyId?: string) { const events = companyId ? sampleEvents.filter(e => e.company_id === companyId) : sampleEvents; return safeFetch<{items: EventItem[]; total: number}>(`/events${companyId ? `?company_id=${companyId}` : ""}`, {items: events, total: events.length}); }

