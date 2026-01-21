const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Lazy load axios only when API methods are called
let axiosInstance: any = null;

async function getAxios() {
  if (!axiosInstance) {
    const axios = (await import('axios')).default;
    axiosInstance = axios.create({
      baseURL: API_URL,
      headers: { 'Content-Type': 'application/json' },
    });
  }
  return axiosInstance;
}

export const invoiceApi = {
  create: async (data: any) => {
    const api = await getAxios();

    // Check if data contains file uploads (logo)
    const hasFiles = data.seller_logo instanceof File || data.buyer_logo instanceof File;

    if (hasFiles) {
      // Use FormData for file uploads
      const formData = new FormData();

      // Append all fields to FormData
      Object.keys(data).forEach((key) => {
        if (key === 'items') {
          // Items need to be sent as JSON string for FormData
          formData.append('items_json', JSON.stringify(data[key]));
        } else if (data[key] instanceof File) {
          // Append file
          formData.append(key, data[key]);
        } else if (data[key] !== null && data[key] !== undefined && data[key] !== '') {
          // Append other fields
          formData.append(key, data[key]);
        }
      });

      const response = await api.post('/invoices/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    } else {
      // Use JSON for non-file uploads
      const response = await api.post('/invoices/', data);
      return response.data;
    }
  },

  downloadPdf: async (id: number) => {
    const api = await getAxios();
    const response = await api.get(`/invoices/${id}/download_pdf/`, {
      responseType: 'blob',
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `invoice_${id}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },

  shareWhatsApp: async (id: number, phoneNumber: string) => {
    const api = await getAxios();
    const response = await api.post(`/invoices/${id}/share_whatsapp/`, {
      phone: phoneNumber,
    });
    return response.data;
  },

  shareEmail: async (id: number, email: string) => {
    const api = await getAxios();
    const response = await api.post(`/invoices/${id}/send_email/`, {
      email,
    });
    return response.data;
  },
};

export default { invoiceApi };
