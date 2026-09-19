export function StatusPill({ value, tone = 'neutral' }: { value: string; tone?: 'success' | 'warning' | 'danger' | 'neutral' | 'info' }) {
  const palette = {
    success: 'bg-emerald-500/15 text-emerald-300 border border-emerald-400/30',
    warning: 'bg-amber-500/15 text-amber-300 border border-amber-400/30',
    danger: 'bg-red-500/15 text-red-300 border border-red-400/30',
    info: 'bg-sky-500/15 text-sky-300 border border-sky-400/30',
    neutral: 'bg-slate-500/15 text-slate-300 border border-slate-400/30',
  };

  return <span className={`badge ${palette[tone]}`}>{value}</span>;
}
