'use client';

import { useState } from 'react';

export default function BulkUploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    invoiceType: 'user',
    userId: 'test_user_123',
    createAsDraft: false,
    sendEmail: true,
    sendWhatsapp: false,
    gstRate: '18',
    sellerName: '',
    sellerGstin: '',
    sellerAddress: '',
    sellerPincode: '',
    sellerState: 'KA',
    sellerPhone: '',
    sellerEmail: ''
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;

    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file) {
      setError('Please select a CSV file');
      return;
    }

    if (formData.invoiceType === 'user') {
      if (!formData.sellerName || !formData.sellerGstin || !formData.sellerAddress ||
          !formData.sellerPincode || !formData.sellerState) {
        setError('Please fill in all seller details for user invoices');
        return;
      }
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('csv_file', file);
      formDataToSend.append('invoice_type', formData.invoiceType);
      formDataToSend.append('user_id', formData.userId);
      formDataToSend.append('create_as_draft', formData.createAsDraft.toString());
      formDataToSend.append('send_email', formData.sendEmail.toString());
      formDataToSend.append('send_whatsapp', formData.sendWhatsapp.toString());
      formDataToSend.append('gst_rate', formData.gstRate);

      if (formData.invoiceType === 'user') {
        formDataToSend.append('seller_name', formData.sellerName);
        formDataToSend.append('seller_gstin', formData.sellerGstin);
        formDataToSend.append('seller_address', formData.sellerAddress);
        formDataToSend.append('seller_pincode', formData.sellerPincode);
        formDataToSend.append('seller_state', formData.sellerState);
        formDataToSend.append('seller_phone', formData.sellerPhone);
        formDataToSend.append('seller_email', formData.sellerEmail);
      }

      const response = await fetch('http://127.0.0.1:8000/api/invoices/bulk-upload/', {
        method: 'POST',
        body: formDataToSend,
      });

      const data = await response.json();

      if (response.ok) {
        setResult(data);
      } else {
        setError(data.error || 'Failed to upload CSV');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred while uploading');
    } finally {
      setLoading(false);
    }
  };

  const downloadSample = () => {
    const csvContent = `receiver_name,receiver_address,pincode,phone,email,gstin,product_descriptions,hsn_sac_codes,quantities,total_values
"John Doe","123 Main Street, Bangalore","560001","919876543210","john@example.com","29ABCDE1234F1Z5","Website Development, SEO Services","998314, 998316","1, 2","59000, 23600"
"Jane Smith","456 Park Avenue, Delhi","110001","919876543211","jane@example.com","","Consulting Service","998314","5","118000"`;

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sample_invoices.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Bulk Invoice Upload</h1>
          <p className="text-gray-600 mb-6">Upload a CSV file to generate multiple invoices and send them via email</p>

          <div className="mb-6">
            <button
              onClick={downloadSample}
              className="text-blue-600 hover:text-blue-800 underline text-sm"
            >
              📥 Download Sample CSV Template
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* CSV File Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                CSV File *
              </label>
              <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none p-2.5"
              />
              {file && (
                <p className="mt-2 text-sm text-green-600">✓ {file.name} selected</p>
              )}
            </div>

            {/* Invoice Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Invoice Type *
              </label>
              <select
                name="invoiceType"
                value={formData.invoiceType}
                onChange={handleInputChange}
                className="block w-full p-2.5 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="user">User Invoice</option>
                <option value="topmate">Topmate Invoice</option>
              </select>
            </div>

            {/* User ID */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                User ID *
              </label>
              <input
                type="text"
                name="userId"
                value={formData.userId}
                onChange={handleInputChange}
                className="block w-full p-2.5 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* GST Rate */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                GST Rate (%) *
              </label>
              <select
                name="gstRate"
                value={formData.gstRate}
                onChange={handleInputChange}
                className="block w-full p-2.5 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="0">0% - Exempt</option>
                <option value="5">5%</option>
                <option value="12">12%</option>
                <option value="18">18% (Most Common)</option>
                <option value="28">28%</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">
                This GST rate will be applied to all invoices. CGST/IGST split is automatic based on location.
              </p>
            </div>

            {/* Options */}
            <div className="space-y-3">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="sendEmail"
                  checked={formData.sendEmail}
                  onChange={handleInputChange}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-900">Send invoices via Email</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="sendWhatsapp"
                  checked={formData.sendWhatsapp}
                  onChange={handleInputChange}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-900">Send invoices via WhatsApp</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="createAsDraft"
                  checked={formData.createAsDraft}
                  onChange={handleInputChange}
                  disabled={formData.sendEmail || formData.sendWhatsapp}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 disabled:opacity-50"
                />
                <span className="ml-2 text-sm text-gray-900">Create as Draft</span>
              </label>
              {(formData.sendEmail || formData.sendWhatsapp) && (
                <p className="text-xs text-gray-500 ml-6">Cannot create drafts when sending is enabled</p>
              )}
            </div>

            {/* Seller Details (only for user invoices) */}
            {formData.invoiceType === 'user' && (
              <div className="border-t pt-6 space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">Seller Details</h3>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Seller Name *
                  </label>
                  <input
                    type="text"
                    name="sellerName"
                    value={formData.sellerName}
                    onChange={handleInputChange}
                    className="block w-full p-2.5 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Your Company Name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    GSTIN *
                  </label>
                  <input
                    type="text"
                    name="sellerGstin"
                    value={formData.sellerGstin}
                    onChange={handleInputChange}
                    className="block w-full p-2.5 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                    placeholder="29ABCDE1234F1Z5"
                    maxLength={15}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Address *
                  </label>
                  <textarea
                    name="sellerAddress"
                    value={formData.sellerAddress}
                    onChange={handleInputChange}
                    rows={3}
                    className="block w-full p-2.5 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                    placeholder="123 Business Street, City"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Pincode *
                    </label>
                    <input
                      type="text"
                      name="sellerPincode"
                      value={formData.sellerPincode}
                      onChange={handleInputChange}
                      className="block w-full p-2.5 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                      placeholder="560001"
                      maxLength={6}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      State Code *
                    </label>
                    <input
                      type="text"
                      name="sellerState"
                      value={formData.sellerState}
                      onChange={handleInputChange}
                      className="block w-full p-2.5 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                      placeholder="KA"
                      maxLength={2}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone (Optional)
                  </label>
                  <input
                    type="tel"
                    name="sellerPhone"
                    value={formData.sellerPhone}
                    onChange={handleInputChange}
                    className="block w-full p-2.5 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                    placeholder="9876543210"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email (Optional)
                  </label>
                  <input
                    type="email"
                    name="sellerEmail"
                    value={formData.sellerEmail}
                    onChange={handleInputChange}
                    className="block w-full p-2.5 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                    placeholder="seller@example.com"
                  />
                </div>
              </div>
            )}

            {/* Submit Button */}
            <div className="pt-4">
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? 'Processing...' : 'Upload & Generate Invoices'}
              </button>
            </div>
          </form>

          {/* Error Display */}
          {error && (
            <div className="mt-6 bg-red-50 border border-red-200 text-red-800 rounded-lg p-4">
              <p className="font-semibold">Error:</p>
              <p>{error}</p>
            </div>
          )}

          {/* Success Result */}
          {result && (
            <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-green-900 mb-4">
                {result.message}
              </h3>

              {/* Summary */}
              <div className="bg-white rounded-lg p-4 mb-4">
                <h4 className="font-semibold mb-2">Summary:</h4>
                <ul className="space-y-1 text-sm">
                  <li>Total Rows: {result.summary.total_rows}</li>
                  <li>✅ Successful: {result.summary.successful}</li>
                  <li>❌ Failed: {result.summary.failed}</li>
                  {result.summary.emails_sent !== null && (
                    <li>📧 Emails Sent: {result.summary.emails_sent}</li>
                  )}
                  {result.summary.whatsapp_sent !== null && (
                    <li>📱 WhatsApp Sent: {result.summary.whatsapp_sent}</li>
                  )}
                </ul>
              </div>

              {/* Success List */}
              {result.successes && result.successes.length > 0 && (
                <div className="mb-4">
                  <h4 className="font-semibold mb-2">✅ Successful Invoices:</h4>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {result.successes.map((success: any, index: number) => (
                      <div key={index} className="bg-white border rounded-lg p-3 text-sm">
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-semibold">{success.buyer_name}</p>
                            <p className="text-gray-600">Invoice: {success.invoice_number}</p>
                            <p className="text-gray-600">Total: Rs. {success.total}</p>
                            {success.email_sent && <p className="text-green-600">✓ Email Sent</p>}
                            {success.whatsapp_sent && <p className="text-green-600">✓ WhatsApp Sent</p>}
                          </div>
                          <a
                            href={success.download_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-xs"
                          >
                            Download PDF
                          </a>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Failures List */}
              {result.failures && result.failures.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-2 text-red-700">❌ Failed Invoices:</h4>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {result.failures.map((failure: any, index: number) => (
                      <div key={index} className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm">
                        <p className="font-semibold">Row {failure.row}</p>
                        <p className="text-red-700">{failure.errors}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
