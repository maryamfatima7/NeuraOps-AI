import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { AuthGate } from '@/components/layout/AuthGate';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'NeuraOps AI',
  description: 'Intelligent AI Observability & Autonomous Incident Analysis Platform',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthGate>{children}</AuthGate>
      </body>
    </html>
  );
}
