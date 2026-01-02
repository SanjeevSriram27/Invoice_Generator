'use client';

import { useState, useCallback } from 'react';
import type { Invoice } from '@/types/invoice';

interface InvoiceSuccessProps {
  invoice: Invoice;
  onReset: () => void;
  onDownload: (id: number) => Promise<void>;
  onShareWhatsApp: (id: number, phone: string) => Promise<any>;
  onShareEmail: (id: number, email: string) => Promise<any>;
}

export default function InvoiceSuccess({
  invoice,
  onReset,
  onDownload,
  onShareWhatsApp,
  onShareEmail
}: InvoiceSuccessProps) {
  const [loading, setLoading] = useState(false);

  const handleDownload = useCallback(async () => {
    try {
      setLoading(true);
      await onDownload(invoice.id!);
    } finally {
      setLoading(false);
    }
  }, [invoice.id, onDownload]);

  const handleWhatsApp = useCallback(async () => {
    let phone = invoice.buyer_phone;
    if (!phone) {
      phone = prompt('Enter WhatsApp number (with country code, e.g., 919876543210):');
    }
    if (phone) {
      try {
        setLoading(true);
        const response = await onShareWhatsApp(invoice.id!, phone);

        if (response.whatsapp_sid) {
          alert('✓ Invoice PDF sent directly to WhatsApp!');
        } else if (response.whatsapp_link) {
          window.open(response.whatsapp_link, '_blank');
          alert(response.note || 'WhatsApp opened with invoice details');
        }
      } catch (error: any) {
        alert(error.response?.data?.error || 'Failed to share via WhatsApp');
      } finally {
        setLoading(false);
      }
    }
  }, [invoice, onShareWhatsApp]);

  const handleEmail = useCallback(async () => {
    let email = invoice.buyer_email;
    if (!email) {
      email = prompt('Enter email address:');
    }
    if (email) {
      try {
        setLoading(true);
        await onShareEmail(invoice.id!, email);
        alert(`✓ Invoice PDF sent successfully to ${email}!`);
      } catch (error: any) {
        alert(error.response?.data?.error || 'Failed to send email');
      } finally {
        setLoading(false);
      }
    }
  }, [invoice, onShareEmail]);

  const totalGST = (
    parseFloat(String(invoice.cgst || '0')) +
    parseFloat(String(invoice.sgst || '0')) +
    parseFloat(String(invoice.igst || '0'))
  ).toFixed(2);

  return (
    <div className="bg-gradient-success flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        <div className="bg-white rounded-3xl shadow-2xl p-10">
          <div className="text-center mb-8">
            <div className="w-24 h-24 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-6 shadow-xl">
              <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-3">Invoice Generated!</h1>
            <p className="text-xl text-gray-600">Your invoice is ready to download</p>
          </div>

          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-6 mb-8 border border-blue-100">
            <div className="flex items-center justify-between mb-4 pb-4 border-b border-blue-200">
              <span className="text-gray-600 font-medium">Invoice Number</span>
              <span className="text-xl font-bold text-blue-600">{invoice.invoice_number}</span>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Buyer</span>
                <span className="font-semibold text-gray-900">{invoice.buyer_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Subtotal</span>
                <span className="font-semibold">₹{invoice.subtotal}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">GST</span>
                <span className="font-semibold">₹{totalGST}</span>
              </div>
              <div className="flex justify-between text-2xl font-bold border-t border-blue-200 pt-3">
                <span className="text-gray-900">Total</span>
                <span className="text-green-600">₹{invoice.total}</span>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <button
              onClick={handleDownload}
              disabled={loading}
              className="w-full btn-primary flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Download PDF Invoice
            </button>

            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={handleWhatsApp}
                disabled={loading}
                className="bg-green-500 text-white py-3 rounded-xl font-semibold hover:bg-green-600 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                </svg>
                {loading ? 'Sending...' : 'WhatsApp'}
              </button>

              <button
                onClick={handleEmail}
                disabled={loading}
                className="bg-blue-500 text-white py-3 rounded-xl font-semibold hover:bg-blue-600 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                {loading ? 'Sending...' : 'Email'}
              </button>
            </div>

            <button
              onClick={onReset}
              className="w-full btn-secondary"
            >
              Create Another Invoice
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
