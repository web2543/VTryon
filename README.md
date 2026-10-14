# Virtual Try-On Web App

A FastAPI-based web application for virtual try-on. Upload a base person image and a cloth image to generate a combined try-on result.

## Quick Start

```bash
# 1. Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
uvicorn app.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

## API

| Method | Path              | Description                       |
|--------|-------------------|-----------------------------------|
| GET    | `/`               | Frontend page                     |
| GET    | `/health`         | Health check                      |
| POST   | `/api/generate`   | Generate a try-on image           |

### POST `/api/generate`

**Request body:**

```json
{
  "base_image": "data:image/png;base64,...",
  "cloth_image": "data:image/png;base64,..."
}
```

**Response:**

```json
{
  "gen_image": "data:image/png;base64,..."
}
```

## Configuration

Set via environment variables or a `.env` file:

| Variable             | Default            | Description                         |
|----------------------|--------------------|-------------------------------------|
| `MODEL_PATH`         | `models/virtual_tryon` | Path to the model weights        |
| `MAX_IMAGE_SIZE`     | `2048`             | Max image dimension in pixels       |
| `MAX_IMAGE_FILE_SIZE`| `10485760`         | Max file size in bytes (10 MB)      |
| `OUTPUT_FORMAT`      | `PNG`              | Output image format                 |

## Running Tests

```bash
pytest tests/ -v
```

## Project Structure

```
app/
├── main.py                 # App factory, lifespan, static mount
├── config.py               # Settings (env vars)
├── api/
│   ├── routes.py           # POST /api/generate, GET /health
│   └── deps.py             # Generator DI provider
├── core/
│   ├── interfaces.py       # ImageGenerator ABC
│   └── errors.py           # Custom exceptions + handlers
├── services/
│   ├── dummy_generator.py  # Stub (composites inputs)
│   └── my_generator.py     # Real model (placeholder)
├── schemas.py              # Pydantic request/response models
├── utils/
│   └── image.py            # Base64 helpers, image validation
└── static/
    ├── index.html
    ├── style.css
    └── app.js
tests/
requirements.txt
```

## Adding a Real Model

1. Implement a class that subclasses `ImageGenerator` in `app/services/my_generator.py`.
2. Implement the `gen(base, cloth, pant) -> bytes` method to return PNG-encoded bytes.
3. Update `app/main.py`'s `lifespan` to instantiate your generator instead of `DummyGenerator`.

```python
# In main.py lifespan:
from app.services.my_generator import MyGenerator
set_generator(MyGenerator(model=load_model()))
```
