from fastapi import APIRouter, Depends

from app.api.deps import get_generator
from app.core.errors import GenerationError, InvalidImageError, ImageTooLargeError
from app.core.interfaces import ImageGenerator
from app.schemas import GenerateRequest, GenerateResponse
from app.utils.image import decode_base64, encode_base64, validate_image

router = APIRouter()


@router.post("/api/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest, generator: ImageGenerator = Depends(get_generator)):
    """Generate a virtual try-on image from base, cloth, and pant images."""
    try:
        base_bytes = decode_base64(req.base_image)
        cloth_bytes = decode_base64(req.cloth_image)

        validate_image(base_bytes)
        validate_image(cloth_bytes)

        result_png_bytes = generator.gen(base_bytes, cloth_bytes)

        # Generator returns PNG-encoded bytes; encode to base64 data URI.
        import base64
        gen_image_b64 = f"data:image/png;base64,{base64.b64encode(result_png_bytes).decode('utf-8')}"
    except InvalidImageError:
        raise
    except ImageTooLargeError:
        raise
    except GenerationError:
        raise
    except Exception as e:
        raise GenerationError(f"Generation failed: {e}")

    return GenerateResponse(gen_image=gen_image_b64)


@router.get("/health")
def health():
    return {"status": "ok"}
