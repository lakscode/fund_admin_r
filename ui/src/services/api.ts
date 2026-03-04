import { API_URL } from '../config/constants';
import { LandingData } from '../types/landing';
import { LeasingData } from '../types/leasing';
import { AssetsData } from '../types/assets';
import { FundsData } from '../types/funds';

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${endpoint}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.error || 'Request failed');
  }
  return data;
}

// Auth
export function loginUser(email: string, password: string) {
  return request<{ token: string; user: { id: string; email: string; name: string; role: string; role_id?: string }; message: string }>(
    '/login',
    { method: 'POST', body: JSON.stringify({ email, password }) },
  );
}

// Command Center
export function getCommandCenter() {
  return request<LandingData>('/command-center');
}

// Leasing
export function getLeasing() {
  return request<LeasingData>('/leasing');
}

// Assets
export function getAssets() {
  return request<AssetsData>('/assets');
}

// Funds
export function getFunds() {
  return request<FundsData>('/funds');
}
