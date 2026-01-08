export const validateGSTIN = (gstin: string): string | null => {
  if (!gstin) return null;

  const gstinRegex = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/;

  if (gstin.length !== 15) {
    return 'GSTIN must be exactly 15 characters';
  }

  if (!gstinRegex.test(gstin)) {
    return 'Invalid GSTIN format (e.g., 29ABCDE1234F1Z5)';
  }

  return null;
};

export const validatePincode = (pincode: string): string | null => {
  if (!pincode) return null;

  if (!/^\d{6}$/.test(pincode)) {
    return 'Pincode must be exactly 6 digits';
  }

  return null;
};

export const validateEmail = (email: string): string | null => {
  if (!email) return null;

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!emailRegex.test(email)) {
    return 'Invalid email format';
  }

  return null;
};

export const validatePhone = (phone: string): string | null => {
  if (!phone) return null;

  // Remove spaces and special characters
  const cleanPhone = phone.replace(/[\s\-\(\)]/g, '');

  if (cleanPhone.length < 10 || cleanPhone.length > 15) {
    return 'Phone number must be 10-15 digits';
  }

  if (!/^[\+]?[\d]+$/.test(cleanPhone)) {
    return 'Invalid phone number format';
  }

  return null;
};
