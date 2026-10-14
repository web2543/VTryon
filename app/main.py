from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.deps import set_generator
from app.services.dummy_generator import DummyGenerator
from app.services.qwen_image_generator import QwenImageGenerator
from app.api.routes import router
from app.core.errors import (
    GenerationError,
    ImageTooLargeError,
    InvalidImageError,
    generation_error_handler,
    image_too_large_handler,
    invalid_image_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the model once (here we use the dummy generator for dev)
    set_generator(QwenImageGenerator(model=None))
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Virtual Try-On",
        lifespan=lifespan,
    )

    # Register error handlers
    app.add_exception_handler(InvalidImageError, invalid_image_handler)
    app.add_exception_handler(ImageTooLargeError, image_too_large_handler)
    app.add_exception_handler(GenerationError, generation_error_handler)

    # Mount static files
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    # Include API routes
    app.include_router(router)

    # Serve index.html at root
    @app.get("/", response_class=FileResponse)
    def index():
        return "app/static/index.html"

    return app


app = create_app()
