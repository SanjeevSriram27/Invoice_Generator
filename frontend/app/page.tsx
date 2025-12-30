'use client';

import { useState } from 'react';
import { useStore } from '@/lib/store';
import { invoiceApi } from '@/lib/api';
import { INDIAN_STATES, InvoiceItem } from '@/types/invoice';

export default function Home() {
  const { step, invoiceType, items, generatedInvoice, setStep, setInvoiceType, setItems, addItem, setGeneratedInvoice, reset } = useStore();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<any>({});

  // Step 1: Select Invoice Type (BillForge Style)
  if (step === 1) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50">
        <div className="container mx-auto px-4 py-16">
          <div className="text-center mb-16">
            <div className="inline-block mb-4">
              <div className="bg-blue-600 text-white px-6 py-2 rounded-full text-sm font-semibold">
                GST Compliant
              </div>
            </div>
            <h1 className="text-6xl font-bold text-gray-900 mb-4 tracking-tight">
              Invoice Generator
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Create professional GST-compliant invoices in seconds
            </p>

            {/* Bulk Upload Link */}
            <div className="mt-6">
              <a
                href="/bulk-upload"
                className="inline-flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-full font-semibold transition-colors shadow-lg hover:shadow-xl"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                Bulk Upload CSV (Generate Multiple Invoices)
              </a>
            </div>
          </div>

          <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-8">
            {/* Topmate Invoice Card */}
            <div
              onClick={() => { setInvoiceType('topmate'); setStep(2); }}
              className="group cursor-pointer bg-white rounded-3xl p-10 shadow-lg hover:shadow-2xl transition-all duration-300 border-2 border-transparent hover:border-blue-500 transform hover:-translate-y-2"
            >
              <div className="flex items-center justify-between mb-6">
                <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                </div>
                <div className="bg-blue-50 text-blue-700 px-4 py-1 rounded-full text-xs font-bold">
                  RECOMMENDED
                </div>
              </div>

              <h2 className="text-3xl font-bold text-gray-900 mb-3">
                Topmate Invoice
              </h2>
              <p className="text-gray-600 mb-6 leading-relaxed">
                Generate an invoice where <span className="font-semibold text-gray-800">Topmate is the seller</span>. Perfect for platform transactions.
              </p>

              <div className="space-y-3 mb-6">
                <div className="flex items-center text-sm text-gray-700">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Company details auto-filled
                </div>
                <div className="flex items-center text-sm text-gray-700">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Automatic GST calculation
                </div>
                <div className="flex items-center text-sm text-gray-700">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Professional invoice template
                </div>
              </div>

              <div className="flex items-center text-blue-600 font-semibold group-hover:translate-x-2 transition-transform">
                Get Started
                <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </div>
            </div>

            {/* Personal Invoice Card */}
            <div
              onClick={() => { setInvoiceType('user'); setStep(2); }}
              className="group cursor-pointer bg-white rounded-3xl p-10 shadow-lg hover:shadow-2xl transition-all duration-300 border-2 border-transparent hover:border-green-500 transform hover:-translate-y-2"
            >
              <div className="flex items-center justify-between mb-6">
                <div className="w-14 h-14 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
              </div>

              <h2 className="text-3xl font-bold text-gray-900 mb-3">
                Personal Invoice
              </h2>
              <p className="text-gray-600 mb-6 leading-relaxed">
                Generate an invoice for <span className="font-semibold text-gray-800">your own business</span>. Perfect for freelancers and agencies.
              </p>

              <div className="space-y-3 mb-6">
                <div className="flex items-center text-sm text-gray-700">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Your business details
                </div>
                <div className="flex items-center text-sm text-gray-700">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Full customization
                </div>
                <div className="flex items-center text-sm text-gray-700">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Profile saved for reuse
                </div>
              </div>

              <div className="flex items-center text-green-600 font-semibold group-hover:translate-x-2 transition-transform">
                Get Started
                <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Step 2: Invoice Form (BillForge Style)
  if (step === 2) {
    const handleSubmit = async (e: React.FormEvent) => {
      e.preventDefault();

      if (items.length === 0) {
        alert('Please add at least one item');
        return;
      }

      setLoading(true);
      try {
        const payload = {
          invoice_type: invoiceType,
          user_id: 'demo-user-123',
          ...formData,
          items: items,
        };

        const invoice = await invoiceApi.create(payload);
        setGeneratedInvoice(invoice);
        setStep(3);
      } catch (error: any) {
        let errorMessage = error.response?.data?.error || error.message;

        // Check for HSN/SAC validation error
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
    };

    return (
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white border-b sticky top-0 z-10 shadow-sm">
          <div className="container mx-auto px-4 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button onClick={() => reset()} className="text-gray-600 hover:text-gray-900 flex items-center">
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
              <div className="bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-sm font-medium">
                {items.length} items
              </div>
            </div>
          </div>
        </div>

        <div className="container mx-auto px-4 py-8 max-w-4xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Seller (for user invoices) */}
            {invoiceType === 'user' && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-center mb-5">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
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
                    <input required placeholder="Your Company Pvt Ltd" className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      onChange={(e) => setFormData({...formData, seller_name: e.target.value})} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">GSTIN *</label>
                    <input required placeholder="29ABCDE1234F1Z5" maxLength={15} className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent uppercase"
                      onChange={(e) => setFormData({...formData, seller_gstin: e.target.value.toUpperCase()})} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">State *</label>
                    <select required className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      onChange={(e) => setFormData({...formData, seller_state: e.target.value})}>
                      <option value="">Select State</option>
                      {INDIAN_STATES.map(s => <option key={s.code} value={s.code}>{s.name}</option>)}
                    </select>
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Address *</label>
                    <input required placeholder="Street, City" className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      onChange={(e) => setFormData({...formData, seller_address: e.target.value})} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Pincode *</label>
                    <input required placeholder="400001" maxLength={6} className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      onChange={(e) => setFormData({...formData, seller_pincode: e.target.value})} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">GST Rate (%) *</label>
                    <select required className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      onChange={(e) => setFormData({...formData, gst_rate: parseFloat(e.target.value)})}
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
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center mb-5">
                <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mr-3">
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
                  <input required placeholder="Client Company Name" className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    onChange={(e) => setFormData({...formData, buyer_name: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Client GSTIN <span className="text-gray-400">(Optional)</span></label>
                  <input placeholder="29ABCDE1234F1Z5" maxLength={15} className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent uppercase"
                    onChange={(e) => setFormData({...formData, buyer_gstin: e.target.value.toUpperCase()})} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">State *</label>
                  <select required className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    onChange={(e) => setFormData({...formData, buyer_state: e.target.value})}>
                    <option value="">Select State</option>
                    {INDIAN_STATES.map(s => <option key={s.code} value={s.code}>{s.name}</option>)}
                  </select>
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Address *</label>
                  <input required placeholder="Street, City" className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    onChange={(e) => setFormData({...formData, buyer_address: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Pincode *</label>
                  <input required placeholder="400001" maxLength={6} className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    onChange={(e) => setFormData({...formData, buyer_pincode: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Phone <span className="text-gray-400">(Optional)</span></label>
                  <input type="tel" placeholder="+91 9876543210" maxLength={15} className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    onChange={(e) => setFormData({...formData, buyer_phone: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email <span className="text-gray-400">(Optional)</span></label>
                  <input type="email" placeholder="client@example.com" className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    onChange={(e) => setFormData({...formData, buyer_email: e.target.value})} />
                </div>
              </div>
            </div>

            {/* Items */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-5">
                <div className="flex items-center">
                  <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
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
                    <div key={idx} className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg border border-gray-200">
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
                        onClick={() => setItems(items.filter((_, i) => i !== idx))}
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

              {/* Add Item Form - FIXED */}
              <AddItemForm onAdd={(item) => {
                addItem(item);
              }} />
            </div>

            {/* Notes */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Notes / Terms & Conditions <span className="text-gray-400">(Optional)</span></label>
              <textarea
                placeholder="Payment due within 30 days..."
                rows={3}
                className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                onChange={(e) => setFormData({...formData, notes: e.target.value})}
              />
            </div>

            {/* Submit */}
            <div className="sticky bottom-0 bg-white border-t border-gray-200 -mx-4 px-4 py-4 shadow-lg">
              <button
                type="submit"
                disabled={loading || items.length === 0}
                className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-4 rounded-xl font-bold text-lg hover:from-blue-700 hover:to-blue-800 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed transition-all transform hover:scale-[1.02] disabled:hover:scale-100 shadow-lg disabled:shadow-none"
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

  // Step 3: Success
  if (step === 3 && generatedInvoice) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 flex items-center justify-center p-4">
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
                <span className="text-xl font-bold text-blue-600">{generatedInvoice.invoice_number}</span>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Buyer</span>
                  <span className="font-semibold text-gray-900">{generatedInvoice.buyer_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Subtotal</span>
                  <span className="font-semibold">₹{generatedInvoice.subtotal}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">GST</span>
                  <span className="font-semibold">₹{(
                    parseFloat(generatedInvoice.cgst || '0') +
                    parseFloat(generatedInvoice.sgst || '0') +
                    parseFloat(generatedInvoice.igst || '0')
                  ).toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-2xl font-bold border-t border-blue-200 pt-3">
                  <span className="text-gray-900">Total</span>
                  <span className="text-green-600">₹{generatedInvoice.total}</span>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <button
                onClick={() => invoiceApi.downloadPdf(generatedInvoice.id!)}
                className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-4 rounded-xl font-bold text-lg hover:from-blue-700 hover:to-blue-800 transition-all transform hover:scale-[1.02] shadow-lg flex items-center justify-center"
              >
                <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Download PDF Invoice
              </button>

              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={async () => {
                    let phone = generatedInvoice.buyer_phone;
                    if (!phone) {
                      phone = prompt('Enter WhatsApp number (with country code, e.g., 919876543210):');
                    }
                    if (phone) {
                      try {
                        setLoading(true);
                        const response = await invoiceApi.shareWhatsApp(generatedInvoice.id!, phone);

                        // If Twilio is configured, PDF is sent directly
                        if (response.whatsapp_sid) {
                          alert('✓ Invoice PDF sent directly to WhatsApp!');
                        } else if (response.whatsapp_link) {
                          // Fallback: Open WhatsApp with message
                          window.open(response.whatsapp_link, '_blank');
                          alert(response.note || 'WhatsApp opened with invoice details');
                        }
                      } catch (error: any) {
                        alert(error.response?.data?.error || 'Failed to share via WhatsApp');
                      } finally {
                        setLoading(false);
                      }
                    }
                  }}
                  disabled={loading}
                  className="bg-green-500 text-white py-3 rounded-xl font-semibold hover:bg-green-600 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                  </svg>
                  {loading ? 'Sending...' : 'WhatsApp'}
                </button>

                <button
                  onClick={async () => {
                    let email = generatedInvoice.buyer_email;
                    if (!email) {
                      email = prompt('Enter email address:');
                    }
                    if (email) {
                      try {
                        setLoading(true);
                        const response = await invoiceApi.shareEmail(generatedInvoice.id!, email);
                        alert(`✓ Invoice PDF sent successfully to ${email}!`);
                      } catch (error: any) {
                        alert(error.response?.data?.error || 'Failed to send email');
                      } finally {
                        setLoading(false);
                      }
                    }
                  }}
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
                onClick={() => reset()}
                className="w-full bg-gray-100 text-gray-700 py-4 rounded-xl font-semibold text-lg hover:bg-gray-200 transition-all"
              >
                Create Another Invoice
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
}

// Add Item Form Component - FIXED to prevent page reload
function AddItemForm({ onAdd }: { onAdd: (item: InvoiceItem) => void }) {
  const [item, setItem] = useState<InvoiceItem>({
    description: '',
    hsn_sac: '',
    quantity: 1,
    unit_price: 0,
  });

  const handleAddItem = () => {
    if (!item.description || !item.hsn_sac || item.quantity <= 0 || item.unit_price <= 0) {
      alert('Please fill all item fields');
      return;
    }
    onAdd(item);
    setItem({ description: '', hsn_sac: '', quantity: 1, unit_price: 0 });
  };

  return (
    <div className="border-t border-gray-200 pt-5">
      <p className="text-sm font-medium text-gray-700 mb-3">Add New Item</p>
      <div className="space-y-3">
        <div className="grid md:grid-cols-2 gap-3">
          <input
            placeholder="Description *"
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            value={item.description}
            onChange={(e) => setItem({...item, description: e.target.value})}
          />
          <input
            placeholder="HSN/SAC Code *"
            maxLength={15}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            value={item.hsn_sac}
            onChange={(e) => setItem({...item, hsn_sac: e.target.value})}
          />
        </div>
        <div className="grid grid-cols-3 gap-3">
          <input
            type="number"
            placeholder="Quantity *"
            min="1"
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            value={item.quantity}
            onChange={(e) => setItem({...item, quantity: parseFloat(e.target.value) || 1})}
          />
          <input
            type="number"
            placeholder="Unit Price *"
            min="0"
            step="0.01"
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            value={item.unit_price}
            onChange={(e) => setItem({...item, unit_price: parseFloat(e.target.value) || 0})}
          />
          <button
            type="button"
            onClick={handleAddItem}
            className="bg-gradient-to-r from-green-600 to-emerald-600 text-white py-2 rounded-lg font-semibold hover:from-green-700 hover:to-emerald-700 transition-all flex items-center justify-center shadow-md"
          >
            <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Add
          </button>
        </div>
      </div>
    </div>
  );
}
