"""Feedback routes: recording, clearing, and reading back verdicts."""
import pytest

from app.extensions import db
from app.models.analysis import Analysis
from app.models.feedback import Feedback
from app.models.user import User

REC = {"category": "colors", "recommendation": "Camel and warm neutrals"}


@pytest.fixture
def analysis(user):
    a = Analysis(
        user_id=user.id,
        face_shape="oval",
        face_confidence=0.8,
        recommendations=[{"category": "colors", "recommendation": "Camel and warm neutrals"}],
    )
    db.session.add(a)
    db.session.commit()
    return a


def put(client, auth, analysis_id, verdict, **overrides):
    body = {**REC, "verdict": verdict, **overrides}
    return client.put(f"/api/feedback/analysis/{analysis_id}", headers=auth, json=body)


def test_feedback_requires_auth(client, analysis):
    assert client.put(f"/api/feedback/analysis/{analysis.id}", json=REC).status_code == 401
    assert client.get(f"/api/feedback/analysis/{analysis.id}").status_code == 401
    assert client.get("/api/feedback/saved").status_code == 401


def test_saved_route_is_not_shadowed_by_the_analysis_route(client, auth):
    """`/saved` must resolve to the list endpoint, not be read as an id."""
    response = client.get("/api/feedback/saved", headers=auth)
    assert response.status_code == 200
    assert "saved" in response.get_json()


def test_like_is_recorded(client, auth, analysis):
    response = put(client, auth, analysis.id, "like")
    assert response.status_code == 200
    assert response.get_json()["feedback"]["verdict"] == "like"
    assert Feedback.query.count() == 1


def test_dislike_is_recorded(client, auth, analysis):
    assert put(client, auth, analysis.id, "dislike").status_code == 200
    assert Feedback.query.one().verdict == "dislike"


def test_changing_the_verdict_updates_rather_than_duplicates(client, auth, analysis):
    put(client, auth, analysis.id, "like")
    put(client, auth, analysis.id, "dislike")

    assert Feedback.query.count() == 1
    assert Feedback.query.one().verdict == "dislike"


def test_null_verdict_clears_the_feedback(client, auth, analysis):
    put(client, auth, analysis.id, "like")

    response = put(client, auth, analysis.id, None)
    assert response.status_code == 200
    assert response.get_json()["feedback"] is None
    assert Feedback.query.count() == 0


def test_clearing_when_nothing_is_stored_is_not_an_error(client, auth, analysis):
    assert put(client, auth, analysis.id, None).status_code == 200


def test_sending_the_same_verdict_twice_is_idempotent(client, auth, analysis):
    put(client, auth, analysis.id, "like")
    put(client, auth, analysis.id, "like")
    assert Feedback.query.count() == 1


def test_invalid_verdict_is_rejected(client, auth, analysis):
    assert put(client, auth, analysis.id, "maybe").status_code == 422


def test_missing_fields_are_rejected(client, auth, analysis):
    response = client.put(
        f"/api/feedback/analysis/{analysis.id}",
        headers=auth,
        json={"verdict": "like"},
    )
    assert response.status_code == 422


def test_non_json_body_is_rejected(client, auth, analysis):
    response = client.put(
        f"/api/feedback/analysis/{analysis.id}", headers=auth, data="nope"
    )
    assert response.status_code == 400


def test_feedback_on_an_unknown_analysis_is_404(client, auth):
    assert put(client, auth, "does-not-exist", "like").status_code == 404


def test_feedback_on_another_users_analysis_is_refused(client, auth):
    other = User(email="other@example.com")
    other.set_password("password123")
    db.session.add(other)
    db.session.commit()

    theirs = Analysis(user_id=other.id, face_shape="round", recommendations=[])
    db.session.add(theirs)
    db.session.commit()

    assert put(client, auth, theirs.id, "like").status_code == 404
    assert Feedback.query.count() == 0


def test_get_returns_a_lookup_keyed_for_the_client(client, auth, analysis):
    put(client, auth, analysis.id, "like")
    put(
        client, auth, analysis.id, "dislike",
        category="necklines", recommendation="V-neck",
    )

    body = client.get(f"/api/feedback/analysis/{analysis.id}", headers=auth).get_json()
    assert body["feedback"] == {
        "colors::Camel and warm neutrals": "like",
        "necklines::V-neck": "dislike",
    }


def test_saved_lists_only_likes(client, auth, analysis):
    put(client, auth, analysis.id, "like")
    put(
        client, auth, analysis.id, "dislike",
        category="necklines", recommendation="V-neck",
    )

    body = client.get("/api/feedback/saved", headers=auth).get_json()
    assert body["total"] == 1
    assert body["saved"][0]["recommendation"] == "Camel and warm neutrals"


def test_saved_excludes_other_users(client, auth, analysis, user):
    other = User(email="other@example.com")
    other.set_password("password123")
    db.session.add(other)
    db.session.commit()
    db.session.add(Feedback(
        user_id=other.id, analysis_id=analysis.id,
        category="colors", recommendation="Their pick", verdict="like",
    ))
    db.session.commit()

    body = client.get("/api/feedback/saved", headers=auth).get_json()
    assert body["total"] == 0


def test_saved_paginates(client, auth, analysis):
    for i in range(5):
        put(client, auth, analysis.id, "like", recommendation=f"Pick {i}")

    body = client.get("/api/feedback/saved?page=2&per_page=2", headers=auth).get_json()
    assert body["page"] == 2
    assert body["pages"] == 3


def test_deleting_an_analysis_removes_its_feedback(client, auth, analysis):
    """An orphaned verdict would poison the training data it exists to build."""
    put(client, auth, analysis.id, "like")
    assert Feedback.query.count() == 1

    client.delete(f"/api/history/{analysis.id}", headers=auth)
    assert Feedback.query.count() == 0
