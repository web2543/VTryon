import base64
import io

import pytest
from fastapi.testclient import TestClient

from app.api.deps import set_generator
from app.services.dummy_generator import DummyGenerator
from app.main import create_app

client = TestClient(create_app())


@pytest.fixture(autouse=True)
def _setup_generator():
    """Ensure DummyGenerator is active for every test."""
    set_generator(DummyGenerator(model=None))
    yield


# ── Health ──────────────────────────────────────────────


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# ── Happy path ──────────────────────────────────────────


def _make_b64(size: int = 64) -> str:
    """Create a small solid-color PNG as a base64 data URI."""
    from PIL import Image

    img = Image.new("RGBA", (size, size), (255, 0, 0, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def test_generate_happy_path():
    payload = {
        "base_image": _make_b64(),
        "cloth_image": _make_b64(size=32),
    }
    resp = client.post("/api/generate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "gen_image" in data
    assert data["gen_image"].startswith("data:image/png;base64,")


# ── Error cases ─────────────────────────────────────────


def test_generate_missing_field():
    resp = client.post(
        "/api/generate",
        json={"base_image": _make_b64()},
    )
    assert resp.status_code == 422


def test_generate_invalid_base64():
    resp = client.post(
        "/api/generate",
        json={
            "base_image": "not-base64!!",
            "cloth_image": _make_b64(),
        },
    )
    assert resp.status_code == 400


def test_generate_invalid_image():
    import base64 as b64

    bad = b64.b64encode(b"not-an-image").decode()
    resp = client.post(
        "/api/generate",
        json={
            "base_image": f"data:image/png;base64,{bad}",
            "cloth_image": _make_b64(),
        },
    )
    assert resp.status_code == 400


# ── Contract test ───────────────────────────────────────


def test_generator_returns_valid_png():
    """Any ImageGenerator subclass must return valid PNG bytes."""
    from PIL import Image

    gen = DummyGenerator(model=None)

    def make_raw_png(size=64):
        img = Image.new("RGBA", (size, size), (255, 0, 0, 255))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    result = gen.gen(make_raw_png(), make_raw_png(32))
    # Verify it's valid PNG bytes
    img = Image.open(io.BytesIO(result))
    assert img.format == "PNG"
