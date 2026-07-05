"""
Image validation, preprocessing, and thumbnail utilities.
"""
import os
import cv2
import numpy as np
from PIL import Image, ExifTags
import io

# Allowed MIME types and their extensions
ALLOWED_TYPES = {
    "image/jpeg": [".jpg", ".jpeg"],
    "image/png": [".png"],
    "image/webp": [".webp"],
}
MAX_DIMENSION = 2048  # Resize if larger than this


def validate_image(file) -> str | None:
    """
    Validate an uploaded image file.

    Checks:
      - File is present and has a filename
      - File extension matches allowed types
      - Content-type header matches allowed MIME types

    Returns an error message string if invalid, None if valid.
    """
    if not file or not file.filename:
        return "No file provided"

    # Check extension
    _, ext = os.path.splitext(file.filename.lower())
    valid_extensions = [e for exts in ALLOWED_TYPES.values() for e in exts]
    if ext not in valid_extensions:
        return f"Invalid file type '{ext}'. Allowed: {', '.join(valid_extensions)}"

    # Check content type
    if file.content_type not in ALLOWED_TYPES:
        return f"Invalid content type '{file.content_type}'"

    return None


def preprocess_image(image_bytes: bytes) -> np.ndarray | None:
    """
    Decode image bytes into an OpenCV BGR ndarray.

    Handles:
      - Decoding from JPEG/PNG/WebP bytes
      - EXIF orientation correction (rotated phone photos)
      - Resizing if dimensions exceed MAX_DIMENSION

    Returns the preprocessed image as a numpy array, or None on failure.
    """
    if not image_bytes:
        return None

    try:
        # Use PIL to handle EXIF orientation, then convert to OpenCV
        pil_image = Image.open(io.BytesIO(image_bytes))

        # ── Fix EXIF orientation ───────────────────────────────────────
        try:
            exif = pil_image._getexif()
            if exif:
                orientation_key = None
                for key, val in ExifTags.TAGS.items():
                    if val == "Orientation":
                        orientation_key = key
                        break
                if orientation_key and orientation_key in exif:
                    orientation = exif[orientation_key]
                    if orientation == 3:
                        pil_image = pil_image.rotate(180, expand=True)
                    elif orientation == 6:
                        pil_image = pil_image.rotate(270, expand=True)
                    elif orientation == 8:
                        pil_image = pil_image.rotate(90, expand=True)
        except (AttributeError, KeyError):
            pass  # No EXIF data, continue

        # ── Convert to RGB then BGR for OpenCV ─────────────────────────
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")

        image = np.array(pil_image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # ── Resize if too large ────────────────────────────────────────
        h, w = image.shape[:2]
        if max(h, w) > MAX_DIMENSION:
            scale = MAX_DIMENSION / max(h, w)
            new_w, new_h = int(w * scale), int(h * scale)
            image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

        return image

    except Exception:
        return None


def save_thumbnail(image: np.ndarray, folder: str, name: str) -> str | None:
    """
    Create and save a 200×200 JPEG thumbnail.

    Args:
        image: OpenCV BGR image
        folder: Directory to save into
        name: Base filename (without extension)

    Returns the full path to the saved thumbnail, or None on failure.
    """
    try:
        os.makedirs(folder, exist_ok=True)
        h, w = image.shape[:2]

        # Center crop to square
        size = min(h, w)
        y_start = (h - size) // 2
        x_start = (w - size) // 2
        cropped = image[y_start:y_start + size, x_start:x_start + size]

        # Resize to 200×200
        thumbnail = cv2.resize(cropped, (200, 200), interpolation=cv2.INTER_AREA)

        path = os.path.join(folder, f"{name}.jpg")
        cv2.imwrite(path, thumbnail, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return path

    except Exception:
        return None
