"""
The /api/analysis/analyze endpoint.

The vision services are stubbed. Running the real models here would add
seconds per test and require photographs of real people in the repo; the
route's job is validation, orchestration, and persistence, which is what
these cover.
"""
import io

import pytest
from PIL import Image

from app.models.analysis import Analysis

FACE_RESULT = {"shape": "heart", "confidence": 0.88}
SKIN_RESULT = {
    "depth": "medium",
    "undertone": "cool",
    "hex_color": "#b07d62",
    "confidence": 0.71,
    "low_confidence_flag": False,
}
BODY_RESULT = {"shape": "pear", "confidence": 0.66}


def photo(name="face.jpg"):
    buffer = io.BytesIO()
    Image.new("RGB", (300, 300), (150, 110, 90)).save(buffer, format="JPEG")
    buffer.seek(0)
    return (buffer, name)


@pytest.fixture
def vision(monkeypatch):
    """Stub the three analysis services. Mutate the dict to change results."""
    state = {"face": FACE_RESULT, "skin": SKIN_RESULT, "body": BODY_RESULT}

    monkeypatch.setattr("app.routes.analysis.analyze_face", lambda img: state["face"])
    monkeypatch.setattr("app.routes.analysis.analyze_skin_tone", lambda img: state["skin"])
    monkeypatch.setattr("app.routes.analysis.analyze_body", lambda img: state["body"])
    return state


def test_analyze_requires_auth(client):
    assert client.post("/api/analysis/analyze").status_code == 401


def test_analyze_requires_at_least_one_image(client, auth, vision):
    response = client.post("/api/analysis/analyze", headers=auth)
    assert response.status_code == 422


def test_analyze_rejects_a_disallowed_file_type(client, auth, vision):
    response = client.post(
        "/api/analysis/analyze",
        headers=auth,
        data={"face_image": (io.BytesIO(b"<svg/>"), "payload.svg")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 422


def test_analyze_rejects_undecodable_image_bytes(client, auth, vision):
    response = client.post(
        "/api/analysis/analyze",
        headers=auth,
        data={"face_image": (io.BytesIO(b"definitely not a jpeg"), "face.jpg")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 422


def test_analyze_with_a_face_photo_returns_a_full_result(client, auth, vision):
    response = client.post(
        "/api/analysis/analyze",
        headers=auth,
        data={"face_image": photo()},
        content_type="multipart/form-data",
    )
    assert response.status_code == 201

    analysis = response.get_json()["analysis"]
    assert analysis["face_analysis"]["shape"] == "heart"
    assert analysis["skin_analysis"]["undertone"] == "cool"
    assert analysis["body_analysis"] is None
    assert analysis["recommendations"]


def test_analyze_with_a_body_photo_only(client, auth, vision):
    response = client.post(
        "/api/analysis/analyze",
        headers=auth,
        data={"body_image": photo("body.jpg")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 201

    analysis = response.get_json()["analysis"]
    assert analysis["body_analysis"]["shape"] == "pear"
    assert analysis["face_analysis"] is None


def test_skin_is_not_analysed_when_no_face_is_found(client, auth, vision):
    """Skin sampling relies on face landmarks — it must not run without them."""
    vision["face"] = None

    response = client.post(
        "/api/analysis/analyze",
        headers=auth,
        data={"face_image": photo(), "body_image": photo("body.jpg")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 201
    assert response.get_json()["analysis"]["skin_analysis"] is None


def test_analyze_fails_cleanly_when_nothing_is_detected(client, auth, vision):
    vision["face"] = None
    vision["body"] = None

    response = client.post(
        "/api/analysis/analyze",
        headers=auth,
        data={"face_image": photo()},
        content_type="multipart/form-data",
    )
    assert response.status_code == 422
    assert "Could not detect" in response.get_json()["message"]


def test_analyze_persists_the_result(client, auth, user, vision):
    client.post(
        "/api/analysis/analyze",
        headers=auth,
        data={"face_image": photo()},
        content_type="multipart/form-data",
    )

    stored = Analysis.query.one()
    assert stored.user_id == user.id
    assert stored.face_shape == "heart"
    assert stored.recommendations


def test_analyze_stores_a_thumbnail_in_the_database(client, auth, vision):
    client.post(
        "/api/analysis/analyze",
        headers=auth,
        data={"face_image": photo()},
        content_type="multipart/form-data",
    )

    stored = Analysis.query.one()
    assert stored.thumbnail
    assert stored.thumbnail.startswith(b"\xff\xd8")  # JPEG magic bytes


def test_stored_analysis_is_immediately_readable_back(client, auth, vision):
    created = client.post(
        "/api/analysis/analyze",
        headers=auth,
        data={"face_image": photo()},
        content_type="multipart/form-data",
    ).get_json()["analysis"]

    fetched = client.get(f"/api/history/{created['id']}", headers=auth)
    assert fetched.status_code == 200
    assert fetched.get_json()["analysis"]["face_analysis"]["shape"] == "heart"


def test_oversized_upload_is_rejected(client, auth, app, vision):
    app.config["MAX_CONTENT_LENGTH"] = 1024

    response = client.post(
        "/api/analysis/analyze",
        headers=auth,
        data={"face_image": (io.BytesIO(b"x" * 5000), "face.jpg")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 413
