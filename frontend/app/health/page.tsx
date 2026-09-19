"use client";

import { useEffect, useState } from 'react';
import { apiFetch } from '@/lib/api';
import { StatusPill } from '@/components/ui/StatusPill';
import type { HealthStatus } from '@/types/dashboard';

export default function HealthPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null);

  useEffect(() => {
    apiFetch<HealthStatus>('/api/v1/health')
      .then(setHealth)
      .catch((err) => console.error(err));
  }, []);

  const checks = health ? [
    { label: 'API status', value: health.status || 'ok' },
    { label: 'Database status', value: health.database || 'ok' },
    { label: 'Redis status', value: health.redis || 'ok' },
    { label: 'AI service status', value: health.ai_service || 'degraded' },
    { label: 'Telemetry ingestion', value: health.telemetry || 'ok' },
  ] : [];

  return (
    <main className="flex-1 p-6 md:p-8">
      <div className="mb-6">
        <div className="text-xs uppercase tracking-[0.24em] text-sky-300/80">System health</div>
        <h1 className="text-3xl font-bold">Platform health</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {checks.map((item) => (
          <div key={item.label} className="card p-4">
            <div className="text-sm text-slate-400">{item.label}</div>
            <div className="mt-3 flex items-center justify-between">
              <div className="text-xl font-semibold uppercase">{item.value}</div>
              <StatusPill value={item.value === 'ok' ? 'Healthy' : item.value === 'degraded' ? 'Degraded' : 'Issue'} tone={item.value === 'ok' ? 'success' : item.value === 'degraded' ? 'warning' : 'danger'} />
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}
