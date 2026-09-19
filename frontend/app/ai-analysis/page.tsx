"use client";

import { useEffect, useState } from 'react';
import { apiFetch } from '@/lib/api';
import type { AIAnalysis, Incident } from '@/types/dashboard';

type AnalysisResult = Incident & { analysis: AIAnalysis };

export default function AIAnalysisPage() {
  const [analysis, setAnalysis] = useState<AnalysisResult[]>([]);

  useEffect(() => {
    apiFetch<Incident[]>('/api/v1/incidents')
      .then(async (incidents) => {
        const results: AnalysisResult[] = [];
        for (const incident of incidents.slice(0, 2)) {
          try {
            const result = await apiFetch<AIAnalysis>(`/api/v1/incidents/${incident.id}/ai-analysis`, { method: 'POST' });
            results.push({ ...incident, analysis: result });
          } catch {
            results.push({ ...incident, analysis: { summary: 'Fallback reasoning available', suspected_root_cause: 'Dependency and latency pattern indicates likely service bottleneck.', confidence: 0 } });
          }
        }
        setAnalysis(results);
      })
      .catch((err) => console.error(err));
  }, []);

  return (
    <main className="flex-1 p-6 md:p-8">
      <div className="mb-6">
        <div className="text-xs uppercase tracking-[0.24em] text-sky-300/80">AI Analysis</div>
        <h1 className="text-3xl font-bold">Incident analysis</h1>
      </div>

      <div className="space-y-6">
        {analysis.map((item) => (
          <div key={item.id} className="card p-4">
            <h2 className="text-xl font-semibold">{item.title}</h2>
            <p className="mt-2 text-slate-300">{item.analysis?.summary || 'No summary available.'}</p>
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              <div className="rounded-xl bg-slate-900/50 p-3"><span className="font-semibold text-white">Suspected root cause:</span> {item.analysis?.suspected_root_cause || 'Pending'}</div>
              <div className="rounded-xl bg-slate-900/50 p-3"><span className="font-semibold text-white">Confidence:</span> {item.analysis?.confidence ?? 'n/a'}</div>
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}
