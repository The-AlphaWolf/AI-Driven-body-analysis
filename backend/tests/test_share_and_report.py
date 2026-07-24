"""Public share links and PDF style reports."""
import pytest

from app.extensions import db
from app.models.analysis import Analysis
from app.models.user import User
from app.services.report import build_style_report

RECOMMENDATIONS = [
    {
        "category": "colors",
        "recommendation": "Camel and warm neutrals",
        "explanation": "Warm undertones are lifted by earthy neutrals.",
        "match_reasons": ["Harmonizes with your warm undertone"],
    },
    {
        "category": "necklines",
        "recommendation": "V-neck",
        "explanation": "Lengthens a rounder face.",
        "match_reasons": ["Complements your round face shape"],
    },
]


@pytest.fixture
def analysis(user):
    a = Analysis(
        user_id=user.id,
        face_shape="round",
        face_confidence=0.81,
        skin_depth="medium",
        skin_undertone="warm",
        skin_hex_color="#c68642",
        skin_confidence=0.74,
        body_shape="inverted_triangle",
        body_confidence=0.69,
        recommendations=RECOMMENDATIONS,
        thumbnail=b"\xff\xd8\xff\xe0 pretend jpeg",
    )
    db.session.add(a)
    db.session.commit()
    return a


def share(client, auth, analysis_id):
    return client.post(f"/api/history/{analysis_id}/share", headers=auth)


# ── Enabling and revoking ──────────────────────────────────────────────────

def test_sharing_requires_auth(client, analysis):
    assert client.post(f"/api/history/{analysis.id}/share").status_code == 401


def test_share_mints_a_token(client, auth, analysis):
    response = share(client, auth, analysis.id)
    assert response.status_code == 200

    body = response.get_json()
    assert body["share_token"]
    assert body["share_path"] == f"/s/{body['share_token']}"
    assert body["shared_at"]


def test_share_token_is_long_and_random(client, auth, analysis, user):
    """A guessable token would make every 'private' analysis enumerable."""
    second = Analysis(user_id=user.id, face_shape="oval", recommendations=[])
    db.session.add(second)
    db.session.commit()

    first_token = share(client, auth, analysis.id).get_json()["share_token"]
    second_token = share(client, auth, second.id).get_json()["share_token"]

    assert len(first_token) >= 40
    assert first_token != second_token
    assert analysis.id not in first_token


def test_sharing_twice_keeps_the_same_link(client, auth, analysis):
    """Re-sharing must not invalidate a URL the owner already sent someone."""
    first = share(client, auth, analysis.id).get_json()["share_token"]
    second = share(client, auth, analysis.id).get_json()["share_token"]
    assert first == second


def test_cannot_share_another_users_analysis(client, auth):
    other = User(email="other@example.com")
    other.set_password("password123")
    db.session.add(other)
    db.session.commit()
    theirs = Analysis(user_id=other.id, face_shape="oval", recommendations=[])
    db.session.add(theirs)
    db.session.commit()

    assert share(client, auth, theirs.id).status_code == 404
    assert theirs.share_token is None


def test_revoking_breaks_the_link(client, auth, analysis):
    token = share(client, auth, analysis.id).get_json()["share_token"]
    assert client.get(f"/api/public/{token}").status_code == 200

    assert client.delete(f"/api/history/{analysis.id}/share", headers=auth).status_code == 200
    assert client.get(f"/api/public/{token}").status_code == 404


def test_owner_sees_the_share_state_on_the_analysis(client, auth, analysis):
    before = client.get(f"/api/history/{analysis.id}", headers=auth).get_json()
    assert before["analysis"]["share_token"] is None

    share(client, auth, analysis.id)

    after = client.get(f"/api/history/{analysis.id}", headers=auth).get_json()
    assert after["analysis"]["share_token"]


# ── Reading a shared analysis ──────────────────────────────────────────────

def test_shared_analysis_is_readable_without_auth(client, auth, analysis):
    token = share(client, auth, analysis.id).get_json()["share_token"]

    body = client.get(f"/api/public/{token}").get_json()
    assert body["analysis"]["face_analysis"]["shape"] == "round"
    assert len(body["analysis"]["recommendations"]) == 2


def test_shared_analysis_omits_the_photo(client, auth, analysis):
    """A shared style report must not hand a stranger the subject's face."""
    token = share(client, auth, analysis.id).get_json()["share_token"]

    payload = client.get(f"/api/public/{token}").get_json()["analysis"]
    assert "thumbnail_url" not in payload


def test_shared_analysis_omits_internal_identifiers(client, auth, analysis):
    token = share(client, auth, analysis.id).get_json()["share_token"]

    payload = client.get(f"/api/public/{token}").get_json()["analysis"]
    assert payload["id"] is None
    assert "share_token" not in payload
    assert "user_id" not in payload


def test_unshared_analysis_is_not_publicly_reachable(client, analysis):
    """The analysis id must not work as a share token."""
    assert client.get(f"/api/public/{analysis.id}").status_code == 404


@pytest.mark.parametrize("token", ["", "nope", "a" * 43])
def test_invalid_tokens_are_404(client, token):
    assert client.get(f"/api/public/{token}").status_code in (404, 405)


# ── PDF reports ────────────────────────────────────────────────────────────

def test_report_is_a_pdf(client, auth, analysis):
    response = client.get(f"/api/history/{analysis.id}/report.pdf", headers=auth)

    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert response.data.startswith(b"%PDF-")
    assert "attachment" in response.headers["Content-Disposition"]


def test_report_requires_auth(client, analysis):
    assert client.get(f"/api/history/{analysis.id}/report.pdf").status_code == 401


def test_cannot_download_another_users_report(client, auth):
    other = User(email="other@example.com")
    other.set_password("password123")
    db.session.add(other)
    db.session.commit()
    theirs = Analysis(user_id=other.id, face_shape="oval", recommendations=[])
    db.session.add(theirs)
    db.session.commit()

    assert client.get(
        f"/api/history/{theirs.id}/report.pdf", headers=auth
    ).status_code == 404


def test_shared_report_is_downloadable_without_auth(client, auth, analysis):
    token = share(client, auth, analysis.id).get_json()["share_token"]

    response = client.get(f"/api/public/{token}/report.pdf")
    assert response.status_code == 200
    assert response.data.startswith(b"%PDF-")


def test_revoked_share_stops_serving_the_report(client, auth, analysis):
    token = share(client, auth, analysis.id).get_json()["share_token"]
    client.delete(f"/api/history/{analysis.id}/share", headers=auth)

    assert client.get(f"/api/public/{token}/report.pdf").status_code == 404


def test_report_contains_the_analysis_content(app, analysis):
    """Sanity-check the text made it into the document, not just the header."""
    pdf = build_style_report(analysis)
    assert len(pdf) > 1500  # A page with real content, not an empty shell


def test_report_survives_an_analysis_with_no_recommendations(app, user):
    empty = Analysis(user_id=user.id, face_shape="oval", face_confidence=0.5)
    db.session.add(empty)
    db.session.commit()

    assert build_style_report(empty).startswith(b"%PDF-")


def test_report_survives_a_partial_analysis(app, user):
    """A body-only analysis has no face or skin rows to render."""
    partial = Analysis(
        user_id=user.id,
        body_shape="pear",
        body_confidence=0.7,
        recommendations=[{"category": "silhouettes", "recommendation": "A-line"}],
    )
    db.session.add(partial)
    db.session.commit()

    assert build_style_report(partial).startswith(b"%PDF-")


def test_report_escapes_markup_in_recommendation_text(app, user):
    """Recommendation text is interpolated into ReportLab's inline markup."""
    risky = Analysis(
        user_id=user.id,
        face_shape="oval",
        face_confidence=0.5,
        recommendations=[{
            "category": "colors",
            "recommendation": "Navy <b> & cream",
            "explanation": "A <unclosed tag & ampersand",
            "match_reasons": ["Works with <everything>"],
        }],
    )
    db.session.add(risky)
    db.session.commit()

    assert build_style_report(risky).startswith(b"%PDF-")
