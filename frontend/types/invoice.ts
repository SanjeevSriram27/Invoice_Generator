// TypeScript types for Invoice Generator
export type InvoiceType = 'topmate' | 'user';

export interface InvoiceItem {
  description: string;
  hsn_sac: string;
  quantity: number;
  unit_price: number;
  amount?: number;
}

export interface Party {
  name: string;
  gstin?: string;
  address: string;
  pincode: string;
  state: string;
  phone?: string;
  email?: string;
}

export interface Invoice {
  id?: number;
  invoice_number?: string;
  invoice_type: InvoiceType;
  user_id: string;
  seller_name: string;
  seller_gstin: string;
  seller_address: string;
  seller_pincode: string;
  seller_state: string;
  seller_phone?: string;
  seller_email?: string;
  buyer_name: string;
  buyer_gstin?: string;
  buyer_address: string;
  buyer_pincode: string;
  buyer_state: string;
  buyer_phone?: string;
  buyer_email?: string;
  items: InvoiceItem[];
  subtotal?: number;
  cgst?: number;
  sgst?: number;
  igst?: number;
  total?: number;
  gst_rate?: number;
  notes?: string;
  pdf_url?: string;
}

export const INDIAN_STATES = [
  { code: 'MH', name: 'Maharashtra' },
  { code: 'KA', name: 'Karnataka' },
  { code: 'DL', name: 'Delhi' },
  { code: 'TN', name: 'Tamil Nadu' },
  { code: 'UP', name: 'Uttar Pradesh' },
  { code: 'GJ', name: 'Gujarat' },
  { code: 'RJ', name: 'Rajasthan' },
  { code: 'WB', name: 'West Bengal' },
  { code: 'AP', name: 'Andhra Pradesh' },
  { code: 'TS', name: 'Telangana' },
  { code: 'HR', name: 'Haryana' },
  { code: 'PB', name: 'Punjab' },
  { code: 'BR', name: 'Bihar' },
  { code: 'OR', name: 'Odisha' },
  { code: 'KL', name: 'Kerala' },
];
