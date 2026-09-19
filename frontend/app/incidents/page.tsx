"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { apiFetch } from '@/lib/api';
import { StatusPill } from '@/components/ui/StatusPill';
import type { Incident } from '@/types/dashboard';

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);

  useEffect(() => {
    apiFetch<Incident[]>('/api/v1/incidents')
      .then(setIncidents)
      .catch((err) => console.error(err));
  }, []);

  return (
    <main className="flex-1 p-6 md:p-8">
      <div className="mb-6">
        <div className="text-xs uppercase tracking-[0.24em] text-sky-300/80">Incident management</div>
        <h1 className="text-3xl font-bold">Incidents</h1>
      </div>

      <div className="space-y-4">
        {incidents.map((incident) => (
          <div key={incident.id} className="card p-4">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
              <div>
                <div className="text-xs uppercase tracking-[0.2em] text-slate-400">#{incident.id}</div>
                <h2 className="text-xl font-semibold">{incident.title}</h2>
              </div>
              <div className="flex gap-2">
                <StatusPill value={incident.severity} tone={incident.severity === 'CRITICAL' ? 'danger' : incident.severity === 'HIGH' ? 'warning' : 'info'} />
                <StatusPill value={incident.status} tone={incident.status === 'RESOLVED' ? 'success' : incident.status === 'INVESTIGATING' ? 'warning' : 'neutral'} />
              </div>
            </div>
            <p className="mt-3 text-slate-300">{incident.description}</p>
            <div className="mt-4 flex flex-wrap gap-3 text-sm text-slate-400">
              <span>Affected: {incident.affected_services}</span>
              <span>Detected: {new Date(incident.detected_time).toLocaleString()}</span>
            </div>
            <div className="mt-4">
              <Link href={`/incidents/${incident.id}`} className="text-sky-300 hover:text-sky-200 font-medium">
                Open investigation →
              </Link>
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}
