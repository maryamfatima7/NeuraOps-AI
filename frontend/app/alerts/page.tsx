"use client";

import { useEffect, useState } from 'react';
import { apiFetch } from '@/lib/api';
import { StatusPill } from '@/components/ui/StatusPill';
import type { Alert } from '@/types/dashboard';

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);

  useEffect(() => {
    apiFetch<Alert[]>('/api/v1/alerts')
      .then(setAlerts)
      .catch((err) => console.error(err));
  }, []);

  return (
    <main className="flex-1 p-6 md:p-8">
      <div className="mb-6">
        <div className="text-xs uppercase tracking-[0.24em] text-sky-300/80">Alerts</div>
        <h1 className="text-3xl font-bold">Alert rules</h1>
      </div>

      <div className="space-y-4">
        {alerts.map((alert) => (
          <div key={alert.id} className="card p-4 flex flex-col md:flex-row justify-between gap-3">
            <div>
              <div className="text-lg font-semibold">{alert.rule}</div>
              <div className="text-slate-400 text-sm">Service: {alert.service || 'unknown'}</div>
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              <StatusPill value={alert.severity} tone={alert.severity === 'CRITICAL' ? 'danger' : alert.severity === 'HIGH' ? 'warning' : 'info'} />
              <StatusPill value={alert.status} tone={alert.status === 'resolved' ? 'success' : 'neutral'} />
              <span className="text-sm text-slate-400">{alert.current_value} / {alert.threshold}</span>
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}
