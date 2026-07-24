"""
Recommendation engine using weighted feature-vector scoring.

Takes the outputs from face, skin, and body analysis and matches them
against a structured style rules dataset. Each rule is scored based on
how well it matches the user's detected attributes, with category-dependent
weighting (e.g., hairstyle rules weight face shape higher; silhouette
rules weight body shape higher).

Architecture note:
  This scoring function accepts a standardized feature vector, making it
  straightforward to replace with a trained ML model in the future. The
  model would take the same inputs and produce the same output shape.
"""
import json
import os
from pathlib import Path

# ── Load style rules dataset ───────────────────────────────────────────────
_RULES_PATH = Path(__file__).parent.parent / "data" / "style_rules.json"
_rules_cache = None


def _load_rules() -> list[dict]:
    """Load and cache the style rules dataset."""
    global _rules_cache
    if _rules_cache is None:
        with open(_RULES_PATH, "r") as f:
            _rules_cache = json.load(f)
    return _rules_cache


# ── Category-dependent weight profiles ─────────────────────────────────────
# Different recommendation categories should weight attributes differently.
# For example, hairstyle advice depends heavily on face shape but barely
# on body shape, while silhouette advice is the opposite.
CATEGORY_WEIGHTS = {
    "necklines":   {"face": 0.45, "body": 0.35, "skin": 0.20},
    "silhouettes": {"face": 0.10, "body": 0.65, "skin": 0.25},
    "colors":      {"face": 0.05, "body": 0.05, "skin": 0.90},
    "patterns":    {"face": 0.30, "body": 0.50, "skin": 0.20},
    "accessories": {"face": 0.35, "body": 0.25, "skin": 0.40},
    "hairstyles":  {"face": 0.75, "body": 0.05, "skin": 0.20},
}

# Default weights if category not in the map
DEFAULT_WEIGHTS = {"face": 0.33, "body": 0.34, "skin": 0.33}

# Within the skin dimension, undertone is the more discriminating signal.
UNDERTONE_SHARE = 0.6
DEPTH_SHARE = 0.4


def _primary_dimension(weights: dict) -> str:
    """The attribute a category's advice is really about."""
    return max(weights, key=weights.get)


def _contradictions(
    rule: dict,
    face_shape: str | None,
    skin_depth: str | None,
    skin_undertone: str | None,
    body_shape: str | None,
) -> dict[str, bool]:
    """
    Which of the user's known attributes this rule explicitly excludes.

    A rule that lists applicable values and does not include the user's is
    not merely a weak match — it is advice written for somebody else. This
    is distinct from a rule that stays silent on a dimension, which applies
    to everyone.
    """
    skin_tones = rule.get("applicable_skin_tones") or {}

    def excluded(value, allowed) -> bool:
        return bool(value and allowed and value not in allowed)

    return {
        "face": excluded(face_shape, rule.get("applicable_face_shapes")),
        "body": excluded(body_shape, rule.get("applicable_body_shapes")),
        "undertone": excluded(skin_undertone, skin_tones.get("undertone")),
        "depth": excluded(skin_depth, skin_tones.get("depth")),
    }


def _score_rule(
    rule: dict,
    face_shape: str | None,
    face_confidence: float,
    skin_depth: str | None,
    skin_undertone: str | None,
    body_shape: str | None,
    body_confidence: float,
) -> float:
    """
    Compute a match score for a single rule against the user's attributes.

    Score components:
      - face_match: 1.0 if user's face shape is in the rule's applicable list
      - body_match: 1.0 if user's body shape is in the rule's applicable list
      - skin_match: Weighted combination of undertone match (0.6) + depth match (0.4)

    Each component is multiplied by the detection confidence and the
    category-dependent weight for that dimension.

    Returns a float score in [0, 1].
    """
    category = rule.get("category", "")
    weights = CATEGORY_WEIGHTS.get(category, DEFAULT_WEIGHTS)

    # ── Contradictions ─────────────────────────────────────────────────
    # A rule that explicitly excludes the user's attribute is not a weak
    # match, it is wrong. Colour advice reading "exceptionally elegant on
    # deeper complexions" was being shown to medium-skinned users because a
    # depth mismatch merely failed to add points instead of costing any.
    contradicts = _contradictions(
        rule, face_shape, skin_depth, skin_undertone, body_shape
    )
    primary = _primary_dimension(weights)

    primary_contradicted = (
        contradicts["undertone"] or contradicts["depth"]
        if primary == "skin"
        else contradicts[primary]
    )
    if primary_contradicted:
        return 0.0

    # ── Face shape match ───────────────────────────────────────────────
    face_score = 0.0
    if face_shape and rule.get("applicable_face_shapes"):
        if face_shape in rule["applicable_face_shapes"]:
            face_score = 1.0
    elif not face_shape:
        # No face data — don't penalize, use neutral score
        face_score = 0.5

    # ── Body shape match ───────────────────────────────────────────────
    body_score = 0.0
    if body_shape and rule.get("applicable_body_shapes"):
        if body_shape in rule["applicable_body_shapes"]:
            body_score = 1.0
    elif not body_shape:
        body_score = 0.5

    # ── Skin tone match ────────────────────────────────────────────────
    skin_score = 0.0
    skin_tones = rule.get("applicable_skin_tones", {})

    if skin_undertone or skin_depth:
        undertone_match = 0.0
        depth_match = 0.0

        if skin_undertone and "undertone" in skin_tones:
            if skin_undertone in skin_tones["undertone"]:
                undertone_match = 1.0

        if skin_depth and "depth" in skin_tones:
            if skin_depth in skin_tones["depth"]:
                depth_match = 1.0

        # Undertone is more discriminating than depth for color recommendations
        skin_score = undertone_match * UNDERTONE_SHARE + depth_match * DEPTH_SHARE
    else:
        skin_score = 0.5  # No skin data — neutral

    # ── Weighted total ─────────────────────────────────────────────────
    # Multiply each component by its confidence and category weight
    total = (
        face_score * face_confidence * weights["face"]
        + body_score * body_confidence * weights["body"]
        + skin_score * weights["skin"]  # Skin doesn't have a separate confidence
    )

    # Apply the rule's own weight (editorial quality/importance weight)
    total *= rule.get("weight", 1.0)

    # ── Secondary contradictions ───────────────────────────────────────
    # Not disqualifying the way a primary one is, but the rule must rank
    # below anything that does not contradict the user at all.
    for dimension, share in (
        ("face", weights["face"]),
        ("body", weights["body"]),
        ("undertone", weights["skin"] * UNDERTONE_SHARE),
        ("depth", weights["skin"] * DEPTH_SHARE),
    ):
        if contradicts[dimension]:
            total *= 1.0 - share

    return total


def generate_recommendations(
    face_result: dict | None = None,
    skin_result: dict | None = None,
    body_result: dict | None = None,
    top_n_per_category: int = 5,
) -> list[dict]:
    """
    Generate ranked style recommendations based on analysis results.

    Args:
        face_result: Output from analyze_face(), or None
        skin_result: Output from analyze_skin_tone(), or None
        body_result: Output from analyze_body(), or None
        top_n_per_category: Max recommendations per category

    Returns:
        List of recommendation dicts, grouped by category, sorted by score.
        Each dict includes:
          - category, recommendation, explanation, score
          - match_reasons: list of strings explaining why this was recommended
    """
    rules = _load_rules()

    # ── Extract attributes from results ────────────────────────────────
    face_shape = face_result.get("shape") if face_result else None
    face_confidence = face_result.get("confidence", 0.5) if face_result else 0.5

    skin_depth = skin_result.get("depth") if skin_result else None
    skin_undertone = skin_result.get("undertone") if skin_result else None

    body_shape = body_result.get("shape") if body_result else None
    body_confidence = body_result.get("confidence", 0.5) if body_result else 0.5

    # ── Score all rules ────────────────────────────────────────────────
    scored_rules = []
    for rule in rules:
        score = _score_rule(
            rule,
            face_shape, face_confidence,
            skin_depth, skin_undertone,
            body_shape, body_confidence,
        )

        if score > 0.1:  # Filter out very low matches
            # Build match reasons
            reasons = []
            if face_shape and face_shape in rule.get("applicable_face_shapes", []):
                reasons.append(f"Complements your {face_shape} face shape")
            if body_shape and body_shape in rule.get("applicable_body_shapes", []):
                reasons.append(f"Flattering for your {body_shape} body shape")
            if skin_undertone:
                skin_tones = rule.get("applicable_skin_tones", {})
                if skin_undertone in skin_tones.get("undertone", []):
                    reasons.append(f"Harmonizes with your {skin_undertone} undertone")
            if skin_depth:
                skin_tones = rule.get("applicable_skin_tones", {})
                if skin_depth in skin_tones.get("depth", []):
                    reasons.append(f"Great for your {skin_depth} skin tone")

            scored_rules.append({
                "category": rule["category"],
                "recommendation": rule["recommendation"],
                "explanation": rule["explanation"],
                "score": round(score, 3),
                "match_reasons": reasons,
                "tags": rule.get("tags", []),
            })

    # ── Group by category and take top N per category ──────────────────
    scored_rules.sort(key=lambda r: r["score"], reverse=True)

    category_counts = {}
    filtered = []
    for rule in scored_rules:
        cat = rule["category"]
        count = category_counts.get(cat, 0)
        if count < top_n_per_category:
            filtered.append(rule)
            category_counts[cat] = count + 1

    return filtered
