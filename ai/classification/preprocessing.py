import re
from urllib.parse import urlparse


class ImageValidationError(ValueError):
    """Raised when an image reference or format fails validation."""

    pass


def validate_image_reference(image_url: str) -> str:
    """Validate and sanitize an incoming image reference or URL.

    Ensures that the input is non-empty, lacks path-traversal patterns,
    and conforms to accepted reference formats (HTTP/HTTPS URL, data URI, or relative asset path).

    Args:
        image_url: The image URL or reference string to validate.

    Returns:
        str: Cleaned and stripped image reference string.

    Raises:
        ImageValidationError: If validation fails.
    """
    if not image_url or not isinstance(image_url, str):
        raise ImageValidationError("Image reference must be a non-empty string.")

    cleaned = image_url.strip()
    if not cleaned:
        raise ImageValidationError("Image reference cannot be blank.")

    # Guard against null byte injections
    if "\x00" in cleaned:
        raise ImageValidationError("Invalid characters detected in image reference.")

    # Guard against directory traversal in local path references
    if "../" in cleaned or "..\\" in cleaned or cleaned.startswith("/etc") or cleaned.startswith("C:\\Windows"):
        raise ImageValidationError("Path traversal sequences are strictly prohibited.")

    parsed = urlparse(cleaned)
    if parsed.scheme:
        if parsed.scheme.lower() not in ("http", "https", "data", "file"):
            raise ImageValidationError(f"Unsupported URL scheme '{parsed.scheme}'. Must be HTTP, HTTPS, DATA, or FILE.")
    else:
        # Relative path/token reference validation
        if not re.match(r"^[a-zA-Z0-9_\-\.\/\\]+$", cleaned):
            raise ImageValidationError("Image path contains invalid or dangerous characters.")

    return cleaned
