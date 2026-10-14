from app.core.interfaces import ImageGenerator


class MyGenerator(ImageGenerator):
    """Real model-backed implementation.

    Replace the body of `gen` with your actual model inference logic.
    The model is expected to accept (base, cloth, pant) and produce a
    virtual try-on result image.
    """

    def gen(self, base: bytes, cloth: bytes) -> bytes:
        # TODO: integrate your virtual try-on model here.
        # Example skeleton:
        #   from . import my_model
        #   result = my_model.infer(base, cloth, pant)
        #   return result.tobytes()
        raise NotImplementedError(
            "MyGenerator is not implemented yet. "
            "Provide model inference logic in `gen()`."
        )
