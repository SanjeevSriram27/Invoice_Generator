import { create } from 'zustand';
import type { InvoiceType, InvoiceItem, Invoice } from '@/types/invoice';

interface InvoiceState {
  step: number;
  invoiceType: InvoiceType | null;
  items: InvoiceItem[];
  generatedInvoice: Invoice | null;
  setStep: (step: number) => void;
  setInvoiceType: (type: InvoiceType) => void;
  setItems: (items: InvoiceItem[]) => void;
  addItem: (item: InvoiceItem) => void;
  setGeneratedInvoice: (invoice: Invoice | null) => void;
  reset: () => void;
}

export const useStore = create<InvoiceState>((set) => ({
  step: 1,
  invoiceType: null,
  items: [],
  generatedInvoice: null,
  setStep: (step) => set({ step }),
  setInvoiceType: (type) => set({ invoiceType: type }),
  setItems: (items) => set({ items }),
  addItem: (item) => set((state) => ({ items: [...state.items, item] })),
  setGeneratedInvoice: (invoice) => set({ generatedInvoice: invoice }),
  reset: () => set({ step: 1, invoiceType: null, items: [], generatedInvoice: null }),
}));
