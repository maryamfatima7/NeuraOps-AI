"use client";

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { apiFetch } from '@/lib/api';
import { StatusPill } from '@/components/ui/StatusPill';
import type { Anomaly, IncidentDetail, LogEntry } from '@/types/dashboard';

export default function IncidentDetailPage() {
  const params = useParams();
  const [incident, setIncident] = useState<IncidentDetail | null>(null);

  useEffect(() => {
    if (!params?.id) return;
    apiFetch<IncidentDetail>(`/api/v1/incidents/${params.id}`)
      .then(setIncident)
      .catch((err) => console.error(err));
  }, [params?.id]);

  if (!incident) return <main className="flex-1 p-8">Loading incident…</main>;

  return (
    <main className="flex-1 p-6 md:p-8">
      <div className="mb-6 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
          <div className="text-xs uppercase tracking-[0.22em] text-sky-300/80">Incident detail</div>
          <h1 className="text-3xl font-bold">{incident.title}</h1>
        </div>
        <div className="flex gap-2">
          <StatusPill value={incident.severity} tone={incident.severity === 'CRITICAL' ? 'danger' : 'warning'} />
          <StatusPill value={incident.status} tone={incident.status === 'RESOLVED' ? 'success' : 'neutral'} />
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 space-y-6">
          <div className="card p-4">
            <h2 className="text-lg font-semibold mb-3">Investigation context</h2>
            <p className="text-slate-300">{incident.description}</p>
            <div className="mt-4 grid grid-cols-2 gap-3 text-sm text-slate-300">
              <div className="rounded-xl bg-slate-900/50 p-3"><div className="text-slate-400">Affected services</div><div className="mt-1">{incident.affected_services.join(', ')}</div></div>
              <div className="rounded-xl bg-slate-900/50 p-3"><div className="text-slate-400">Detection time</div><div className="mt-1">{new Date(incident.detected_time).toLocaleString()}</div></div>
            </div>
          </div>

          <div className="card p-4">
            <h2 className="text-lg font-semibold mb-3">AI Incident Summary</h2>
            <p className="text-slate-300">{incident.ai_summary || 'No AI summary yet. Trigger analysis to generate structured findings.'}</p>
          </div>

          <div className="card p-4">
            <h2 className="text-lg font-semibold mb-3">AI analysis</h2>
            <div className="space-y-3 text-sm text-slate-300">
              <div><span className="font-semibold text-white">Suspected root cause:</span> {incident.root_cause || 'Not yet available'}</div>
              <div><span className="font-semibold text-white">Confidence:</span> {incident.ai_summary ? 'High' : 'Pending'}</div>
              <div><span className="font-semibold text-white">Recommended actions:</span> {incident.recommendations || 'Not yet generated'}</div>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="card p-4">
            <h2 className="text-lg font-semibold mb-3">Related anomalies</h2>
            <div className="space-y-3">
              {incident.anomalies?.length ? incident.anomalies.map((a: Anomaly, idx: number) => (
                <div key={idx} className="rounded-xl bg-slate-900/50 p-3 text-sm">
                  <div className="font-medium">{a.metric}</div>
                  <div className="text-slate-400">Observed {a.observed_value} vs baseline {a.expected_baseline}</div>
                </div>
              )) : <div className="text-slate-400 text-sm">No anomaly references linked.</div>}
            </div>
          </div>

          <div className="card p-4">
            <h2 className="text-lg font-semibold mb-3">Recent logs</h2>
            <div className="space-y-2 text-sm text-slate-300">
              {incident.related_logs?.length ? incident.related_logs.slice(0, 8).map((log: LogEntry, idx: number) => (
                <div key={idx} className="rounded-xl bg-slate-900/50 p-2">{log.message || log.summary || JSON.stringify(log)}</div>
              )) : <div className="text-slate-400">No logs linked.</div>}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
