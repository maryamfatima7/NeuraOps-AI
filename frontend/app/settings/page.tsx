"use client";

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { apiFetch } from '@/lib/api';
import type { AuthUser } from '@/lib/auth';

type Usage = {
  plan: string;
  plan_status: string;
  usage: Record<string, number>;
  limits: Record<string, number | boolean>;
};

export default function SettingsPage() {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [usage, setUsage] = useState<Usage | null>(null);

  useEffect(() => {
    Promise.all([apiFetch<AuthUser>('/api/v1/auth/me'), apiFetch<Usage>('/api/v1/auth/usage')])
      .then(([profile, planUsage]) => {
        setUser(profile);
        setUsage(planUsage);
      })
      .catch((error) => console.error(error));
  }, []);

  return (
    <main className="flex-1 p-6 md:p-8">
      <div className="mb-6">
        <div className="text-xs uppercase tracking-[0.24em] text-sky-300/80">Settings</div>
        <h1 className="text-3xl font-bold">Platform configuration</h1>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
      <div className="card p-5 space-y-4">
        <div>
          <div className="text-sm text-slate-400">Observability profile</div>
          <div className="mt-2 text-lg font-semibold">Production engineering view</div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-slate-300">
          <div className="rounded-xl bg-slate-900/50 p-3">Telemetry retention: 30 days</div>
          <div className="rounded-xl bg-slate-900/50 p-3">Alert threshold profile: Balanced</div>
          <div className="rounded-xl bg-slate-900/50 p-3">AI incident mode: Structured fallback enabled</div>
          <div className="rounded-xl bg-slate-900/50 p-3">Security posture: JWT + env-based config</div>
        </div>
      </div>

      <div className="card p-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="text-sm text-slate-400">Workspace account</div>
            <div className="mt-2 text-lg font-semibold">{user?.full_name || 'Loading profile'}</div>
            <div className="text-sm text-slate-400">{user?.email}</div>
          </div>
          <span className="badge bg-sky-500/15 text-sky-300">{usage?.plan || user?.plan || 'FREE'}</span>
        </div>
        <div className="mt-6 grid grid-cols-2 gap-3 text-sm">
          <div className="rounded-xl bg-slate-900/50 p-3"><span className="text-slate-400">Services</span><div className="mt-1 font-semibold">{usage?.usage.services ?? 0} / {usage?.limits.max_services === -1 ? '∞' : usage?.limits.max_services ?? 2}</div></div>
          <div className="rounded-xl bg-slate-900/50 p-3"><span className="text-slate-400">AI analyses</span><div className="mt-1 font-semibold">{usage?.usage.ai_analyses ?? 0} / {usage?.limits.max_ai_analyses_per_day === -1 ? '∞' : usage?.limits.max_ai_analyses_per_day ?? 3}</div></div>
        </div>
        {usage?.plan !== 'PRO' ? <Link href="/pricing" className="mt-5 inline-flex rounded-xl bg-sky-500 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-sky-400">Compare PRO</Link> : null}
      </div>
      </div>
    </main>
  );
}
