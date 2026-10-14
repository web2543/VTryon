from app.core.interfaces import ImageGenerator

_generator: ImageGenerator | None = None


def set_generator(generator: ImageGenerator) -> None:
    """Store the generator singleton (called from lifespan)."""
    global _generator
    _generator = generator


def get_generator() -> ImageGenerator:
    if _generator is None:
        raise RuntimeError("Generator not initialized. Did you forget the lifespan?")
    return _generator
