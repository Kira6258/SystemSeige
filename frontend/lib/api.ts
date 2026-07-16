export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

class Api {
  private getHeaders() {
    return {
      "Content-Type": "application/json",
    };
  }

  private async _fetch(url: string, options: RequestInit): Promise<Response> {
    return fetch(url, {
      ...options,
      credentials: "include",
      headers: {
        ...this.getHeaders(),
        ...options.headers,
      },
    });
  }

  async request<T>(endpoint: string, options: RequestInit = {}, retry = true): Promise<T> {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const url = `${baseUrl}${endpoint}`;

    let response = await this._fetch(url, options);

    // On 401, silently attempt a token refresh and retry ONCE
    if (response.status === 401 && retry) {
      const refreshed = await this._fetch(`${baseUrl}/api/auth/refresh`, { method: "POST" });
      if (refreshed.ok) {
        // Retry original request with new cookie
        response = await this._fetch(url, options);
      }
    }

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
