import { API_BASE_URL } from '@/lib/config';

export const AUTH_STORAGE_KEY = 'neuraops_auth_token';

export type AuthUser = {
  id: number;
  email: string;
  full_name: string;
  plan: string;
  plan_status: string;
};

export function getAuthToken(): string | null {
  if (typeof window === 'undefined') {
    return null;
  }

  return window.localStorage.getItem(AUTH_STORAGE_KEY);
}

export function setAuthToken(token: string | null) {
  if (typeof window === 'undefined') {
    return;
  }

  if (token) {
    window.localStorage.setItem(AUTH_STORAGE_KEY, token);
    return;
  }

  window.localStorage.removeItem(AUTH_STORAGE_KEY);
}

export function clearAuthToken() {
  setAuthToken(null);
}

export function getAuthHeaders(extraHeaders: HeadersInit = {}): HeadersInit {
  const token = getAuthToken();

  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...extraHeaders,
  };
}

export async function fetchCurrentUser(): Promise<AuthUser | null> {
  const token = getAuthToken();
  if (!token) {
    return null;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Authentication required');
    }

    return (await response.json()) as AuthUser;
  } catch {
    clearAuthToken();
    return null;
  }
}
