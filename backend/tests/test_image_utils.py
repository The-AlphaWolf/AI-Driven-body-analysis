"""Image validation, decoding, and thumbnail generation."""
import io

import cv2
import numpy as np
import pytest
from PIL import Image
from werkzeug.datastructures import FileStorage

from app.utils.image_utils import MAX_DIMENSION, make_thumbnail, preprocess_image, validate_image


def encode(width=400, height=300, fmt="JPEG", colour=(120, 90, 70)):
    """Produce real encoded image bytes of the given size."""
    image = Image.new("RGB", (width, height), colour)
    buffer = io.BytesIO()
    image.save(buffer, format=fmt)
    return buffer.getvalue()


def upload(filename="photo.jpg", content_type="image/jpeg", data=None):
    return FileStorage(
        stream=io.BytesIO(data if data is not None else encode()),
        filename=filename,
        content_type=content_type,
    )


# ── validate_image ─────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    ("filename", "content_type"),
    [
        ("photo.jpg", "image/jpeg"),
        ("photo.jpeg", "image/jpeg"),
        ("photo.PNG", "image/png"),
        ("photo.webp", "image/webp"),
    ],
)
def test_accepts_allowed_image_types(filename, content_type):
    assert validate_image(upload(filename, content_type)) is None


def test_rejects_a_missing_file():
    assert validate_image(None) is not None
    assert validate_image(upload(filename="")) is not None


def test_rejects_a_disallowed_extension():
    assert validate_image(upload("payload.svg", "image/jpeg")) is not None


def test_rejects_a_mismatched_content_type():
    """An .jpg name with a script content type must not slip through."""
    assert validate_image(upload("photo.jpg", "text/html")) is not None


# ── preprocess_image ───────────────────────────────────────────────────────

def test_decodes_to_a_bgr_array():
    image = preprocess_image(encode(width=200, height=100))
    assert image is not None
    assert image.shape == (100, 200, 3)


def test_converts_rgb_to_bgr():
    """OpenCV consumers downstream assume BGR channel order."""
    red_rgb = encode(width=10, height=10, fmt="PNG", colour=(255, 0, 0))
    image = preprocess_image(red_rgb)
    blue, green, red = image[0, 0]
    assert red > 200 and blue < 50 and green < 50


def test_downscales_oversized_images():
    image = preprocess_image(encode(width=4000, height=2000))
    assert max(image.shape[:2]) == MAX_DIMENSION
    # Aspect ratio preserved
    assert image.shape[1] / image.shape[0] == pytest.approx(2.0, abs=0.01)


def test_leaves_small_images_alone():
    image = preprocess_image(encode(width=640, height=480))
    assert image.shape[:2] == (480, 640)


def test_handles_png_and_webp():
    assert preprocess_image(encode(fmt="PNG")) is not None
    assert preprocess_image(encode(fmt="WEBP")) is not None


@pytest.mark.parametrize("payload", [b"", b"not an image at all", None])
def test_returns_none_for_undecodable_input(payload):
    assert preprocess_image(payload) is None


# ── make_thumbnail ─────────────────────────────────────────────────────────

def test_produces_decodable_jpeg_bytes():
    image = preprocess_image(encode(width=800, height=600))
    thumb = make_thumbnail(image)

    assert isinstance(thumb, bytes)
    decoded = cv2.imdecode(np.frombuffer(thumb, np.uint8), cv2.IMREAD_COLOR)
    assert decoded.shape == (200, 200, 3)


def test_thumbnail_is_small_enough_to_store_inline():
    """Thumbnails live in a database column — they must stay tiny."""
    image = preprocess_image(encode(width=2000, height=2000))
    assert len(make_thumbnail(image)) < 30_000


def test_centre_crops_rather_than_squashing():
    """
    A wide image is cropped to its middle square. Painting the centre a
    distinct colour proves the crop kept the middle, not an edge.
    """
    canvas = np.zeros((100, 300, 3), dtype=np.uint8)
    canvas[:, 100:200] = (0, 0, 255)  # BGR red down the central square

    decoded = cv2.imdecode(
        np.frombuffer(make_thumbnail(canvas), np.uint8), cv2.IMREAD_COLOR
    )
    blue, green, red = decoded[100, 100]
    assert red > 200 and blue < 60


def test_returns_none_for_a_bad_array():
    assert make_thumbnail(np.array([])) is None
