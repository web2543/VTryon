from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class InvalidImageError(HTTPException):
    def __init__(self, detail: str = "Invalid image data"):
        super().__init__(status_code=400, detail=detail)


class ImageTooLargeError(HTTPException):
    def __init__(self, limit_bytes: int):
        super().__init__(
            status_code=413,
            detail=f"Image exceeds maximum size of {limit_bytes} bytes",
        )


class GenerationError(HTTPException):
    def __init__(self, detail: str = "Image generation failed"):
        super().__init__(status_code=500, detail=detail)


async def invalid_image_handler(request: Request, exc: InvalidImageError):
    return JSONResponse(status_code=400, content={"error": exc.detail})


async def image_too_large_handler(request: Request, exc: ImageTooLargeError):
    return JSONResponse(status_code=413, content={"error": exc.detail})


async def generation_error_handler(request: Request, exc: GenerationError):
    return JSONResponse(status_code=500, content={"error": exc.detail})
