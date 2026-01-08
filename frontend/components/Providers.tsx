'use client';

import ThemeToggle from './ThemeToggle';
import ToastProvider from './ToastProvider';

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <>
      {children}
      <ThemeToggle />
      <ToastProvider />
    </>
  );
}
