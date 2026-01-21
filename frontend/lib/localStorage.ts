// Local storage utility for saving seller details

const SELLER_DETAILS_KEY = 'invoice_seller_details';

export interface SavedSellerDetails {
  seller_name: string;
  seller_gstin: string;
  seller_address: string;
  seller_pincode: string;
  seller_state: string;
  seller_phone?: string;
  seller_email?: string;
  seller_website?: string;
  seller_bank_name?: string;
  seller_account_number?: string;
  seller_ifsc_code?: string;
  seller_account_holder_name?: string;
  seller_branch?: string;
  gst_rate: number;
}

export const saveSellerDetails = (details: SavedSellerDetails): void => {
  try {
    localStorage.setItem(SELLER_DETAILS_KEY, JSON.stringify(details));
  } catch (error) {
    console.error('Failed to save seller details:', error);
  }
};

export const loadSellerDetails = (): SavedSellerDetails | null => {
  try {
    const saved = localStorage.getItem(SELLER_DETAILS_KEY);
    return saved ? JSON.parse(saved) : null;
  } catch (error) {
    console.error('Failed to load seller details:', error);
    return null;
  }
};

export const clearSellerDetails = (): void => {
  try {
    localStorage.removeItem(SELLER_DETAILS_KEY);
  } catch (error) {
    console.error('Failed to clear seller details:', error);
  }
};

export const hasSellerDetails = (): boolean => {
  try {
    return localStorage.getItem(SELLER_DETAILS_KEY) !== null;
  } catch (error) {
    return false;
  }
};
