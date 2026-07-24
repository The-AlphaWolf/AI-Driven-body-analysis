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
        # Depth is open, so only the undertone varies between the two calls.
        "applicable_skin_tones": {
            "undertone": ["warm"],
            "depth": ["fair", "medium", "deep"],
        },
    }
    matching = _score_rule(rule, None, 0.5, "medium", "warm", None, 0.5)
    mismatched = _score_rule(rule, None, 0.5, "medium", "cool", None, 0.5)
    assert matching > mismatched


# ── Contradictions ─────────────────────────────────────────────────────────

def test_a_rule_that_excludes_the_users_skin_depth_is_not_recommended():
    """
    Colour advice reading "elegant on deeper complexions" was being shown
    to medium-skinned users, because a depth mismatch merely failed to add
    points rather than costing any.
    """
    results = generate_recommendations(FULL_FACE, FULL_SKIN, FULL_BODY)
    rules_by_text = {r["recommendation"]: r for r in _load_rules()}

    for result in results:
        if result["category"] != "colors":
            continue
        tones = rules_by_text[result["recommendation"]].get("applicable_skin_tones", {})
        assert FULL_SKIN["depth"] in tones.get("depth", [FULL_SKIN["depth"]])
        assert FULL_SKIN["undertone"] in tones.get("undertone", [FULL_SKIN["undertone"]])


def test_no_recommendation_contradicts_its_categorys_primary_attribute():
    """Sweep every attribute combination, not just one profile."""
    import itertools

    rules_by_text = {r["recommendation"]: r for r in _load_rules()}
    primary = {
        "necklines": "face", "hairstyles": "face",
        "silhouettes": "body", "patterns": "body",
        "colors": "skin", "accessories": "skin",
    }

    for face, depth, undertone, body in itertools.product(
        ["oval", "round", "square"],
        ["fair", "medium", "deep"],
        ["warm", "cool", "neutral"],
        ["hourglass", "pear", "apple"],
    ):
        results = generate_recommendations(
            {"shape": face, "confidence": 0.8},
            {"depth": depth, "undertone": undertone},
            {"shape": body, "confidence": 0.8},
        )
        for result in results:
            rule = rules_by_text[result["recommendation"]]
            dimension = primary.get(result["category"])

            if dimension == "face":
                allowed = rule.get("applicable_face_shapes")
                assert not allowed or face in allowed
            elif dimension == "body":
                allowed = rule.get("applicable_body_shapes")
                assert not allowed or body in allowed
            elif dimension == "skin":
                tones = rule.get("applicable_skin_tones", {})
                assert not tones.get("depth") or depth in tones["depth"]
                assert not tones.get("undertone") or undertone in tones["undertone"]


def test_a_secondary_contradiction_ranks_below_a_clean_match():
    """A body mismatch on a hairstyle rule demotes it without killing it."""
    clean = {
        "category": "hairstyles",
        "recommendation": "Test",
        "explanation": "Test",
        "applicable_face_shapes": ["oval"],
        "applicable_body_shapes": ["hourglass"],
        "applicable_skin_tones": {},
    }
    contradicting = {**clean, "applicable_body_shapes": ["pear"]}

    good = _score_rule(clean, "oval", 0.9, None, None, "hourglass", 0.9)
    demoted = _score_rule(contradicting, "oval", 0.9, None, None, "hourglass", 0.9)

    assert 0 < demoted < good


def test_a_rule_declaring_no_applicability_scores_zero():
    """
    Declaring nothing is not the same as applying to everyone — such a rule
    can never be recommended. Nothing in the dataset does this, and the test
    below keeps it that way; this one documents why that matters.
    """
    silent = {
        "category": "patterns",
        "recommendation": "Test",
        "explanation": "Test",
        "applicable_face_shapes": [],
        "applicable_body_shapes": [],
        "applicable_skin_tones": {},
    }
    assert _score_rule(silent, "diamond", 0.9, "deep", "cool", "apple", 0.9) == 0.0


def test_every_rule_declares_its_applicability():
    """A rule that declares nothing is unreachable, so none may exist."""
    for rule in _load_rules():
        tones = rule.get("applicable_skin_tones") or {}
        declares_something = (
            rule.get("applicable_face_shapes")
            or rule.get("applicable_body_shapes")
            or tones.get("undertone")
            or tones.get("depth")
        )
        assert declares_something, f"{rule['recommendation']} can never be recommended"


def test_every_profile_still_gets_advice_in_every_category():
    """Excluding contradictions must not leave a category empty."""
    import itertools

    for face, depth, undertone, body in itertools.product(
        ["oval", "round", "square", "heart", "oblong", "diamond"],
        ["fair", "light", "medium", "tan", "deep"],
        ["warm", "cool", "neutral"],
        ["hourglass", "pear", "apple", "rectangle", "inverted_triangle"],
    ):
        results = generate_recommendations(
            {"shape": face, "confidence": 0.8},
            {"depth": depth, "undertone": undertone},
            {"shape": body, "confidence": 0.8},
        )
        categories = {r["category"] for r in results}
        assert categories == set(CATEGORY_WEIGHTS), (
            f"{face}/{depth}/{undertone}/{body} has no advice for "
            f"{set(CATEGORY_WEIGHTS) - categories}"
        )


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
