"""Recommendation engine scoring."""
import pytest

from app.services.recommendation import (
    CATEGORY_WEIGHTS,
    _load_rules,
    _score_rule,
    generate_recommendations,
)

FULL_FACE = {"shape": "oval", "confidence": 0.9}
FULL_SKIN = {"depth": "medium", "undertone": "warm", "hex_color": "#c68642"}
FULL_BODY = {"shape": "hourglass", "confidence": 0.85}


def test_rules_dataset_is_well_formed():
    rules = _load_rules()
    assert rules

    for rule in rules:
        assert rule["category"]
        assert rule["recommendation"]
        assert rule["explanation"]
        assert 0 < rule.get("weight", 1.0) <= 1.5


def test_every_category_has_rules():
    """A weighted category with no rules would silently produce no advice."""
    categories = {rule["category"] for rule in _load_rules()}
    assert set(CATEGORY_WEIGHTS) <= categories


def test_full_profile_produces_recommendations():
    results = generate_recommendations(FULL_FACE, FULL_SKIN, FULL_BODY)
    assert results
    assert all(r["score"] > 0 for r in results)


def test_results_are_sorted_by_score_descending():
    results = generate_recommendations(FULL_FACE, FULL_SKIN, FULL_BODY)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_no_category_exceeds_the_cap():
    results = generate_recommendations(
        FULL_FACE, FULL_SKIN, FULL_BODY, top_n_per_category=3
    )
    counts = {}
    for r in results:
        counts[r["category"]] = counts.get(r["category"], 0) + 1
    assert all(count <= 3 for count in counts.values())


def test_face_only_profile_still_produces_recommendations():
    """A user who uploads a headshot and no body photo must still get advice."""
    results = generate_recommendations(FULL_FACE, FULL_SKIN, None)
    assert results


def test_body_only_profile_still_produces_recommendations():
    results = generate_recommendations(None, None, FULL_BODY)
    assert results


def test_empty_profile_produces_nothing_rather_than_crashing():
    assert generate_recommendations(None, None, None) is not None


def test_matching_face_shape_scores_higher_than_a_mismatch():
    rule = {
        "category": "hairstyles",
        "recommendation": "Test",
        "explanation": "Test",
        "applicable_face_shapes": ["oval"],
        "applicable_body_shapes": [],
        "applicable_skin_tones": {},
    }
    match = _score_rule(rule, "oval", 0.9, None, None, None, 0.5)
    miss = _score_rule(rule, "square", 0.9, None, None, None, 0.5)
    assert match > miss


def test_confidence_scales_the_score():
    rule = {
        "category": "hairstyles",
        "recommendation": "Test",
        "explanation": "Test",
        "applicable_face_shapes": ["oval"],
        "applicable_body_shapes": [],
        "applicable_skin_tones": {},
    }
    confident = _score_rule(rule, "oval", 0.95, None, None, None, 0.5)
    unsure = _score_rule(rule, "oval", 0.30, None, None, None, 0.5)
    assert confident > unsure


def test_undertone_outweighs_depth_for_colours():
    """Undertone is the more discriminating signal and must dominate."""
    rule = {
        "category": "colors",
        "recommendation": "Test",
        "explanation": "Test",
        "applicable_face_shapes": [],
        "applicable_body_shapes": [],
        "applicable_skin_tones": {"undertone": ["warm"], "depth": ["deep"]},
    }
    undertone_only = _score_rule(rule, None, 0.5, "medium", "warm", None, 0.5)
    depth_only = _score_rule(rule, None, 0.5, "deep", "cool", None, 0.5)
    assert undertone_only > depth_only


def test_match_reasons_explain_each_hit():
    results = generate_recommendations(FULL_FACE, FULL_SKIN, FULL_BODY)
    matched = [r for r in results if r["match_reasons"]]
    assert matched

    for r in matched:
        for reason in r["match_reasons"]:
            assert isinstance(reason, str) and reason


def test_output_shape_is_json_serialisable():
    """The result is persisted into a JSON column, so it must round-trip."""
    import json

    results = generate_recommendations(FULL_FACE, FULL_SKIN, FULL_BODY)
    assert json.loads(json.dumps(results)) == results
