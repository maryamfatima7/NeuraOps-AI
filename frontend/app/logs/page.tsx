"use client";

import { useEffect, useState } from 'react';
import { apiFetch } from '@/lib/api';
import type { LogEntry } from '@/types/dashboard';

export default function LogsPage() {
  const [logs, setLogs] = useState<LogEntry[]>([]);

  useEffect(() => {
    apiFetch<LogEntry[]>('/api/v1/logs')
      .then(setLogs)
      .catch((err) => console.error(err));
  }, []);

  return (
    <main className="flex-1 p-6 md:p-8">
      <div className="mb-6">
        <div className="text-xs uppercase tracking-[0.24em] text-sky-300/80">Log management</div>
        <h1 className="text-3xl font-bold">Logs</h1>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-900/80 text-slate-300">
            <tr>
              <th className="p-3">Service</th>
              <th className="p-3">Level</th>
              <th className="p-3">Message</th>
              <th className="p-3">Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id} className="border-t border-slate-800">
                <td className="p-3">{log.service}</td>
                <td className="p-3">{log.level}</td>
                <td className="p-3 max-w-[500px] break-words">{log.message}</td>
                <td className="p-3">{new Date(log.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}
