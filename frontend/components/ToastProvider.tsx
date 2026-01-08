'use client';

import { memo } from 'react';
import { Toaster } from 'react-hot-toast';

const toastOptions = {
  duration: 4000,
  style: {
    background: '#fff',
    color: '#363636',
    padding: '16px',
    borderRadius: '12px',
    fontSize: '14px',
    boxShadow: '0 10px 40px rgba(0, 0, 0, 0.1)',
  },
  success: {
    duration: 3000,
    iconTheme: {
      primary: '#10b981',
      secondary: '#fff',
    },
  },
  error: {
    duration: 5000,
    iconTheme: {
      primary: '#ef4444',
      secondary: '#fff',
    },
  },
};

function ToastProvider() {
  return (
    <Toaster
      position="top-center"
      reverseOrder={false}
      toastOptions={toastOptions}
    />
  );
}

export default memo(ToastProvider);
