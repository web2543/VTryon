from ast import Raise

from app.core.errors import GenerationError
from app.core.interfaces import ImageGenerator
import torch
from diffusers import QwenImage21Pipeline
from PIL import Image
import io



class QwenImageGenerator(ImageGenerator):
    pipe: QwenImage21Pipeline
    edit_prompt = "Change outfit to input image."
    def __init__(self, model):
        super().__init__(model)
        self.pipe = QwenImage21Pipeline.from_pretrained(
            "Qwen/Qwen-Image-2.1-Turbo",
            dtype=torch.bfloat16,
        )
        self.pipe.enable_sequential_cpu_offload()

    def gen(self, base: bytes, cloth: bytes) -> bytes:
        base_img = Image.open(io.BytesIO(base)).convert("RGBA")
        cloth_img = Image.open(io.BytesIO(cloth)).convert("RGBA")

        input_image = [base_img,cloth_img]
        try:
            image = self.pipe(
            prompt=self.edit_prompt,
            image=input_image,
            use_kv_cache=True,
            generator=torch.Generator("cpu").manual_seed(20261009),
        ).images[0]
        except Exception as e:
            raise GenerationError("Something Fuck")

        buf = io.BytesIO()
        image.save(buf, format="PNG")

        return buf.getvalue()
