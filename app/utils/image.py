import base64
import io

from PIL import Image

from app.config import settings
from app.core.errors import ImageTooLargeError, InvalidImageError


def _strip_prefix(data: str) -> str:
    """Remove a 'data:...;base64,' prefix if present."""
    if "," in data:
        # Only strip if it looks like a data URI
        prefix, _, rest = data.partition(",")
        if prefix.startswith("data:"):
            return rest
    return data


def decode_base64(data: str) -> bytes:
    """Decode a base64-encoded image string to raw bytes."""
    try:
        cleaned = _strip_prefix(data)
        return base64.b64decode(cleaned)
    except Exception as e:
        raise InvalidImageError(f"Invalid base64 data: {e}")


def validate_image(data: bytes) -> Image.Image:
    """Validate that bytes form a real image and enforce size limits."""
    if len(data) > settings.max_image_file_size:
        raise ImageTooLargeError(settings.max_image_file_size)

    try:
        img = Image.open(io.BytesIO(data))
        img.load()  # Force full decode
        # Check dimensions
        w, h = img.size
        if w > settings.max_image_size or h > settings.max_image_size:
            raise InvalidImageError(
                f"Image too large ({w}x{h}). Max dimension is {settings.max_image_size}"
            )
        return img
    except Image.UnidentifiedImageError:
        raise InvalidImageError("Unable to identify image file")
    except Exception as e:
        if isinstance(e, (InvalidImageError, ImageTooLargeError)):
            raise
        raise InvalidImageError(f"Invalid image data: {e}")


def encode_base64(img: Image.Image, fmt: str | None = None) -> str:
    """Encode a PIL Image to a base64 data URI string."""
    fmt = fmt or settings.output_format
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    mime = f"image/{fmt.lower()}"
    return f"data:{mime};base64,{b64}"
