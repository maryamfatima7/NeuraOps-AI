"use client";

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FormEvent, useState } from 'react';
import { CheckCircle2, Eye, EyeOff, Lock, Mail, UserRound } from 'lucide-react';
import { setAuthToken } from '@/lib/auth';
import { API_BASE_URL } from '@/lib/config';

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ full_name: '', email: '', password: '', confirm_password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.detail?.message || data?.detail || 'Registration failed');
      }

      const loginResponse = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username: form.email, password: form.password }),
      });

      const loginData = await loginResponse.json();
      if (!loginResponse.ok) {
        throw new Error(loginData?.detail?.message || loginData?.detail || 'Account created but login failed');
      }

      setAuthToken(loginData.access_token);
      router.push('/');
      router.refresh();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : 'Registration failed');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 px-4 py-12">
      <div className="w-full max-w-lg rounded-2xl border border-slate-700 bg-slate-900/80 p-6 shadow-2xl shadow-violet-500/10">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-violet-400/30 bg-violet-500/10 text-violet-300">
            <CheckCircle2 size={22} />
          </div>
          <div>
            <div className="text-xs uppercase tracking-[0.22em] text-violet-300/80">Start free</div>
            <h1 className="text-2xl font-bold">Create your account</h1>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-2 block text-sm text-slate-300">Full name</label>
            <div className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-950/60 px-3 py-2">
              <UserRound size={16} className="text-slate-400" />
              <input
                type="text"
                value={form.full_name}
                onChange={(e) => setForm((current) => ({ ...current, full_name: e.target.value }))}
                className="w-full bg-transparent text-slate-100 outline-none"
                placeholder="Alex Morgan"
                required
              />
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm text-slate-300">Work email</label>
            <div className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-950/60 px-3 py-2">
              <Mail size={16} className="text-slate-400" />
              <input
                type="email"
                value={form.email}
                onChange={(e) => setForm((current) => ({ ...current, email: e.target.value }))}
                className="w-full bg-transparent text-slate-100 outline-none"
                placeholder="team@company.com"
                required
              />
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm text-slate-300">Password</label>
            <div className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-950/60 px-3 py-2">
              <Lock size={16} className="text-slate-400" />
              <input
                type={showPassword ? 'text' : 'password'}
                value={form.password}
                onChange={(e) => setForm((current) => ({ ...current, password: e.target.value }))}
                className="w-full bg-transparent text-slate-100 outline-none"
                placeholder="At least 8 characters"
                required
              />
              <button type="button" onClick={() => setShowPassword((current) => !current)} className="text-slate-400 hover:text-slate-200">
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm text-slate-300">Confirm password</label>
            <div className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-950/60 px-3 py-2">
              <Lock size={16} className="text-slate-400" />
              <input
                type={showPassword ? 'text' : 'password'}
                value={form.confirm_password}
                onChange={(e) => setForm((current) => ({ ...current, confirm_password: e.target.value }))}
                className="w-full bg-transparent text-slate-100 outline-none"
                placeholder="Repeat your password"
                required
              />
            </div>
          </div>

          {error ? <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-200">{error}</div> : null}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-xl bg-violet-500 px-4 py-2.5 font-semibold text-white transition hover:bg-violet-400 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSubmitting ? 'Creating account…' : 'Create account'}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-slate-400">
          Already have an account?{' '}
          <Link href="/login" className="font-medium text-violet-300 hover:text-violet-200">
            Sign in
          </Link>
        </div>
      </div>
    </main>
  );
}
