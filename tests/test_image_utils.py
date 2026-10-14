import base64
import io

import pytest

from app.utils.image import decode_base64, encode_base64, validate_image
from app.core.errors import InvalidImageError, ImageTooLargeError
from app.config import settings


def _make_png(width: int = 64, height: int = 64) -> bytes:
    from PIL import Image

    img = Image.new("RGBA", (width, height), (128, 64, 192, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ── decode_base64 ───────────────────────────────────────


def test_decode_plain_base64():
    raw = _make_png()
    b64 = base64.b64encode(raw).decode()
    assert decode_base64(b64) == raw


def test_decode_data_uri():
    raw = _make_png()
    b64 = base64.b64encode(raw).decode()
    uri = f"data:image/png;base64,{b64}"
    assert decode_base64(uri) == raw


def test_decode_invalid_base64():
    with pytest.raises(InvalidImageError):
        decode_base64("!!!not-valid-base64!!!")


# ── validate_image ──────────────────────────────────────


def test_validate_valid_image():
    raw = _make_png()
    img = validate_image(raw)
    assert img.size == (64, 64)


def test_validate_invalid_bytes():
    with pytest.raises(InvalidImageError):
        validate_image(b"this is not an image")


def test_validate_too_large():
    # Temporarily lower the limit
    original = settings.max_image_file_size
    try:
        settings.max_image_file_size = 10
        with pytest.raises(ImageTooLargeError):
            validate_image(_make_png(256, 256))
    finally:
        settings.max_image_file_size = original


# ── encode_base64 ───────────────────────────────────────


def test_encode_base64():
    img = Image.new("RGBA", (10, 10), (255, 0, 0, 128))
    data_uri = encode_base64(img)
    assert data_uri.startswith("data:image/png;base64,")
    b64 = data_uri.split(",", 1)[1]
    raw = base64.b64decode(b64)
    reloaded = Image.open(io.BytesIO(raw))
    assert reloaded.size == (10, 10)


from PIL import Image
