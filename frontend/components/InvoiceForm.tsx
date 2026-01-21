'use client';

import { useState, useCallback, useEffect } from 'react';
import toast from 'react-hot-toast';
import { INDIAN_STATES, type InvoiceType, type InvoiceItem } from '@/types/invoice';
import AddItemForm from './AddItemForm';
import ErrorMessage from './ErrorMessage';
import { saveSellerDetails, loadSellerDetails, clearSellerDetails, hasSellerDetails } from '@/lib/localStorage';
import { validateGSTIN, validatePincode, validateEmail, validatePhone } from '@/lib/validation';

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
  const [saveDetails, setSaveDetails] = useState(false);
  const [hasSavedDetails, setHasSavedDetails] = useState(false);
  const [errors, setErrors] = useState<Record<string, string | null>>({});

  // Load saved seller details on mount (only for user invoices)
  useEffect(() => {
    if (invoiceType === 'user') {
      const saved = loadSellerDetails();
      if (saved) {
        setFormData(saved);
        setHasSavedDetails(true);
      }
    }
  }, [invoiceType]);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();

    if (items.length === 0) {
      toast.error('Please add at least one item');
      return;
    }

    // Save seller details if checkbox is checked (only for user invoices)
    if (invoiceType === 'user' && saveDetails) {
      saveSellerDetails({
        seller_name: formData.seller_name,
        seller_gstin: formData.seller_gstin,
        seller_address: formData.seller_address,
        seller_pincode: formData.seller_pincode,
        seller_state: formData.seller_state,
        gst_rate: formData.gst_rate || 18,
      });
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

      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [formData, items, onSubmit, invoiceType, saveDetails]);

  const handleClearSavedDetails = useCallback(() => {
    if (confirm('Are you sure you want to clear your saved business details?')) {
      clearSellerDetails();
      setFormData({});
      setHasSavedDetails(false);
      toast.success('Saved details cleared successfully!');
    }
  }, []);

  const updateField = useCallback((field: string, value: any) => {
    setFormData((prev: any) => ({ ...prev, [field]: value }));

    // Real-time validation
    let error: string | null = null;
    if (field === 'seller_gstin' || field === 'buyer_gstin') {
      error = validateGSTIN(value);
    } else if (field === 'seller_pincode' || field === 'buyer_pincode') {
      error = validatePincode(value);
    } else if (field === 'buyer_email') {
      error = validateEmail(value);
    } else if (field === 'buyer_phone') {
      error = validatePhone(value);
    }

    setErrors((prev) => ({ ...prev, [field]: error }));
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b dark:border-gray-700 sticky top-0 z-10 shadow-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button onClick={onBack} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white flex items-center transition-colors">
              <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back
            </button>
            <div className="h-8 w-px bg-gray-300 dark:bg-gray-600"></div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100 dark:text-white">Create Invoice</h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">
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
                  <h2 className="text-lg heading-text">Your Business Details</h2>
                  <p className="text-sm text-gray-500">Information about your company</p>
                </div>
              </div>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <label className="block label-text mb-1">Business Name *</label>
                  <input required placeholder="Your Company Pvt Ltd" className="form-input"
                    value={formData.seller_name || ''}
                    onChange={(e) => updateField('seller_name', e.target.value)} />
                </div>
                <div>
                  <label className="block label-text mb-1">GSTIN *</label>
                  <input required placeholder="29ABCDE1234F1Z5" maxLength={15} className={`form-input uppercase ${errors.seller_gstin ? 'border-red-500 focus:ring-red-500' : ''}`}
                    value={formData.seller_gstin || ''}
                    onChange={(e) => updateField('seller_gstin', e.target.value.toUpperCase())} />
                  <ErrorMessage errors={errors} field="seller_gstin" />
                </div>
                <div>
                  <label className="block label-text mb-1">State *</label>
                  <select required className="form-input"
                    value={formData.seller_state || ''}
                    onChange={(e) => updateField('seller_state', e.target.value)}>
                    <option value="">Select State</option>
                    {INDIAN_STATES.map(s => <option key={s.code} value={s.code}>{s.name}</option>)}
                  </select>
                </div>
                <div className="md:col-span-2">
                  <label className="block label-text mb-1">Address *</label>
                  <input required placeholder="Street, City" className="form-input"
                    value={formData.seller_address || ''}
                    onChange={(e) => updateField('seller_address', e.target.value)} />
                </div>
                <div>
                  <label className="block label-text mb-1">Pincode *</label>
                  <input required placeholder="400001" maxLength={6} className={`form-input ${errors.seller_pincode ? 'border-red-500 focus:ring-red-500' : ''}`}
                    value={formData.seller_pincode || ''}
                    onChange={(e) => updateField('seller_pincode', e.target.value)} />
                  <ErrorMessage errors={errors} field="seller_pincode" />
                </div>
                <div>
                  <label className="block label-text mb-1">GST Rate (%) *</label>
                  <select required className="form-input"
                    value={formData.gst_rate || '18'}
                    onChange={(e) => updateField('gst_rate', parseFloat(e.target.value))}>
                    <option value="0">0% - Exempt</option>
                    <option value="5">5% - Essential Goods/Services</option>
                    <option value="12">12% - Standard Rate</option>
                    <option value="18">18% - Standard Rate (Default)</option>
                    <option value="28">28% - Luxury Goods</option>
                  </select>
                </div>
                <div className="md:col-span-2">
                  <label className="block label-text mb-1">Business Logo <span className="text-gray-400">(Optional)</span></label>
                  <input
                    type="file"
                    accept="image/png,image/jpeg,image/jpg"
                    className="form-input"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) {
                        updateField('seller_logo', file);
                      }
                    }}
                  />
                  <p className="text-xs text-gray-500 mt-1">Upload your business logo (PNG, JPG). Max size: 120x60px recommended.</p>
                </div>
                <div className="md:col-span-2">
                  <label className="block label-text mb-1">Website/Profile URL <span className="text-gray-400">(Optional)</span></label>
                  <input
                    type="url"
                    placeholder="https://mycompany.com"
                    className="form-input"
                    value={formData.seller_website || ''}
                    onChange={(e) => updateField('seller_website', e.target.value)}
                  />
                  <p className="text-xs text-gray-500 mt-1">Your business website or profile URL (will appear on invoice)</p>
                </div>
              </div>

              {/* Save Details Checkbox and Clear Button */}
              <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={saveDetails}
                    onChange={(e) => setSaveDetails(e.target.checked)}
                    className="w-4 h-4 text-blue-600 border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                    Save my business details for next time
                  </span>
                </label>
                {hasSavedDetails && (
                  <button
                    type="button"
                    onClick={handleClearSavedDetails}
                    className="text-sm text-red-600 hover:text-red-800 hover:underline"
                  >
                    Clear Saved Details
                  </button>
                )}
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
                <h2 className="text-lg heading-text">Client Details</h2>
                <p className="text-sm text-gray-500">Who are you billing?</p>
              </div>
            </div>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block label-text mb-1">Client Name *</label>
                <input required placeholder="Client Company Name" className="form-input"
                  onChange={(e) => updateField('buyer_name', e.target.value)} />
              </div>
              <div>
                <label className="block label-text mb-1">Client GSTIN <span className="text-gray-400">(Optional)</span></label>
                <input placeholder="29ABCDE1234F1Z5" maxLength={15} className={`form-input uppercase ${errors.buyer_gstin ? 'border-red-500 focus:ring-red-500' : ''}`}
                  onChange={(e) => updateField('buyer_gstin', e.target.value.toUpperCase())} />
                <ErrorMessage errors={errors} field="buyer_gstin" />
              </div>
              <div>
                <label className="block label-text mb-1">State *</label>
                <select required className="form-input"
                  onChange={(e) => updateField('buyer_state', e.target.value)}>
                  <option value="">Select State</option>
                  {INDIAN_STATES.map(s => <option key={s.code} value={s.code}>{s.name}</option>)}
                </select>
              </div>
              <div className="md:col-span-2">
                <label className="block label-text mb-1">Address *</label>
                <input required placeholder="Street, City" className="form-input"
                  onChange={(e) => updateField('buyer_address', e.target.value)} />
              </div>
              <div>
                <label className="block label-text mb-1">Pincode *</label>
                <input required placeholder="400001" maxLength={6} className={`form-input ${errors.buyer_pincode ? 'border-red-500 focus:ring-red-500' : ''}`}
                  onChange={(e) => updateField('buyer_pincode', e.target.value)} />
                <ErrorMessage errors={errors} field="buyer_pincode" />
              </div>
              <div>
                <label className="block label-text mb-1">Phone <span className="text-gray-400">(Optional)</span></label>
                <input type="tel" placeholder="+91 9876543210" maxLength={15} className={`form-input ${errors.buyer_phone ? 'border-red-500 focus:ring-red-500' : ''}`}
                  onChange={(e) => updateField('buyer_phone', e.target.value)} />
                <ErrorMessage errors={errors} field="buyer_phone" />
              </div>
              <div>
                <label className="block label-text mb-1">Email <span className="text-gray-400">(Optional)</span></label>
                <input type="email" placeholder="client@example.com" className={`form-input ${errors.buyer_email ? 'border-red-500 focus:ring-red-500' : ''}`}
                  onChange={(e) => updateField('buyer_email', e.target.value)} />
                <ErrorMessage errors={errors} field="buyer_email" />
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
                  <h2 className="text-lg heading-text">Invoice Items</h2>
                  <p className="text-sm text-gray-500">Add products or services</p>
                </div>
              </div>
            </div>

            {/* Display Items */}
            {items.length > 0 && (
              <div className="mb-5 space-y-3">
                {items.map((item, idx) => (
                  <div key={idx} className="item-card stagger-item">
                    <div className="flex-1">
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-semibold text-gray-900">{item.description}</p>
                          <p className="text-sm text-gray-500 mt-1">
                            HSN: {item.hsn_sac} • Qty: {item.quantity} × ₹{item.unit_price.toFixed(2)}
                          </p>
                        </div>
                        <div className="text-right ml-4">
                          <p className="text-lg heading-text">₹{(item.quantity * item.unit_price).toFixed(2)}</p>
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
            <label className="block label-text mb-2">Notes / Terms & Conditions <span className="text-gray-400">(Optional)</span></label>
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
