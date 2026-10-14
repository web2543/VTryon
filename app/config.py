from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_path: str = "models/virtual_tryon"
    max_image_size: int = 2048  # max dimension in pixels
    max_image_file_size: int = 10 * 1024 * 1024  # 10 MB
    output_format: str = "PNG"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
