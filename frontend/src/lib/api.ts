import {
  PredictionInput,
  PredictionResponse,
  PredictionHistoryPage,
  PredictionHistoryItem,
  UserResponse,
  TokenResponse,
  AdminDashboardMetrics,
  AdminUserListPage,
  ApiErrorResponse,
} from "@/types/api";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export class ApiError extends Error {
  code: string;
  status: number;
  details?: unknown;
  requestId?: string;

  constructor(
    message: string,
    code: string = "INTERNAL_ERROR",
    status: number = 500,
    details?: unknown,
    requestId?: string
  ) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
    this.details = details;
    this.requestId = requestId;
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {},
  token?: string | null
): Promise<{ data: T; requestId: string | null }> {
  const url = `${BASE_URL}${endpoint}`;
  const headers = new Headers(options.headers || {});

  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  const requestId = response.headers.get("x-request-id");

  if (!response.ok) {
    let errorData: ApiErrorResponse | null = null;
    let fallbackText = "";

    try {
      errorData = (await response.json()) as ApiErrorResponse;
    } catch {
      fallbackText = await response.text();
    }

    if (errorData?.error) {
      throw new ApiError(
        errorData.error.message || "An API error occurred.",
        errorData.error.code || `HTTP_${response.status}`,
        response.status,
        errorData.error.details,
        errorData.request_id || requestId || undefined
      );
    }

    throw new ApiError(
      fallbackText || response.statusText || "Request failed.",
      `HTTP_${response.status}`,
      response.status,
      undefined,
      requestId || undefined
    );
  }

  const data = (await response.json()) as T;
  return { data, requestId };
}

export const api = {
  // Authentication
  async register(email: string, password: string): Promise<UserResponse> {
    const { data } = await request<UserResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    return data;
  },

  async login(email: string, password: string): Promise<TokenResponse> {
    const { data } = await request<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    return data;
  },

  async getMe(token: string): Promise<UserResponse> {
    const { data } = await request<UserResponse>("/auth/me", {}, token);
    return data;
  },

  async logout(token: string): Promise<{ message: string }> {
    const { data } = await request<{ message: string }>("/auth/logout", { method: "POST" }, token);
    return data;
  },

  // Predictions
  async createPrediction(
    payload: PredictionInput,
    token: string
  ): Promise<{ prediction: PredictionResponse; requestId: string | null }> {
    const { data, requestId } = await request<PredictionResponse>(
      "/predictions",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      token
    );
    return { prediction: data, requestId };
  },

  async getPredictionHistory(
    page: number = 1,
    pageSize: number = 20,
    token: string
  ): Promise<PredictionHistoryPage> {
    const { data } = await request<PredictionHistoryPage>(
      `/predictions/history?page=${page}&page_size=${pageSize}`,
      {},
      token
    );
    return data;
  },

  async getPredictionDetail(id: string, token: string): Promise<PredictionHistoryItem> {
    const { data } = await request<PredictionHistoryItem>(`/predictions/history/${id}`, {}, token);
    return data;
  },

  // Admin
  async getAdminDashboard(token: string): Promise<AdminDashboardMetrics> {
    const { data } = await request<AdminDashboardMetrics>("/admin/dashboard", {}, token);
    return data;
  },

  async getAdminUsers(
    page: number = 1,
    pageSize: number = 20,
    token: string
  ): Promise<AdminUserListPage> {
    const { data } = await request<AdminUserListPage>(
      `/admin/users?page=${page}&page_size=${pageSize}`,
      {},
      token
    );
    return data;
  },
};

