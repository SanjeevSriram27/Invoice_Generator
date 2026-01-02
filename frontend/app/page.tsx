'use client';

import { Suspense, lazy } from 'react';
import { useStore } from '@/lib/store';
import InvoiceTypeSelector from '@/components/InvoiceTypeSelector';
import type { InvoiceType, InvoiceItem } from '@/types/invoice';

// Lazy load heavy components
const InvoiceForm = lazy(() => import('@/components/InvoiceForm'));
const InvoiceSuccess = lazy(() => import('@/components/InvoiceSuccess'));

export default function Home() {
  // Use selectors to prevent unnecessary re-renders
  const step = useStore((state) => state.step);
  const invoiceType = useStore((state) => state.invoiceType);
  const items = useStore((state) => state.items);
  const generatedInvoice = useStore((state) => state.generatedInvoice);
  const setStep = useStore((state) => state.setStep);
  const setInvoiceType = useStore((state) => state.setInvoiceType);
  const setItems = useStore((state) => state.setItems);
  const addItem = useStore((state) => state.addItem);
  const setGeneratedInvoice = useStore((state) => state.setGeneratedInvoice);
  const reset = useStore((state) => state.reset);

  const handleSelectType = (type: InvoiceType) => {
    setInvoiceType(type);
    setStep(2);
  };

  const handleSubmit = async (formData: any) => {
    // Lazy load the API only when submitting the form
    const { invoiceApi } = await import('@/lib/api');

    const payload = {
      invoice_type: invoiceType,
      user_id: 'demo-user-123',
      ...formData,
      items: items,
    };

    const invoice = await invoiceApi.create(payload);
    setGeneratedInvoice(invoice);
    setStep(3);
  };

  const handleDownload = async (id: number) => {
    const { invoiceApi } = await import('@/lib/api');
    await invoiceApi.downloadPdf(id);
  };

  const handleShareWhatsApp = async (id: number, phone: string) => {
    const { invoiceApi } = await import('@/lib/api');
    return await invoiceApi.shareWhatsApp(id, phone);
  };

  const handleShareEmail = async (id: number, email: string) => {
    const { invoiceApi } = await import('@/lib/api');
    return await invoiceApi.shareEmail(id, email);
  };

  const handleRemoveItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index));
  };

  // Step 1: Select Invoice Type
  if (step === 1) {
    return <InvoiceTypeSelector onSelectType={handleSelectType} />;
  }

  // Step 2: Invoice Form
  if (step === 2 && invoiceType) {
    return (
      <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><div className="text-xl">Loading form...</div></div>}>
        <InvoiceForm
          invoiceType={invoiceType}
          items={items}
          onBack={reset}
          onAddItem={addItem}
          onRemoveItem={handleRemoveItem}
          onSubmit={handleSubmit}
        />
      </Suspense>
    );
  }

  // Step 3: Success
  if (step === 3 && generatedInvoice) {
    return (
      <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><div className="text-xl">Loading...</div></div>}>
        <InvoiceSuccess
          invoice={generatedInvoice}
          onReset={reset}
          onDownload={handleDownload}
          onShareWhatsApp={handleShareWhatsApp}
          onShareEmail={handleShareEmail}
        />
      </Suspense>
    );
  }

  return null;
}
