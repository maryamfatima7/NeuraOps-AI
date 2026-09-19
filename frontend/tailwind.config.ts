import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{js,ts,jsx,tsx,mdx}', './components/**/*.{js,ts,jsx,tsx,mdx}', './lib/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        bg: '#07111f',
        panel: '#0f1d2b',
        accent: '#4cc9f0',
        success: '#22c55e',
        warning: '#f59e0b',
        danger: '#ef4444',
        purple: '#8b5cf6',
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(76,201,240,0.2), 0 18px 40px rgba(6,10,20,0.45)',
      },
    },
  },
  plugins: [],
};

export default config;
