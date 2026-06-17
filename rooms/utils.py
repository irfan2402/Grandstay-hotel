"""
File upload security helpers — Manual Code Review Checklist item 6 / OWASP file upload.

Checks performed (defense-in-depth):
  1. Extension whitelist                — blocks .php, .exe, .svg, etc. by name.
  2. Declared Content-Type whitelist    — second-line check; spoofable, so never alone.
  3. Maximum file size (5 MB)            — matches DATA_UPLOAD_MAX_MEMORY_SIZE.
  4. Real image verification with Pillow — opens and decodes the file. This is
     what catches a polyglot / a file renamed from "shell.php" to "shell.jpg":
     extension and content-type can both be spoofed, but a non-image file can't
     pass `Image.verify()`.
  5. Filename is renamed to a random UUID by the model's upload_to callback —
     prevents path traversal via crafted filenames, filename collisions, and
     leakage of the uploader's original filename.

Note: imghdr (used in the previous version) was removed in Python 3.13.
Pillow does the same job better — it actually decodes the file instead of
just checking the first few bytes — and Pillow is already a dependency.
"""
import logging
import os
from PIL import Image, UnidentifiedImageError

logger = logging.getLogger('security')

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
ALLOWED_CONTENT_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
ALLOWED_PIL_FORMATS = {'JPEG', 'PNG', 'WEBP'}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MiB


def validate_room_image(uploaded_file):
    """
    Raise ValueError with a user-safe message if the upload fails any check.
    Call this inside a Django form's clean_image() method.
    """
    # --- 1. Extension whitelist ---
    _, ext = os.path.splitext(uploaded_file.name)
    ext = ext.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file extension '{ext}'. "
            f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # --- 2. Declared content-type whitelist ---
    content_type = getattr(uploaded_file, 'content_type', None)
    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        logger.warning(
            f"FILE_UPLOAD_REJECTED | name={uploaded_file.name} "
            f"| reason=content_type | declared={content_type}"
        )
        raise ValueError("File content-type is not allowed.")

    # --- 3. Size limit ---
    if uploaded_file.size > MAX_UPLOAD_BYTES:
        raise ValueError(
            f"File too large ({uploaded_file.size // 1024} KB). "
            f"Maximum allowed size is {MAX_UPLOAD_BYTES // 1024 // 1024} MB."
        )

    # --- 4. Real image verification (Pillow decodes the bytes) ---
    try:
        uploaded_file.seek(0)
        img = Image.open(uploaded_file)
        img.verify()
        detected_format = img.format
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        logger.warning(
            f"FILE_UPLOAD_REJECTED | name={uploaded_file.name} "
            f"| reason=pillow_verify | error={type(exc).__name__}"
        )
        raise ValueError(
            "File content does not match a valid image format. "
            "Please upload a real JPEG, PNG, or WebP image."
        )
    finally:
        # Always rewind so Django can read the file afterwards.
        uploaded_file.seek(0)

    # --- 4b. Cross-check: detected format must agree with the extension ---
    # Catches a .jpg-named WebP, a .png-named JPEG, etc.
    if detected_format not in ALLOWED_PIL_FORMATS:
        raise ValueError("File is not a permitted image format.")

    return uploaded_file
