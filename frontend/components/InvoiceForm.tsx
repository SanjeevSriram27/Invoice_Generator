'use client';

import { useState, useCallback } from 'react';
import { INDIAN_STATES, type InvoiceType, type InvoiceItem } from '@/types/invoice';
import AddItemForm from './AddItemForm';

interface InvoiceFormProps {
  invoiceType: InvoiceType;
  items: InvoiceItem[];
  onBack: () => void;
  onAddItem: (item: InvoiceItem) => void;
  onRemoveItem: (index: number) => void;
  onSubmit: (formData: any) => Promise<void>;
}

export default function InvoiceForm({
  invoiceType,
  items,
  onBack,
  onAddItem,
  onRemoveItem,
  onSubmit
}: InvoiceFormProps) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<any>({});

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();

    if (items.length === 0) {
      alert('Please add at least one item');
      return;
    }

    setLoading(true);
    try {
      await onSubmit(formData);
    } catch (error: any) {
      let errorMessage = error.response?.data?.error || error.message;

      if (error.response?.data?.items) {
        const hsnError = error.response.data.items[0]?.hsn_sac;
        if (hsnError && hsnError[0]?.includes('no more than')) {
          errorMessage = 'HSN/SAC Code is too long. Please enter a code with maximum 15 characters.';
        }
      }

      alert('Error: ' + errorMessage);
    } finally {
      setLoading(false);
    }
  }, [formData, items, onSubmit]);

  const updateField = useCallback((field: string, value: any) => {
    setFormData((prev: any) => ({ ...prev, [field]: value }));
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10 shadow-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button onClick={onBack} className="text-gray-600 hover:text-gray-900 flex items-center">
              <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back
            </button>
            <div className="h-8 w-px bg-gray-300"></div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Create Invoice</h1>
              <p className="text-sm text-gray-500">
                {invoiceType === 'topmate' ? 'Topmate Invoice' : 'Personal Invoice'}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <div className="badge-blue px-3 py-1">
              {items.length} items
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Seller (for user invoices) */}
          {invoiceType === 'user' && (
            <div className="section-card">
              <div className="flex items-center mb-5">
                <div className="icon-container-sm bg-blue-100 mr-3">
                  <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                </div>
                <div>
                  <h2 className="text-lg font-bold text-gray-900">Your Business Details</h2>
                  <p className="text-sm text-gray-500">Information about your company</p>
                </div>
              </div>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Business Name *</label>
                  <input required placeholder="Your Company Pvt Ltd" className="form-input"
                    onChange={(e) => updateField('seller_name', e.target.value)} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">GSTIN *</label>
                  <input required placeholder="29ABCDE1234F1Z5" maxLength={15} className="form-input uppercase"
                    onChange={(e) => updateField('seller_gstin', e.target.value.toUpperCase())} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">State *</label>
                  <select required className="form-input"
                    onChange={(e) => updateField('seller_state', e.target.value)}>
                    <option value="">Select State</option>
                    {INDIAN_STATES.map(s => <option key={s.code} value={s.code}>{s.name}</option>)}
                  </select>
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Address *</label>
                  <input required placeholder="Street, City" className="form-input"
                    onChange={(e) => updateField('seller_address', e.target.value)} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Pincode *</label>
                  <input required placeholder="400001" maxLength={6} className="form-input"
                    onChange={(e) => updateField('seller_pincode', e.target.value)} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">GST Rate (%) *</label>
                  <select required className="form-input"
                    onChange={(e) => updateField('gst_rate', parseFloat(e.target.value))}
                    defaultValue="18">
                    <option value="0">0% - Exempt</option>
                    <option value="5">5% - Essential Goods/Services</option>
                    <option value="12">12% - Standard Rate</option>
                    <option value="18">18% - Standard Rate (Default)</option>
                    <option value="28">28% - Luxury Goods</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Buyer */}
          <div className="section-card">
            <div className="flex items-center mb-5">
              <div className="icon-container-sm bg-green-100 mr-3">
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div>
                <h2 className="text-lg font-bold text-gray-900">Client Details</h2>
                <p className="text-sm text-gray-500">Who are you billing?</p>
              </div>
            </div>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Client Name *</label>
                <input required placeholder="Client Company Name" className="form-input"
                  onChange={(e) => updateField('buyer_name', e.target.value)} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Client GSTIN <span className="text-gray-400">(Optional)</span></label>
                <input placeholder="29ABCDE1234F1Z5" maxLength={15} className="form-input uppercase"
                  onChange={(e) => updateField('buyer_gstin', e.target.value.toUpperCase())} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">State *</label>
                <select required className="form-input"
                  onChange={(e) => updateField('buyer_state', e.target.value)}>
                  <option value="">Select State</option>
                  {INDIAN_STATES.map(s => <option key={s.code} value={s.code}>{s.name}</option>)}
                </select>
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Address *</label>
                <input required placeholder="Street, City" className="form-input"
                  onChange={(e) => updateField('buyer_address', e.target.value)} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Pincode *</label>
                <input required placeholder="400001" maxLength={6} className="form-input"
                  onChange={(e) => updateField('buyer_pincode', e.target.value)} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone <span className="text-gray-400">(Optional)</span></label>
                <input type="tel" placeholder="+91 9876543210" maxLength={15} className="form-input"
                  onChange={(e) => updateField('buyer_phone', e.target.value)} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email <span className="text-gray-400">(Optional)</span></label>
                <input type="email" placeholder="client@example.com" className="form-input"
                  onChange={(e) => updateField('buyer_email', e.target.value)} />
              </div>
            </div>
          </div>

          {/* Items */}
          <div className="section-card">
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center">
                <div className="icon-container-sm bg-purple-100 mr-3">
                  <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <div>
                  <h2 className="text-lg font-bold text-gray-900">Invoice Items</h2>
                  <p className="text-sm text-gray-500">Add products or services</p>
                </div>
              </div>
            </div>

            {/* Display Items */}
            {items.length > 0 && (
              <div className="mb-5 space-y-3">
                {items.map((item, idx) => (
                  <div key={idx} className="item-card">
                    <div className="flex-1">
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-semibold text-gray-900">{item.description}</p>
                          <p className="text-sm text-gray-500 mt-1">
                            HSN: {item.hsn_sac} • Qty: {item.quantity} × ₹{item.unit_price.toFixed(2)}
                          </p>
                        </div>
                        <div className="text-right ml-4">
                          <p className="text-lg font-bold text-gray-900">₹{(item.quantity * item.unit_price).toFixed(2)}</p>
                        </div>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => onRemoveItem(idx)}
                      className="ml-4 text-red-500 hover:text-red-700 hover:bg-red-50 p-2 rounded-lg transition-colors"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            )}

            <AddItemForm onAdd={onAddItem} />
          </div>

          {/* Notes */}
          <div className="section-card">
            <label className="block text-sm font-medium text-gray-700 mb-2">Notes / Terms & Conditions <span className="text-gray-400">(Optional)</span></label>
            <textarea
              placeholder="Payment due within 30 days..."
              rows={3}
              className="form-input"
              onChange={(e) => updateField('notes', e.target.value)}
            />
          </div>

          {/* Submit */}
          <div className="sticky bottom-0 bg-white border-t border-gray-200 -mx-4 px-4 py-4 shadow-lg">
            <button
              type="submit"
              disabled={loading || items.length === 0}
              className="w-full btn-primary disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:shadow-none"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Generating Invoice...
                </span>
              ) : (
                `Generate Invoice (${items.length} ${items.length === 1 ? 'item' : 'items'})`
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
