import { clearAuthToken, getAuthHeaders } from '@/lib/auth';
import { API_BASE_URL } from '@/lib/config';

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: getAuthHeaders(init?.headers),
    ...init,
  });

  if (!response.ok) {
    const errorText = await response.text();
    let message = `Request failed with status ${response.status}`;
    try {
      const payload = JSON.parse(errorText);
      const detail = payload?.detail;
      message = typeof detail === 'string' ? detail : detail?.message || message;
    } catch {
      if (errorText) message = errorText;
    }
    if (response.status === 401 && typeof window !== 'undefined') {
      clearAuthToken();
      window.location.replace('/login');
    }
    if (response.status === 403) message = message || 'This action is not available on your current plan.';
    if (response.status === 404) message = 'The requested resource was not found.';
    if (response.status === 422) message = 'Please check the submitted values and try again.';
    if (response.status === 429) message = 'Usage limit reached. Please try again later or upgrade your plan.';
    if (response.status >= 500) message = 'The service is temporarily unavailable. Please try again shortly.';
    throw new ApiError(response.status, message);
  }

  return response.json() as Promise<T>;
}
