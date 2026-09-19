"use client";

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Activity, AlertTriangle, Bell, Database, Gauge, LogOut, Server, ShieldCheck, Sparkles, Wrench } from 'lucide-react';
import { clearAuthToken } from '@/lib/auth';

const navItems = [
  { label: 'Overview', href: '/', icon: Activity },
  { label: 'Services', href: '/services', icon: Server },
  { label: 'Incidents', href: '/incidents', icon: AlertTriangle },
  { label: 'Logs', href: '/logs', icon: LogOut },
  { label: 'Metrics', href: '/metrics', icon: Gauge },
  { label: 'AI Analysis', href: '/ai-analysis', icon: Sparkles },
  { label: 'Alerts', href: '/alerts', icon: Bell },
  { label: 'System Health', href: '/health', icon: ShieldCheck },
  { label: 'Settings', href: '/settings', icon: Wrench },
  { label: 'Plans', href: '/pricing', icon: Sparkles },
];

export function Sidebar() {
  const router = useRouter();

  function handleLogout() {
    clearAuthToken();
    router.replace('/login');
  }

  return (
    <aside className="w-full max-w-[260px] bg-slate-950/60 border-r border-slate-800 p-5">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-9 h-9 rounded-lg bg-sky-500/20 border border-sky-400/40 flex items-center justify-center text-sky-300">
            <Database size={18} />
          </div>
          <div>
            <div className="text-xs uppercase tracking-[0.22em] text-sky-300/80">NeuraOps</div>
            <div className="font-bold text-lg">AI</div>
          </div>
        </div>
      </div>

      <nav className="space-y-2">
        {navItems.map(({ label, href, icon: Icon }) => (
          <Link
            key={label}
            href={href}
            className="flex items-center gap-3 rounded-xl px-3 py-2 text-slate-200 hover:bg-slate-800/80 transition"
          >
            <Icon size={16} className="text-sky-300" />
            <span>{label}</span>
          </Link>
        ))}
      </nav>

      <button onClick={handleLogout} className="mt-8 flex w-full items-center gap-3 rounded-xl px-3 py-2 text-slate-400 transition hover:bg-red-500/10 hover:text-red-200">
        <LogOut size={16} />
        <span>Sign out</span>
      </button>
    </aside>
  );
}
