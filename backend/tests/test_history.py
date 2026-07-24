"""History routes: listing, ownership, deletion, thumbnails."""
import pytest

from app.extensions import db
from app.models.analysis import Analysis
from app.models.user import User


def make_analysis(user_id, **overrides):
    fields = {
        "user_id": user_id,
        "face_shape": "oval",
        "face_confidence": 0.82,
        "skin_depth": "medium",
        "skin_undertone": "warm",
        "skin_hex_color": "#c68642",
        "body_shape": "hourglass",
        "body_confidence": 0.77,
        "recommendations": [{"category": "colors", "recommendation": "Camel"}],
    }
    fields.update(overrides)
    analysis = Analysis(**fields)
    db.session.add(analysis)
    db.session.commit()
    return analysis


def test_history_requires_auth(client):
    assert client.get("/api/history").status_code == 401


def test_history_is_empty_for_a_new_account(client, auth):
    body = client.get("/api/history", headers=auth).get_json()
    assert body == {"analyses": [], "total": 0, "page": 1, "pages": 0}


def test_history_lists_the_users_analyses(client, auth, user):
    make_analysis(user.id)
    make_analysis(user.id)

    body = client.get("/api/history", headers=auth).get_json()
    assert body["total"] == 2
    assert len(body["analyses"]) == 2


def test_history_paginates(client, auth, user):
    for _ in range(5):
        make_analysis(user.id)

    body = client.get("/api/history?page=2&per_page=2", headers=auth).get_json()
    assert body["page"] == 2
    assert body["pages"] == 3
    assert len(body["analyses"]) == 2


def test_history_caps_page_size(client, auth, user):
    """per_page is clamped so a caller cannot ask for the whole table."""
    for _ in range(3):
        make_analysis(user.id)

    body = client.get("/api/history?per_page=9999", headers=auth).get_json()
    assert len(body["analyses"]) == 3  # clamped to 50, only 3 exist


def test_history_excludes_other_users_analyses(client, auth, user):
    other = User(email="other@example.com")
    other.set_password("password123")
    db.session.add(other)
    db.session.commit()
    make_analysis(other.id)

    body = client.get("/api/history", headers=auth).get_json()
    assert body["total"] == 0


def test_get_analysis_returns_full_detail(client, auth, user):
    analysis = make_analysis(user.id)

    body = client.get(f"/api/history/{analysis.id}", headers=auth).get_json()
    assert body["analysis"]["face_analysis"]["shape"] == "oval"
    assert body["analysis"]["skin_analysis"]["undertone"] == "warm"
    assert body["analysis"]["body_analysis"]["shape"] == "hourglass"
    assert body["analysis"]["recommendations"][0]["category"] == "colors"


def test_get_another_users_analysis_is_404_not_403(client, auth, user):
    """Ownership failures must not confirm that the id exists."""
    other = User(email="other@example.com")
    other.set_password("password123")
    db.session.add(other)
    db.session.commit()
    theirs = make_analysis(other.id)

    assert client.get(f"/api/history/{theirs.id}", headers=auth).status_code == 404


def test_delete_removes_the_analysis(client, auth, user):
    analysis = make_analysis(user.id)

    assert client.delete(f"/api/history/{analysis.id}", headers=auth).status_code == 200
    assert Analysis.query.count() == 0


def test_delete_another_users_analysis_is_refused(client, auth, user):
    other = User(email="other@example.com")
    other.set_password("password123")
    db.session.add(other)
    db.session.commit()
    theirs = make_analysis(other.id)

    assert client.delete(f"/api/history/{theirs.id}", headers=auth).status_code == 404
    assert Analysis.query.count() == 1


def test_thumbnail_is_served_from_the_database(client, auth, user):
    analysis = make_analysis(user.id, thumbnail=b"\xff\xd8\xff\xe0 not-a-real-jpeg")

    response = client.get(f"/api/history/{analysis.id}/thumbnail", headers=auth)
    assert response.status_code == 200
    assert response.mimetype == "image/jpeg"
    assert response.data == b"\xff\xd8\xff\xe0 not-a-real-jpeg"


def test_thumbnail_requires_auth(client, auth, user):
    """
    The client once passed the JWT as a query parameter. The endpoint reads
    headers only, so that never worked — this pins the header requirement.
    """
    analysis = make_analysis(user.id, thumbnail=b"jpeg-bytes")
    token = auth["Authorization"].split()[1]

    assert client.get(f"/api/history/{analysis.id}/thumbnail").status_code == 401
    assert client.get(
        f"/api/history/{analysis.id}/thumbnail?token={token}"
    ).status_code == 401


def test_thumbnail_absent_is_404(client, auth, user):
    analysis = make_analysis(user.id, thumbnail=None)
    assert client.get(
        f"/api/history/{analysis.id}/thumbnail", headers=auth
    ).status_code == 404


def test_summary_advertises_a_thumbnail_only_when_one_exists(client, auth, user):
    with_thumb = make_analysis(user.id, thumbnail=b"jpeg-bytes")
    without = make_analysis(user.id, thumbnail=None)

    by_id = {
        a["id"]: a for a in client.get("/api/history", headers=auth).get_json()["analyses"]
    }
    assert by_id[with_thumb.id]["thumbnail_url"] is not None
    assert by_id[without.id]["thumbnail_url"] is None
