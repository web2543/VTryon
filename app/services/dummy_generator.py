import io

from PIL import Image

from app.core.interfaces import ImageGenerator


class DummyGenerator(ImageGenerator):
    """Stub implementation that composites the inputs into a simple result."""

    def gen(self, base: bytes, cloth: bytes) -> bytes:
        """Create a placeholder result by overlaying cloth onto the base."""
        base_img = Image.open(io.BytesIO(base)).convert("RGBA")
        cloth_img = Image.open(io.BytesIO(cloth)).convert("RGBA")

        w, h = base_img.size
        result = base_img.copy()
        cloth_resized = cloth_img.resize((w, h))
        result.paste(cloth_resized, (0, 0), mask=cloth_resized.split()[3])

        buf = io.BytesIO()
        result.save(buf, format="PNG")
        return buf.getvalue()
