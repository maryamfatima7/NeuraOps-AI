"use client";

import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { fetchCurrentUser } from '@/lib/auth';
import { Sidebar } from '@/components/layout/Sidebar';

const publicRoutes = ['/login', '/register'];

export function AuthGate({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    let mounted = true;

    async function checkSession() {
      const user = await fetchCurrentUser();
      if (!user && !publicRoutes.includes(pathname)) {
        router.replace('/login');
        return;
      }
      if (user && publicRoutes.includes(pathname)) {
        router.replace('/');
        return;
      }
      if (mounted) {
        setChecking(false);
      }
    }

    checkSession();
    return () => {
      mounted = false;
    };
  }, [pathname, router]);

  if (checking && !publicRoutes.includes(pathname)) {
    return <div className="flex min-h-screen items-center justify-center bg-slate-950 text-slate-300">Checking session…</div>;
  }

  if (publicRoutes.includes(pathname)) {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex">
      <Sidebar />
      <div className="flex-1">{children}</div>
    </div>
  );
}
