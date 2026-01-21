'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import ErrorMessage from '@/components/ErrorMessage';
import { saveSellerDetails, loadSellerDetails, clearSellerDetails } from '@/lib/localStorage';
import { validateGSTIN, validatePincode, validateEmail, validatePhone } from '@/lib/validation';

export default function BulkUploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [saveDetails, setSaveDetails] = useState(false);
  const [hasSavedDetails, setHasSavedDetails] = useState(false);
  const [errors, setErrors] = useState<Record<string, string | null>>({});

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

  // Load saved seller details on mount (only for user invoices)
  useEffect(() => {
    if (formData.invoiceType === 'user') {
      const saved = loadSellerDetails();
      if (saved) {
        setFormData(prev => ({
          ...prev,
          sellerName: saved.seller_name,
          sellerGstin: saved.seller_gstin,
          sellerAddress: saved.seller_address,
          sellerPincode: saved.seller_pincode,
          sellerState: saved.seller_state,
          gstRate: saved.gst_rate.toString()
        }));
        setHasSavedDetails(true);
      }
    }
  }, [formData.invoiceType]);

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

    // Real-time validation for seller fields
    let validationError: string | null = null;
    if (name === 'sellerGstin') {
      validationError = validateGSTIN(value);
    } else if (name === 'sellerPincode') {
      validationError = validatePincode(value);
    } else if (name === 'sellerEmail') {
      validationError = validateEmail(value);
    } else if (name === 'sellerPhone') {
      validationError = validatePhone(value);
    }

    setErrors(prev => ({ ...prev, [name]: validationError }));
  };

  const handleClearSavedDetails = () => {
    if (confirm('Are you sure you want to clear your saved business details?')) {
      clearSellerDetails();
      setFormData(prev => ({
        ...prev,
        sellerName: '',
        sellerGstin: '',
        sellerAddress: '',
        sellerPincode: '',
        sellerState: 'KA',
        sellerPhone: '',
        sellerEmail: '',
        gstRate: '18'
      }));
      setHasSavedDetails(false);
      toast.success('Saved details cleared successfully!');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file) {
      toast.error('Please select a CSV file');
      return;
    }

    if (formData.invoiceType === 'user') {
      if (!formData.sellerName || !formData.sellerGstin || !formData.sellerAddress ||
          !formData.sellerPincode || !formData.sellerState) {
        toast.error('Please fill in all seller details for user invoices');
        return;
      }
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('csv_file', file);

      // Build query parameters
      const queryParams = new URLSearchParams({
        invoice_type: formData.invoiceType,
        user_id: formData.userId,
        create_as_draft: formData.createAsDraft.toString(),
        send_email: formData.sendEmail.toString(),
        send_whatsapp: formData.sendWhatsapp.toString(),
        gst_rate: formData.gstRate,
      });

      if (formData.invoiceType === 'user') {
        queryParams.append('seller_name', formData.sellerName);
        queryParams.append('seller_gstin', formData.sellerGstin);
        queryParams.append('seller_address', formData.sellerAddress);
        queryParams.append('seller_pincode', formData.sellerPincode);
        queryParams.append('seller_state', formData.sellerState);
        if (formData.sellerPhone) queryParams.append('seller_phone', formData.sellerPhone);
        if (formData.sellerEmail) queryParams.append('seller_email', formData.sellerEmail);

        // Append logo if uploaded
        if ((formData as any).sellerLogo) {
          formDataToSend.append('seller_logo', (formData as any).sellerLogo);
        }

        // Append website if provided
        if ((formData as any).sellerWebsite) {
          queryParams.append('seller_website', (formData as any).sellerWebsite);
        }
      }

      const response = await fetch(`http://127.0.0.1:8000/api/invoices/bulk-upload/?${queryParams.toString()}`, {
        method: 'POST',
        body: formDataToSend,
      });

      const data = await response.json();

      if (response.ok) {
        // Save seller details if checkbox is checked (only for user invoices)
        if (formData.invoiceType === 'user' && saveDetails) {
          saveSellerDetails({
            seller_name: formData.sellerName,
            seller_gstin: formData.sellerGstin,
            seller_address: formData.sellerAddress,
            seller_pincode: formData.sellerPincode,
            seller_state: formData.sellerState,
            seller_phone: formData.sellerPhone,
            seller_email: formData.sellerEmail,
            seller_website: (formData as any).sellerWebsite,
            gst_rate: parseFloat(formData.gstRate)
          });
          setHasSavedDetails(true);
        }
        setResult(data);
        toast.success('Bulk upload completed successfully!');
      } else {
        setError(data.error || 'Failed to upload CSV');
        toast.error(data.error || 'Failed to upload CSV');
      }
    } catch (err: any) {
      const errorMsg = err.message || 'An error occurred while uploading';
      setError(errorMsg);
      toast.error(errorMsg);
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
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b dark:border-gray-700 sticky top-0 z-10 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button onClick={() => router.push('/')} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white flex items-center transition-colors">
              <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back
            </button>
            <div className="h-8 w-px bg-gray-300 dark:bg-gray-600"></div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">Bulk Invoice Upload</h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">Generate multiple invoices at once</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8 fade-in">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 transition-all duration-300 hover:shadow-xl">
          <p className="text-gray-600 dark:text-gray-300 mb-6">Upload a CSV file to generate multiple invoices and send them via email</p>

          <div className="mb-6">
            <button
              onClick={downloadSample}
              className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-800 font-semibold text-sm transition-all duration-200 hover:gap-3"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Download Sample CSV Template
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* CSV File Upload */}
            <div>
              <label className="block label-text mb-2">
                CSV File *
              </label>
              <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-900 dark:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer bg-gray-50 dark:bg-gray-700 focus:outline-none p-2.5"
              />
              {file && (
                <p className="mt-2 text-sm text-green-600">{file.name} selected</p>
              )}
            </div>

            {/* Invoice Type */}
            <div>
              <label className="block label-text mb-2">
                Invoice Type *
              </label>
              <select
                name="invoiceType"
                value={formData.invoiceType}
                onChange={handleInputChange}
                className="block w-full p-2.5 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-blue-500"
              >
                <option value="user">User Invoice</option>
                <option value="topmate">Topmate Invoice</option>
              </select>
            </div>

            {/* User ID */}
            <div>
              <label className="block label-text mb-2">
                User ID *
              </label>
              <input
                type="text"
                name="userId"
                value={formData.userId}
                onChange={handleInputChange}
                className="block w-full p-2.5 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-blue-500"
              />
            </div>

            {/* GST Rate */}
            <div>
              <label className="block label-text mb-2">
                GST Rate (%) *
              </label>
              <select
                name="gstRate"
                value={formData.gstRate}
                onChange={handleInputChange}
                className="block w-full p-2.5 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-blue-500"
              >
                <option value="0">0% - Exempt</option>
                <option value="5">5%</option>
                <option value="12">12%</option>
                <option value="18">18% (Most Common)</option>
                <option value="28">28%</option>
              </select>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
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
                  className="w-4 h-4 text-blue-600 border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-900 dark:text-gray-200">Send invoices via Email</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="sendWhatsapp"
                  checked={formData.sendWhatsapp}
                  onChange={handleInputChange}
                  className="w-4 h-4 text-blue-600 border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-900 dark:text-gray-200">Send invoices via WhatsApp</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="createAsDraft"
                  checked={formData.createAsDraft}
                  onChange={handleInputChange}
                  disabled={formData.sendEmail || formData.sendWhatsapp}
                  className="w-4 h-4 text-blue-600 border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded focus:ring-blue-500 disabled:opacity-50"
                />
                <span className="ml-2 text-sm text-gray-900 dark:text-gray-200">Create as Draft</span>
              </label>
              {(formData.sendEmail || formData.sendWhatsapp) && (
                <p className="text-xs text-gray-500 dark:text-gray-400 ml-6">Cannot create drafts when sending is enabled</p>
              )}
            </div>

            {/* Seller Details (only for user invoices) */}
            {formData.invoiceType === 'user' && (
              <div className="border-t pt-6 space-y-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Seller Details</h3>

                <div>
                  <label className="block label-text mb-2">
                    Seller Name *
                  </label>
                  <input
                    type="text"
                    name="sellerName"
                    value={formData.sellerName}
                    onChange={handleInputChange}
                    className="block w-full p-2.5 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-blue-500"
                    placeholder="Your Company Name"
                  />
                </div>

                <div>
                  <label className="block label-text mb-2">
                    GSTIN *
                  </label>
                  <input
                    type="text"
                    name="sellerGstin"
                    value={formData.sellerGstin}
                    onChange={handleInputChange}
                    className={`block w-full p-2.5 border rounded-lg uppercase transition-all duration-200 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 ${errors.sellerGstin ? 'border-red-500 focus:ring-red-500 focus:border-red-500' : 'border-gray-300 dark:border-gray-600 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-blue-500'}`}
                    placeholder="29ABCDE1234F1Z5"
                    maxLength={15}
                  />
                  <ErrorMessage errors={errors} field="sellerGstin" />
                </div>

                <div>
                  <label className="block label-text mb-2">
                    Address *
                  </label>
                  <textarea
                    name="sellerAddress"
                    value={formData.sellerAddress}
                    onChange={handleInputChange}
                    rows={3}
                    className="block w-full p-2.5 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-blue-500"
                    placeholder="123 Business Street, City"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block label-text mb-2">
                      Pincode *
                    </label>
                    <input
                      type="text"
                      name="sellerPincode"
                      value={formData.sellerPincode}
                      onChange={handleInputChange}
                      className={`block w-full p-2.5 border rounded-lg transition-all duration-200 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 ${errors.sellerPincode ? 'border-red-500 focus:ring-red-500 focus:border-red-500' : 'border-gray-300 dark:border-gray-600 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-blue-500'}`}
                      placeholder="560001"
                      maxLength={6}
                    />
                    <ErrorMessage errors={errors} field="sellerPincode" />
                  </div>

                  <div>
                    <label className="block label-text mb-2">
                      State Code *
                    </label>
                    <input
                      type="text"
                      name="sellerState"
                      value={formData.sellerState}
                      onChange={handleInputChange}
                      className="block w-full p-2.5 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-blue-500"
                      placeholder="KA"
                      maxLength={2}
                    />
                  </div>
                </div>

                <div>
                  <label className="block label-text mb-2">
                    Phone (Optional)
                  </label>
                  <input
                    type="tel"
                    name="sellerPhone"
                    value={formData.sellerPhone}
                    onChange={handleInputChange}
                    className={`block w-full p-2.5 border rounded-lg transition-all duration-200 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 ${errors.sellerPhone ? 'border-red-500 focus:ring-red-500 focus:border-red-500' : 'border-gray-300 dark:border-gray-600 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-blue-500'}`}
                    placeholder="9876543210"
                  />
                  <ErrorMessage errors={errors} field="sellerPhone" />
                </div>

                <div>
                  <label className="block label-text mb-2">
                    Email (Optional)
                  </label>
                  <input
                    type="email"
                    name="sellerEmail"
                    value={formData.sellerEmail}
                    onChange={handleInputChange}
                    className={`block w-full p-2.5 border rounded-lg transition-all duration-200 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 ${errors.sellerEmail ? 'border-red-500 focus:ring-red-500 focus:border-red-500' : 'border-gray-300 dark:border-gray-600 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-blue-500'}`}
                    placeholder="seller@example.com"
                  />
                  <ErrorMessage errors={errors} field="sellerEmail" />
                </div>

                <div>
                  <label className="block label-text mb-2">
                    Business Logo (Optional)
                  </label>
                  <input
                    type="file"
                    accept="image/png,image/jpeg,image/jpg"
                    onChange={(e) => {
                      const logoFile = e.target.files?.[0];
                      if (logoFile) {
                        setFormData(prev => ({ ...prev, sellerLogo: logoFile as any }));
                      }
                    }}
                    className="block w-full text-sm text-gray-900 dark:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer bg-gray-50 dark:bg-gray-700 focus:outline-none p-2.5"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Upload your business logo (PNG, JPG). Max size: 120x60px recommended.</p>
                </div>

                <div>
                  <label className="block label-text mb-2">
                    Website/Profile URL (Optional)
                  </label>
                  <input
                    type="url"
                    name="sellerWebsite"
                    value={(formData as any).sellerWebsite || ''}
                    onChange={handleInputChange}
                    className="block w-full p-2.5 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-blue-500"
                    placeholder="https://mycompany.com"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Your business website or profile URL (will appear on all invoices)</p>
                </div>

                {/* Save Details Checkbox and Clear Button */}
                <div className="mt-4 pt-4 border-t border-gray-200 flex items-center justify-between">
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
                      className="text-sm text-red-600 hover:text-red-800 hover:underline transition-colors"
                    >
                      Clear Saved Details
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Submit Button */}
            <div className="pt-4">
              <button
                type="submit"
                disabled={loading}
                className="w-full btn-primary disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed disabled:hover:scale-100"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Processing...
                  </span>
                ) : (
                  'Upload & Generate Invoices'
                )}
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
            <div className="mt-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-green-900 dark:text-green-200 mb-4">
                Bulk Upload Completed
              </h3>

              {/* Summary */}
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4 mb-4">
                <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">Summary:</h4>
                <ul className="space-y-1 text-sm text-gray-900 dark:text-gray-200">
                  <li>Total Rows: {result.total_rows}</li>
                  <li>Successful: {result.successful}</li>
                  <li>Failed: {result.failed}</li>
                  {result.processing_time_seconds && (
                    <li>Processing Time: {result.processing_time_seconds}s</li>
                  )}
                </ul>
              </div>

              {/* Success List */}
              {result.successes && result.successes.length > 0 && (
                <div className="mb-4">
                  <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">Successful Invoices:</h4>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {result.successes.map((success: any, index: number) => (
                      <div key={index} className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-3 text-sm">
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-semibold text-gray-900 dark:text-gray-100">{success.buyer_name}</p>
                            <p className="text-gray-600 dark:text-gray-400">Invoice: {success.invoice_number}</p>
                            <p className="text-gray-600 dark:text-gray-400">Total: Rs. {success.total}</p>
                            {success.email_sent && <p className="text-green-600 dark:text-green-400">Email Sent</p>}
                            {success.whatsapp_sent && <p className="text-green-600 dark:text-green-400">WhatsApp Sent</p>}
                            {success.is_draft && <p className="text-yellow-600 dark:text-yellow-400">Draft</p>}
                          </div>
                          <a
                            href={`http://localhost:8000/api/invoices/${success.invoice_id}/download_pdf/`}
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
                  <h4 className="font-semibold mb-2 text-red-700 dark:text-red-400">Failed Invoices:</h4>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {result.failures.map((failure: any, index: number) => (
                      <div key={index} className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3 text-sm">
                        <p className="font-semibold text-gray-900 dark:text-gray-100">Row {failure.row_number}</p>
                        <p className="text-gray-700 dark:text-gray-300">Buyer: {failure.buyer_name}</p>
                        <p className="text-red-700 dark:text-red-400 mt-1">{failure.error}</p>
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
