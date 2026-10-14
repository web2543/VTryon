from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    base_image: str = Field(..., description="Base person image in base64")
    cloth_image: str = Field(..., description="Cloth image in base64")


class GenerateResponse(BaseModel):
    gen_image: str = Field(..., description="Generated image in base64")
