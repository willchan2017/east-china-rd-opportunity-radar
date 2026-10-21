export type Stage = "S0" | "S1" | "S2" | "S3";
export interface Company { id: string; name: string; industry: string; province: string; city?: string | null; rd_size?: number | null; icp_tier: string; crm_status: string; sales_owner?: string | null; current_stage: Stage; is_sample: boolean; }
export interface EventItem { id: string; company_id: string; event_date: string; event_type: string; event_title: string; event_description: string; source_url: string; source_type: string; evidence_excerpt: string; confidence_level: string; verification_status: string; is_sample: boolean; }

