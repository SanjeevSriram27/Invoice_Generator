"""
Validation utilities for invoice operations
Ported from Django's invoices/utils.py and model validators
"""
import re
from typing import Tuple


def validate_and_format_phone(phone: str, default_country_code: str = '91') -> Tuple[bool, str, str]:
    """
    Validate and format phone number with country code for WhatsApp/international use.

    Args:
        phone: Phone number string (can be with or without country code)
        default_country_code: Default country code to use if not present (default: '91' for India)

    Returns:
        Tuple of (is_valid, formatted_phone, error_message)
        - is_valid: Boolean indicating if phone is valid
        - formatted_phone: Phone with + and country code (e.g., '+918148382707')
        - error_message: Error message if invalid, empty string if valid

    Examples:
        '8148382707' -> (True, '+918148382707', '')
        '+918148382707' -> (True, '+918148382707', '')
        '918148382707' -> (True, '+918148382707', '')
        '+1234567890' -> (True, '+1234567890', '')
        'invalid' -> (False, '', 'Invalid phone number format')
    """
    if not phone:
        return False, '', 'Phone number is required'

    # Remove all whitespace and common separators
    cleaned = re.sub(r'[\s\-\(\)\.]+', '', phone.strip())

    # Check if it contains only digits and optional leading +
    if not re.match(r'^\+?\d+$', cleaned):
        return False, '', 'Phone number must contain only digits and optional + prefix'

    # Check if input already had a + prefix (indicates country code is present)
    had_plus_prefix = cleaned.startswith('+')

    # Remove + for processing
    digits_only = cleaned.lstrip('+')

    # Validate minimum length (at least 10 digits for most countries)
    if len(digits_only) < 10:
        return False, '', 'Phone number must be at least 10 digits'

    # Validate maximum length (15 digits as per E.164 standard)
    if len(digits_only) > 15:
        return False, '', 'Phone number cannot exceed 15 digits'

    # Determine if country code is present
    has_country_code = False
    formatted_number = digits_only

    # If input had + prefix, assume country code is present
    if had_plus_prefix:
        has_country_code = True
    # Check common country code patterns
    elif digits_only.startswith('91') and len(digits_only) == 12:  # India: +91 XXXXXXXXXX (10 digits)
        has_country_code = True
    elif digits_only.startswith('1') and len(digits_only) == 11:  # USA/Canada: +1 XXXXXXXXXX (10 digits)
        has_country_code = True
    elif len(digits_only) > 10:  # Assume country code is present if more than 10 digits
        has_country_code = True

    # Add default country code if not present
    if not has_country_code:
        formatted_number = f"{default_country_code}{digits_only}"

    # Add + prefix
    formatted_number = f"+{formatted_number}"

    return True, formatted_number, ''


def format_indian_phone(phone: str) -> Tuple[bool, str, str]:
    """
    Convenience function specifically for Indian phone numbers.
    Validates and formats to +91XXXXXXXXXX format.

    Args:
        phone: Phone number string

    Returns:
        Tuple of (is_valid, formatted_phone, error_message)
    """
    return validate_and_format_phone(phone, default_country_code='91')


def validate_gstin(gstin: str) -> Tuple[bool, str]:
    """
    Validate Indian GSTIN (GST Identification Number).
    Format: 15 characters - 2 digits (state code) + 5 letters (PAN) + 4 digits + 1 letter + 1 digit/letter + Z + 1 digit/letter

    Args:
        gstin: GSTIN string to validate

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        '29AAFCT0123A1Z5' -> (True, '')
        'invalid' -> (False, 'Invalid GSTIN format')
    """
    if not gstin:
        return False, 'GSTIN is required'

    # GSTIN pattern: 2 digits, 5 letters, 4 digits, 1 letter, 1 digit/letter, Z, 1 digit/letter
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'

    if not re.match(pattern, gstin):
        return False, 'Invalid GSTIN format. Expected format: 29AAFCT0123A1Z5'

    # Verify length
    if len(gstin) != 15:
        return False, 'GSTIN must be exactly 15 characters'

    return True, ''


def validate_pincode(pincode: str) -> Tuple[bool, str]:
    """
    Validate Indian pincode (6 digits).

    Args:
        pincode: Pincode string to validate

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        '560001' -> (True, '')
        '12345' -> (False, 'Pincode must be exactly 6 digits')
        'abcdef' -> (False, 'Pincode must contain only digits')
    """
    if not pincode:
        return False, 'Pincode is required'

    # Remove whitespace
    pincode = pincode.strip()

    # Check if it contains only digits
    if not pincode.isdigit():
        return False, 'Pincode must contain only digits'

    # Check length
    if len(pincode) != 6:
        return False, 'Pincode must be exactly 6 digits'

    return True, ''


def infer_state_from_pincode(pincode: str) -> str:
    """
    Infer Indian state code from pincode (simplified mapping).
    Uses first digit of pincode to determine region.

    Note: This is a simplified mapping. For production, use a complete pincode database.

    Args:
        pincode: 6-digit Indian pincode

    Returns:
        State code (2 letters) or 'DL' as default

    Mapping (first digit):
        1 -> Delhi, Haryana, Punjab, Himachal Pradesh, Jammu & Kashmir
        2 -> Uttarakhand, Uttar Pradesh
        3 -> Rajasthan, Gujarat
        4 -> Maharashtra, Madhya Pradesh, Chhattisgarh
        5 -> Andhra Pradesh, Telangana, Karnataka
        6 -> Tamil Nadu, Kerala, Puducherry
        7 -> West Bengal, Odisha, Assam, North-Eastern states
        8 -> Bihar, Jharkhand
        9 -> Reserved
    """
    if not pincode or len(pincode) < 1:
        return 'DL'  # Default to Delhi

    first_digit = pincode[0]

    # Simplified mapping based on first digit
    mapping = {
        '1': 'DL',  # Delhi region
        '2': 'UP',  # Uttar Pradesh region
        '3': 'RJ',  # Rajasthan region
        '4': 'MH',  # Maharashtra region
        '5': 'KA',  # Karnataka region (5 series is primarily Karnataka)
        '6': 'TN',  # Tamil Nadu region
        '7': 'WB',  # West Bengal region
        '8': 'BR',  # Bihar region
        '9': 'DL',  # Reserved, default to Delhi
    }

    return mapping.get(first_digit, 'DL')


# Validation helpers for Pydantic
def validate_phone_field(value: str) -> str:
    """
    Pydantic field validator for phone numbers.
    Raises ValueError if invalid, returns formatted phone if valid.
    """
    if not value:
        return value

    is_valid, formatted, error = validate_and_format_phone(value)
    if not is_valid:
        raise ValueError(error)
    return formatted


def validate_gstin_field(value: str) -> str:
    """
    Pydantic field validator for GSTIN.
    Raises ValueError if invalid, returns GSTIN if valid.
    """
    if not value:
        return value

    is_valid, error = validate_gstin(value)
    if not is_valid:
        raise ValueError(error)
    return value


def validate_pincode_field(value: str) -> str:
    """
    Pydantic field validator for pincode.
    Raises ValueError if invalid, returns pincode if valid.
    """
    if not value:
        return value

    is_valid, error = validate_pincode(value)
    if not is_valid:
        raise ValueError(error)
    return value
