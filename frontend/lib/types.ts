export interface FeeFlag {
  fee_type: string;
  found_pct: number;
  typical_range_pct: number[];
  severity: string;
}

export interface ComplianceFlag {
  rule_violated: string;
  severity: string;
}

export interface LoanAnalysis {
  id: string;
  fairness_score: number;
  confidence: number;
  computation: {
    verified_emi: number;
    stated_emi: number | null;
    emi_deviation_pct: number;
    fee_flags: FeeFlag[];
    compliance_flags: ComplianceFlag[];
    apr?: number;
    predatory_signals?: string[];
  };
  explanation: string;
  reproducible: boolean;
  created_at: string;
}

export interface LoanListItem {
  id: string;
  principal: number;
  fairness_score: number;
  created_at: string;
}

export interface Advisor {
  role: string;
  advice: string;
  evidence: string[];
  reasoning: string;
  confidence: number;
  risk_level: string;
  formula_used: string | null;
}

export interface BoardChatResponse {
  id: string;
  advisors: Advisor[];
  language: string;
  created_at: string;
}
