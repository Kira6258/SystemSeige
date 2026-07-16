export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

class Api {
  private getHeaders() {
    const token = localStorage.getItem("token");
    return {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
  }

  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `http://localhost:8000${endpoint}`;
    const headers = this.getHeaders();
    
    const response = await fetch(url, {
      ...options,
      credentials: "include",
      headers: {
        ...headers,
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new ApiError(
        response.status,
        errorData?.error || errorData?.detail || `API Error: ${response.statusText}`
      );
    }

    if (response.status === 204) return {} as T;
    return response.json();
  }

  get<T>(endpoint: string) { return this.request<T>(endpoint, { method: "GET" }); }
  post<T>(endpoint: string, body: any) { return this.request<T>(endpoint, { method: "POST", body: JSON.stringify(body) }); }
  put<T>(endpoint: string, body: any) { return this.request<T>(endpoint, { method: "PUT", body: JSON.stringify(body) }); }
  delete<T>(endpoint: string) { return this.request<T>(endpoint, { method: "DELETE" }); }
}

export const api = new Api();
