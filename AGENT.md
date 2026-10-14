# AGENT.md — Virtual Try-On Web App

## What this project is

A FastAPI + vanilla HTML/CSS/JS web app for virtual try-on. Users upload a **base person image** and a **cloth image**; the app returns a combined try-on result as a **PNG** image.

## How to run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload          # dev server
python -m pytest tests/ -v             # run tests
```

Open [http://localhost:8000](http://localhost:8000) in a browser.

## Project layout

```
app/
├── main.py                 # App factory, lifespan (model load), static mount
├── config.py               # pydantic-settings, env vars (.env supported)
├── api/
│   ├── routes.py           # POST /api/generate, GET /health
│   └── deps.py             # Singleton generator provider (get_generator / set_generator)
├── core/
│   ├── interfaces.py       # ImageGenerator ABC — gen(base, cloth, pant) -> PNG bytes
│   └── errors.py           # Custom HTTP exceptions + FastAPI error handlers
├── services/
│   ├── dummy_generator.py  # Dev stub: composites cloth+pant onto base, returns PNG
│   └── my_generator.py     # Real model placeholder (NotImplemented)
├── schemas.py              # Pydantic GenerateRequest / GenerateResponse
├── utils/
│   └── image.py            # decode_base64, validate_image, encode_base64
└── static/
    ├── index.html          # Three file inputs, Generate button, result panel
    ├── style.css           # Responsive layout
    └── app.js              # FileReader → canvas downscale → fetch → display
tests/
├── test_api.py             # 6 tests: health, happy path, errors, contract
└── test_image_utils.py     # 7 tests: base64 helpers, validation, encoding
requirements.txt
README.md
plan.md
```

## Architecture decisions

### 1. ABC on raw bytes, base64 at the edges

`ImageGenerator.gen(base, cloth) -> bytes` works on raw bytes (PNG-encoded). Base64 encoding/decoding and data-URI prefix stripping live in `utils/image.py` and the API route only. This keeps the generator model-agnostic.

### 2. Singleton generator via DI

- `deps.py` holds a module-level `_generator` variable.
- `main.py`'s `lifespan` calls `set_generator(DummyGenerator(None))` once at startup.
- `routes.py` declares `generator: ImageGenerator = Depends(get_generator)`.
- Tests override with `app.dependency_overrides[get_generator] = lambda: DummyGenerator(None)` or call `set_generator` directly.

### 3. Output format is PNG

Both input and output are PNG. The `DummyGenerator` saves the composite as PNG; the route base64-encodes those PNG bytes into a `data:image/png;base64,...` URI.

### 4. Frontend is vanilla JS (no framework)

- Two inputs: base image + cloth image
- `FileReader.readAsDataURL` reads files.
- A canvas element downscales images client-side (max 2048 px) to keep payloads small.
- `fetch('/api/generate', ...)` sends a JSON body with two base64 strings.
- Result is rendered as `<img src="data:image/png;base64,...">` with a download link.

### 5. Error handling

Custom exceptions (`InvalidImageError`, `ImageTooLargeError`, `GenerationError`) map to 400, 413, 500 respectively. Handlers in `core/errors.py` return JSON responses.

## Key files to know

| File | What to change here |
|------|---------------------|
| `app/services/my_generator.py` | Implement real model inference in `gen()` |
| `app/main.py` | Swap `DummyGenerator` → your generator in `lifespan` |
| `app/api/routes.py` | API contract (request/response shape) |
| `app/utils/image.py` | Size limits, base64 helpers, validation |
| `app/config.py` | Env-var defaults (`MAX_IMAGE_SIZE`, `MAX_IMAGE_FILE_SIZE`) |
| `app/static/app.js` | Frontend logic, fetch call, error display |

## Adding a real model

1. Edit `app/services/my_generator.py` — implement `gen(self, base, cloth) -> bytes` to return **PNG-encoded bytes**.
2. In `app/main.py`'s `lifespan`, replace:
   ```python
   set_generator(DummyGenerator(model=None))
   ```
   with:
   ```python
   set_generator(MyGenerator(model=load_your_model()))
   ```
3. Run `pytest tests/` to verify nothing broke.

## Testing

```bash
python -m pytest tests/ -v
```

- `test_api.py` — FastAPI `TestClient`, covers health, happy path, missing fields, invalid base64, invalid image, and a generator contract test.
- `test_image_utils.py` — Unit tests for base64 decode/encode, image validation, and size limits.

## Configuration (env vars)

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_PATH` | `models/virtual_tryon` | Path to model weights |
| `MAX_IMAGE_SIZE` | `2048` | Max image dimension (px) |
| `MAX_IMAGE_FILE_SIZE` | `10485760` | Max file size (10 MB) |
| `OUTPUT_FORMAT` | `PNG` | Output image format |

Read from `.env` or set as environment variables. `config.py` uses `pydantic-settings`.

## Common pitfalls

- **Do not pass raw bytes directly to `Image.open()`** — wrap in `io.BytesIO()` first (e.g., `Image.open(io.BytesIO(data))`).
- **Frontend event handlers must be functions, not Promises** — don't mark wrapper functions as `async` if they return a callback (see `app/static/app.js` `handleFileSelect`).
- **Generator must return PNG bytes** — the route base64-encodes whatever `gen()` returns; it doesn't re-encode.
- **Tests call `set_generator()` directly** — don't rely on `app.dependency_overrides` unless you need it.
