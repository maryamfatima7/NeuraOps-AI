"use client";

import { useEffect, useState } from 'react';
import { AlertTriangle, ArrowUpRight, Bell, BrainCircuit, Clock3, Gauge, ShieldCheck, TrendingUp } from 'lucide-react';
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { StatusPill } from '@/components/ui/StatusPill';
import { apiFetch } from '@/lib/api';
import type { HealthSummary } from '@/types/dashboard';

const overviewData = [
  { name: 'Mon', latency: 240, errors: 0.8 },
  { name: 'Tue', latency: 290, errors: 1.1 },
  { name: 'Wed', latency: 520, errors: 2.4 },
  { name: 'Thu', latency: 380, errors: 1.7 },
  { name: 'Fri', latency: 430, errors: 1.9 },
  { name: 'Sat', latency: 310, errors: 1.2 },
  { name: 'Sun', latency: 255, errors: 0.9 },
];

export default function HomePage() {
  const [summary, setSummary] = useState<HealthSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch<HealthSummary>('/api/v1/dashboard/summary');
        setSummary(data);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  const stats = summary ? [
    { label: 'Overall system health', value: summary.overall_health.toUpperCase(), tone: 'success', icon: ShieldCheck },
    { label: 'Active incidents', value: String(summary.active_incidents), tone: 'warning', icon: AlertTriangle },
    { label: 'Error rate', value: `${summary.error_rate}%`, tone: 'danger', icon: Bell },
    { label: 'Avg latency', value: `${summary.average_latency} ms`, tone: 'info', icon: Gauge },
    { label: 'Req / min', value: `${summary.requests_per_minute}`, tone: 'success', icon: TrendingUp },
    { label: 'Services monitored', value: String(summary.services_monitored), tone: 'neutral', icon: ArrowUpRight },
  ] : [];

  return (
    <main className="flex-1 p-6 md:p-8">
      <div className="mb-6 flex items-center justify-between gap-4">
        <div>
          <div className="text-xs uppercase tracking-[0.28em] text-sky-300/80">Operations overview</div>
          <h1 className="text-3xl font-bold">Telemetry → Detection → Investigation → AI Analysis</h1>
        </div>
        <div className="card px-4 py-2 text-sm text-slate-200">
          <span className="text-slate-400">Last updated:</span> 2m ago
        </div>
      </div>

      {loading ? <div className="text-slate-300">Loading dashboard…</div> : (
        <>
          <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 mb-6">
            {stats.map(({ label, value, tone, icon: Icon }) => (
              <div key={label} className="card p-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="text-sm text-slate-400">{label}</div>
                  <Icon className="text-sky-300" size={18} />
                </div>
                <div className="flex items-center justify-between gap-3">
                  <div className="text-2xl font-bold">{value}</div>
                  <StatusPill value={tone === 'success' ? 'Healthy' : tone === 'warning' ? 'Watch' : tone === 'danger' ? 'Critical' : 'Stable'} tone={tone as 'success' | 'warning' | 'danger' | 'neutral' | 'info'} />
                </div>
              </div>
            ))}
          </section>

          <section className="grid grid-cols-1 xl:grid-cols-3 gap-6 mb-6">
            <div className="card p-4 xl:col-span-2">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-lg font-semibold">Latency & error trends</h2>
                <StatusPill value="Live" tone="info" />
              </div>
              <ResponsiveContainer width="100%" height={250}>
                <AreaChart data={overviewData}>
                  <CartesianGrid vertical={false} stroke="#334155" />
                  <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                  <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
                  <Tooltip />
                  <Area type="monotone" dataKey="latency" stroke="#4cc9f0" fill="#4cc9f0" fillOpacity={0.15} />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div className="card p-4">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-lg font-semibold">Recent alerts</h2>
                <Bell className="text-sky-300" size={18} />
              </div>
              <div className="space-y-3">
                {summary?.recent_alerts.slice(0, 4).map((alert, idx) => (
                  <div key={`${alert.rule}-${idx}`} className="rounded-xl border border-slate-700 bg-slate-900/50 p-3">
                    <div className="flex items-center justify-between gap-2">
                      <div className="font-medium text-sm">{alert.rule}</div>
                      <StatusPill value={alert.severity} tone={alert.severity === 'CRITICAL' ? 'danger' : alert.severity === 'HIGH' ? 'warning' : 'info'} />
                    </div>
                    <div className="mt-2 text-xs text-slate-400">{alert.service}</div>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <section className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            <div className="card p-4">
              <div className="mb-4 flex items-center gap-2">
                <BrainCircuit className="text-violet-300" size={18} />
                <h2 className="text-lg font-semibold">AI-detected anomalies</h2>
              </div>
              <div className="space-y-3">
                {summary?.ai_detected_anomalies.slice(0, 5).map((item, idx) => (
                  <div key={`${item.metric}-${idx}`} className="flex items-center justify-between rounded-xl bg-slate-900/50 px-3 py-2 border border-slate-700">
                    <div>
                      <div className="font-medium">{item.metric}</div>
                      <div className="text-xs text-slate-400">{item.service}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold text-sky-300">{item.deviation.toFixed(1)}</div>
                      <div className="text-xs text-slate-400">deviation</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="card p-4">
              <div className="mb-4 flex items-center gap-2">
                <Clock3 className="text-amber-300" size={18} />
                <h2 className="text-lg font-semibold">Recent incidents</h2>
              </div>
              <div className="space-y-3">
                {summary?.recent_incidents.slice(0, 5).map((incident) => (
                  <div key={incident.id} className="rounded-xl bg-slate-900/50 border border-slate-700 p-3">
                    <div className="flex items-center justify-between gap-2">
                      <div className="font-medium">#{incident.id} {incident.title}</div>
                      <StatusPill value={incident.severity} tone={incident.severity === 'CRITICAL' ? 'danger' : 'warning'} />
                    </div>
                    <div className="mt-2 flex items-center justify-between text-xs text-slate-400">
                      <span>{incident.status}</span>
                      <span>{new Date(incident.detected_time).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>
        </>
      )}
    </main>
  );
}
