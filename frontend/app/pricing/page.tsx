import Link from 'next/link';
import { Check, Lock, Sparkles, Star } from 'lucide-react';

const plans = [
  {
    name: 'FREE',
    price: '$0',
    description: 'For small teams validating AI-first observability workflows.',
    features: ['Dashboard access', 'Basic logs & metrics', 'Up to 2 services', '3 AI analyses/day'],
    cta: 'Current plan',
    highlight: false,
  },
  {
    name: 'PRO',
    price: '$29',
    description: 'For modern ops teams that need AI RCA, alerts, and scalable visibility.',
    features: ['Unlimited services', 'Unlimited logs & incidents', 'Advanced AI RCA', 'Extended alerting & exports'],
    cta: 'Upgrade to Pro',
    highlight: true,
  },
];

export default function PricingPage() {
  return (
    <main className="flex-1 p-6 md:p-8">
      <div className="mb-8">
        <div className="text-xs uppercase tracking-[0.24em] text-sky-300/80">Pricing</div>
        <h1 className="text-3xl font-bold">AI operations subscriptions</h1>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {plans.map((plan) => (
          <div
            key={plan.name}
            className={`rounded-2xl border p-6 ${plan.highlight ? 'border-sky-400/40 bg-sky-500/5 shadow-xl shadow-sky-500/10' : 'border-slate-700 bg-slate-900/70'}`}
          >
            <div className="mb-5 flex items-center justify-between">
              <div>
                <div className="text-sm uppercase tracking-[0.22em] text-slate-400">{plan.name}</div>
                <div className="mt-3 text-4xl font-bold">{plan.price}<span className="text-base text-slate-400">/mo</span></div>
              </div>
              {plan.highlight ? <Star className="text-sky-300" /> : <Lock className="text-slate-400" />}
            </div>

            <p className="mb-5 text-sm text-slate-300">{plan.description}</p>

            <ul className="space-y-3">
              {plan.features.map((feature) => (
                <li key={feature} className="flex items-center gap-3 text-sm text-slate-200">
                  <span className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500/15 text-emerald-300">
                    <Check size={12} />
                  </span>
                  {feature}
                </li>
              ))}
            </ul>

            <Link
              href={plan.highlight ? '/settings' : '/register'}
              className={`mt-6 inline-flex w-full items-center justify-center rounded-xl px-4 py-3 font-semibold transition ${plan.highlight ? 'bg-sky-500 text-slate-950 hover:bg-sky-400' : 'border border-slate-700 bg-slate-950/60 text-slate-100 hover:border-slate-500'}`}
            >
              {plan.cta}
            </Link>
          </div>
        ))}
      </div>

      <div className="mt-8 rounded-2xl border border-slate-700 bg-slate-900/60 p-5">
        <div className="mb-2 flex items-center gap-2 text-sky-300">
          <Sparkles size={16} />
          <span className="text-sm font-medium">Why teams upgrade</span>
        </div>
        <p className="text-sm text-slate-300">
          PRO unlocks advanced AI RCA, full-service coverage, extended retention, and enterprise-ready alerting across distributed systems.
        </p>
      </div>
    </main>
  );
}
