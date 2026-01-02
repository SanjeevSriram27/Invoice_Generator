'use client';

import Link from 'next/link';

interface InvoiceTypeSelectorProps {
  onSelectType: (type: 'topmate' | 'user') => void;
}

export default function InvoiceTypeSelector({ onSelectType }: InvoiceTypeSelectorProps) {
  return (
    <div className="bg-gradient-page">
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
            <Link
              href="/bulk-upload"
              className="inline-flex items-center gap-2 badge-green hover:bg-green-700 px-6 py-3 shadow-lg hover:shadow-xl transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              Bulk Upload CSV (Generate Multiple Invoices)
            </Link>
          </div>
        </div>

        <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-8">
          {/* Topmate Invoice Card */}
          <div
            onClick={() => onSelectType('topmate')}
            className="group card-hover-blue"
          >
            <div className="flex items-center justify-between mb-6">
              <div className="icon-container bg-gradient-to-br from-blue-500 to-blue-600">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <div className="badge-blue">
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
              <div className="feature-item">
                <svg className="feature-icon" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                Company details auto-filled
              </div>
              <div className="feature-item">
                <svg className="feature-icon" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                Automatic GST calculation
              </div>
              <div className="feature-item">
                <svg className="feature-icon" fill="currentColor" viewBox="0 0 20 20">
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
            onClick={() => onSelectType('user')}
            className="group card-hover-green"
          >
            <div className="flex items-center justify-between mb-6">
              <div className="icon-container bg-gradient-to-br from-green-500 to-emerald-600">
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
              <div className="feature-item">
                <svg className="feature-icon" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                Your business details
              </div>
              <div className="feature-item">
                <svg className="feature-icon" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                Full customization
              </div>
              <div className="feature-item">
                <svg className="feature-icon" fill="currentColor" viewBox="0 0 20 20">
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
