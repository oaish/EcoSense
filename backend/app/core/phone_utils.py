import re
from typing import Optional


def normalize_phone_number(phone: Optional[str]) -> Optional[str]:
    """Normalizes and validates a phone number to standard E.164 format.
    
    Defaults to Indian mobile numbers (+91) when a 10-digit number is provided.
    
    Accepts:
        - 10 digits: "9876543210" -> "+919876543210"
        - Leading zero: "09876543210" -> "+919876543210"
        - With country code: "919876543210" or "+919876543210" -> "+919876543210"
        - Spaced/hyphenated: "+91 98765-43210" -> "+919876543210"
        - Other international E.164: "+14155552671" -> "+14155552671"
        - None or empty string -> None
        
    Raises:
        ValueError if the phone number is malformed.
    """
    if phone is None:
        return None

    cleaned = str(phone).strip()
    if not cleaned:
        return None

    # Check for invalid characters (only digits, +, -, space, brackets allowed)
    if not re.match(r"^[0-9+\s\-().]+$", cleaned):
        raise ValueError("Phone number contains invalid characters.")

    # Remove formatting characters
    digits_and_plus = re.sub(r"[\s\-().]", "", cleaned)

    # 1. If starts with '+91'
    if digits_and_plus.startswith("+91"):
        digits_after = digits_and_plus[3:]
        if not (len(digits_after) == 10 and digits_after[0] in "6789" and digits_after.isdigit()):
            raise ValueError("Invalid Indian mobile number after +91. Must be 10 digits starting with 6, 7, 8, or 9.")
        return f"+91{digits_after}"

    # 2. If starts with '91' and is 12 digits total
    if digits_and_plus.startswith("91") and len(digits_and_plus) == 12:
        digits_after = digits_and_plus[2:]
        if digits_after[0] in "6789" and digits_after.isdigit():
            return f"+91{digits_after}"
        raise ValueError("Invalid Indian mobile number after 91. Must be 10 digits starting with 6, 7, 8, or 9.")

    # 3. If starts with '0' and is 11 digits total (e.g. 09876543210)
    if digits_and_plus.startswith("0") and len(digits_and_plus) == 11:
        digits_after = digits_and_plus[1:]
        if digits_after[0] in "6789" and digits_after.isdigit():
            return f"+91{digits_after}"
        raise ValueError("Invalid Indian mobile number after 0. Must be 10 digits starting with 6, 7, 8, or 9.")

    # 4. Standard 10-digit Indian mobile number
    if len(digits_and_plus) == 10 and digits_and_plus.isdigit():
        if digits_and_plus[0] not in "6789":
            raise ValueError("Indian mobile numbers must start with 6, 7, 8, or 9.")
        return f"+91{digits_and_plus}"

    # 5. General international E.164 (e.g. +14155552671)
    if digits_and_plus.startswith("+"):
        raw_digits = digits_and_plus[1:]
        if 7 <= len(raw_digits) <= 15 and raw_digits.isdigit():
            return digits_and_plus
        raise ValueError("International phone number must have between 7 and 15 digits.")

    raise ValueError(
        "Invalid phone number format. Please provide a 10-digit Indian mobile number (e.g., 9876543210 or +919876543210)."
    )


def to_national_phone_digits(phone: Optional[str]) -> Optional[str]:
    """Converts an E.164 phone number to a clean 10-digit national mobile number.
    
    For Indian numbers (+91XXXXXXXXXX), returns the 10-digit mobile number (e.g. 9876543210).
    Returns None if the phone number is invalid or empty.
    """
    if not phone:
        return None
    try:
        normalized = normalize_phone_number(phone)
    except ValueError:
        return None
    if not normalized:
        return None
    if normalized.startswith("+91") and len(normalized) == 13:
        return normalized[3:]  # return 10-digit mobile number
    if normalized.startswith("+"):
        return normalized[1:]  # strip leading '+'
    return normalized


# Backwards compatibility alias
to_smshorizon_recipient = to_national_phone_digits


def mask_phone_number(phone: Optional[str]) -> str:
    """Masks a phone number for privacy in application logs.
    
    e.g. +919876543210 -> +91******3210
         9876543210    -> +91******3210
    """
    if not phone:
        return "<none>"
    phone_str = str(phone).strip()
    if len(phone_str) <= 6:
        return "***"
    if phone_str.startswith("+91") and len(phone_str) == 13:
        return f"+91******{phone_str[-4:]}"
    if len(phone_str) == 10 and phone_str.isdigit():
        return f"+91******{phone_str[-4:]}"
    prefix = phone_str[:3]
    suffix = phone_str[-4:]
    masked_length = len(phone_str) - len(prefix) - len(suffix)
    return f"{prefix}{'*' * max(masked_length, 4)}{suffix}"
