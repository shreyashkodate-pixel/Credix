export type AllowedEducation = "Graduate" | "Not Graduate";
export type AllowedSelfEmployed = "Yes" | "No";
export type AllowedDependents = "0" | "1" | "2" | "3+";
export type AllowedPropertyArea = "Urban" | "Semiurban" | "Rural";
export type AllowedCreditHistory = 0 | 1;
export type AllowedLoanTerm = 12 | 36 | 60 | 120 | 180 | 240 | 300 | 360 | 480;

export interface PredictionInput {
  applicant_income: number;
  coapplicant_income: number;
  loan_amount: number;
  loan_amount_term: AllowedLoanTerm;
  credit_history: AllowedCreditHistory;
  education: AllowedEducation;
  self_employed: AllowedSelfEmployed;
  dependents: AllowedDependents;
  property_area: AllowedPropertyArea;
}

export interface PredictionFactor {
  factor: string;
  impact: "positive" | "negative";
  weight: number;
  description: string;
}

export interface PredictionExplanation {
  method: string;
  factors: PredictionFactor[];
}

export interface PredictionResponse {
  prediction_id: string;
  outcome: "Approved" | "Rejected";
  probability: number | null;
  model_version: string;
  created_at: string;
  explanation: PredictionExplanation;
}

export interface PredictionHistoryItem {
  id: string;
  created_at: string;
  model_version: string;
  outcome: "Approved" | "Rejected" | string;
  probability: number | null;
  explanation: PredictionExplanation;
  input_snapshot: Record<string, string | number | undefined>;
}

export interface PredictionHistoryPage {
  items: PredictionHistoryItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface UserResponse {
  id: string;
  email: string;
  role: "user" | "admin" | string;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  role: string;
  user_id: string;
}

export interface AdminDashboardMetrics {
  total_users: number;
  total_predictions: number;
  approved_predictions: number;
  rejected_predictions: number;
  approval_rate_percent: number;
}

export interface AdminUserListPage {
  users: UserResponse[];
  total: number;
  page: number;
  page_size: number;
}

export interface ApiErrorDetail {
  loc?: (string | number)[];
  msg?: string;
  type?: string;
}

export interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
    details?: ApiErrorDetail[] | string[];
  };
  request_id?: string;
}

