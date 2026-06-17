"""
File upload security helpers — OWASP ASVS V12 / Manual Checklist item 6.

Checks performed:
  1. Extension whitelist
  2. MIME type via python-magic (reads actual file bytes, not just filename)
  3. Maximum file size (5 MB)
  4. Filename is already randomised to UUID by the model's upload_to callback
"""
import imghdr
import logging

logger = logging.getLogger('security')

# Allowed image extensions (lowercase, with leading dot)
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

# Corresponding imghdr type strings returned by imghdr.what()
ALLOWED_IMGHDR_TYPES = {'jpeg', 'png', 'webp'}

# 5 MB hard limit
MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MiB


def validate_room_image(uploaded_file):
    """
    Raise ValueError with a user-safe message if the upload fails any check.
    Call this inside a Django form's clean_image() method.
    """
    import os

    # --- 1. Extension whitelist ---
    _, ext = os.path.splitext(uploaded_file.name)
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file extension '{ext}'. "
            f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # --- 2. File size limit ---
    if uploaded_file.size > MAX_UPLOAD_BYTES:
        raise ValueError(
            f"File too large ({uploaded_file.size // 1024} KB). "
            f"Maximum allowed size is {MAX_UPLOAD_BYTES // 1024 // 1024} MB."
        )

    # --- 3. Magic-byte MIME check (reads actual file bytes) ---
    # Seek to beginning so imghdr reads from start
    uploaded_file.seek(0)
    detected = imghdr.what(uploaded_file)
    uploaded_file.seek(0)  # Reset for Django's subsequent handling

    if detected not in ALLOWED_IMGHDR_TYPES:
        logger.warning(
            f"FILE_UPLOAD_REJECTED | name={uploaded_file.name} "
            f"| ext={ext} | detected_type={detected}"
        )
        raise ValueError(
            "File content does not match a recognised image format. "
            "Please upload a valid JPEG, PNG, or WebP image."
        )

    return uploaded_file
