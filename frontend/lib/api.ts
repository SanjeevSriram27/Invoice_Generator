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
    const response = await api.post('/invoices/', data);
    return response.data;
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
