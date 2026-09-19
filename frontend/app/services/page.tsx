"use client";

import { useEffect, useState } from 'react';
import { apiFetch } from '@/lib/api';
import { StatusPill } from '@/components/ui/StatusPill';
import type { ServiceSummary } from '@/types/dashboard';

export default function ServicesPage() {
  const [services, setServices] = useState<ServiceSummary[]>([]);

  useEffect(() => {
    apiFetch<ServiceSummary[]>('/api/v1/services')
      .then(setServices)
      .catch((err) => console.error(err));
  }, []);

  return (
    <main className="flex-1 p-6 md:p-8">
      <div className="mb-6">
        <div className="text-xs uppercase tracking-[0.24em] text-sky-300/80">Service monitoring</div>
        <h1 className="text-3xl font-bold">Services</h1>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        {services.map((service) => (
          <div key={service.id} className="card p-4">
            <div className="flex items-start justify-between gap-3 mb-4">
              <div>
                <h2 className="text-xl font-semibold">{service.name}</h2>
                <p className="text-sm text-slate-400">{service.description || 'Production service'}</p>
              </div>
              <StatusPill value={service.status.toUpperCase()} tone={service.status === 'healthy' ? 'success' : service.status === 'degraded' ? 'warning' : 'danger'} />
            </div>

            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-xl bg-slate-900/50 p-3"><div className="text-slate-400">Uptime</div><div className="mt-1 text-lg font-semibold">{service.uptime}%</div></div>
              <div className="rounded-xl bg-slate-900/50 p-3"><div className="text-slate-400">Request rate</div><div className="mt-1 text-lg font-semibold">{service.request_rate}/min</div></div>
              <div className="rounded-xl bg-slate-900/50 p-3"><div className="text-slate-400">Error rate</div><div className="mt-1 text-lg font-semibold">{service.error_rate}%</div></div>
              <div className="rounded-xl bg-slate-900/50 p-3"><div className="text-slate-400">Latency</div><div className="mt-1 text-lg font-semibold">{service.latency_ms} ms</div></div>
            </div>

            <div className="mt-4 text-sm text-slate-300">
              <div>Dependencies: {service.dependencies || 'N/A'}</div>
              <div className="mt-1">Owner: {service.owner || 'Platform Team'}</div>
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}
