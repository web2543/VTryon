from abc import ABC, abstractmethod


class ImageGenerator(ABC):
    def __init__(self, model):
        self.model = model

    @abstractmethod
    def gen(self, base: bytes, cloth: bytes) -> bytes:
        """Return the generated image as PNG bytes."""
