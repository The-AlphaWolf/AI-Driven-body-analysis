"""
Body proportion analysis using MediaPipe Pose.

Extracts key body landmarks (shoulders, hips, knees, ankles) and computes
proportion ratios to classify body shape into standard categories.

Key landmarks used (MediaPipe Pose indices):
  - Shoulders: 11 (left), 12 (right)
  - Hips:      23 (left), 24 (right)
  - Knees:     25 (left), 26 (right)
  - Ankles:    27 (left), 28 (right)

Derived ratios:
  - Shoulder-to-Hip Ratio (SHR): Primary discriminator
  - Torso-to-Leg Ratio: Secondary proportion metric
  - Waist estimation: Interpolated from torso landmarks
"""
import math
import numpy as np
import cv2
import mediapipe as mp

from app.services.landmarkers import detect_pose

# ── Landmark indices ───────────────────────────────────────────────────────
LM_LEFT_SHOULDER = 11
LM_RIGHT_SHOULDER = 12
LM_LEFT_HIP = 23
LM_RIGHT_HIP = 24
LM_LEFT_KNEE = 25
LM_RIGHT_KNEE = 26
LM_LEFT_ANKLE = 27
LM_RIGHT_ANKLE = 28

# Minimum visibility score to trust a landmark
MIN_VISIBILITY = 0.5

# ── Body shape classification thresholds ───────────────────────────────────
# SHR = Shoulder Width / Hip Width
# These thresholds define the boundaries between body shape categories
BODY_SHAPE_PROFILES = {
    "hourglass": {
        "shr_range": (0.90, 1.10),   # Shoulders and hips roughly equal
        "waist_ratio_max": 0.75,      # Waist notably narrower than shoulders and hips
        "description": "Balanced shoulders and hips with a defined waist"
    },
    "pear": {
        "shr_range": (0.0, 0.90),    # Hips wider than shoulders
        "waist_ratio_max": 1.0,       # Waist can vary
        "description": "Hips wider than shoulders, weight carried in lower body"
    },
    "inverted_triangle": {
        "shr_range": (1.15, 2.0),    # Shoulders much wider than hips
        "waist_ratio_max": 1.0,
        "description": "Broad shoulders tapering to narrower hips"
    },
    "rectangle": {
        "shr_range": (0.90, 1.15),   # Similar widths throughout
        "waist_ratio_max": 1.0,       # But waist NOT narrower (no hourglass curve)
        "description": "Shoulders, waist, and hips are similar width"
    },
    "apple": {
        "shr_range": (0.90, 1.15),   # Similar shoulder/hip width
        "waist_ratio_max": 1.0,       # Waist wider relative to hips
        "description": "Weight carried around the midsection, broader waist area"
    },
}


def _euclidean_distance(p1: tuple, p2: tuple) -> float:
    """Compute 2D Euclidean distance between two (x, y) points."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def _midpoint(p1: tuple, p2: tuple) -> tuple:
    """Compute midpoint between two (x, y) points."""
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)


def _get_landmark_pixel(landmark, img_w: int, img_h: int) -> tuple:
    """Convert a normalized landmark to pixel coordinates."""
    return (landmark.x * img_w, landmark.y * img_h)


def _check_visibility(landmarks, indices: list) -> float:
    """
    Check average visibility of a set of landmarks.
    Returns average visibility score (0-1).
    """
    visibilities = [landmarks[i].visibility for i in indices]
    return sum(visibilities) / len(visibilities)


def _extract_body_measurements(landmarks, img_w: int, img_h: int) -> dict | None:
    """
    Extract body measurements from pose landmarks.

    Returns a dict of measurements and ratios, or None if key landmarks
    aren't visible enough for reliable analysis.
    """
    # Check that critical landmarks are visible
    critical = [
        LM_LEFT_SHOULDER, LM_RIGHT_SHOULDER,
        LM_LEFT_HIP, LM_RIGHT_HIP,
    ]
    avg_visibility = _check_visibility(landmarks, critical)
    if avg_visibility < MIN_VISIBILITY:
        return None

    # Get pixel coordinates
    left_shoulder = _get_landmark_pixel(landmarks[LM_LEFT_SHOULDER], img_w, img_h)
    right_shoulder = _get_landmark_pixel(landmarks[LM_RIGHT_SHOULDER], img_w, img_h)
    left_hip = _get_landmark_pixel(landmarks[LM_LEFT_HIP], img_w, img_h)
    right_hip = _get_landmark_pixel(landmarks[LM_RIGHT_HIP], img_w, img_h)

    # Compute widths
    shoulder_width = _euclidean_distance(left_shoulder, right_shoulder)
    hip_width = _euclidean_distance(left_hip, right_hip)

    if shoulder_width < 1 or hip_width < 1:
        return None

    # Shoulder-to-Hip Ratio (primary classifier)
    shr = shoulder_width / hip_width

    # Torso and leg lengths (if lower body landmarks are visible)
    shoulder_mid = _midpoint(left_shoulder, right_shoulder)
    hip_mid = _midpoint(left_hip, right_hip)
    torso_length = _euclidean_distance(shoulder_mid, hip_mid)

    leg_length = None
    torso_leg_ratio = None
    leg_visibility = _check_visibility(landmarks, [LM_LEFT_ANKLE, LM_RIGHT_ANKLE])
    if leg_visibility >= MIN_VISIBILITY:
        left_ankle = _get_landmark_pixel(landmarks[LM_LEFT_ANKLE], img_w, img_h)
        right_ankle = _get_landmark_pixel(landmarks[LM_RIGHT_ANKLE], img_w, img_h)
        ankle_mid = _midpoint(left_ankle, right_ankle)
        leg_length = _euclidean_distance(hip_mid, ankle_mid)
        if leg_length > 1:
            torso_leg_ratio = torso_length / leg_length

    # Estimate waist width
    # The waist is approximately 1/3 of the way from hips to shoulders
    # We estimate it by interpolating between shoulder and hip widths
    # with a narrowing factor based on the torso shape
    waist_y = hip_mid[1] + (shoulder_mid[1] - hip_mid[1]) * 0.35
    # Interpolate x positions for waist estimation
    left_waist_x = left_hip[0] + (left_shoulder[0] - left_hip[0]) * 0.35
    right_waist_x = right_hip[0] + (right_shoulder[0] - right_hip[0]) * 0.35
    waist_width = abs(right_waist_x - left_waist_x)

    waist_hip_ratio = waist_width / hip_width if hip_width > 0 else 1.0
    waist_shoulder_ratio = waist_width / shoulder_width if shoulder_width > 0 else 1.0

    return {
        "shoulder_width": shoulder_width,
        "hip_width": hip_width,
        "shoulder_hip_ratio": shr,
        "torso_length": torso_length,
        "leg_length": leg_length,
        "torso_leg_ratio": torso_leg_ratio,
        "waist_width": waist_width,
        "waist_hip_ratio": waist_hip_ratio,
        "waist_shoulder_ratio": waist_shoulder_ratio,
        "avg_visibility": avg_visibility,
    }


def _classify_body_shape(measurements: dict) -> tuple[str, float]:
    """
    Classify body shape from measurements.

    Classification logic:
      1. Check SHR for clear pear or inverted triangle
      2. For middle-range SHR, use waist ratio to distinguish
         hourglass (defined waist) from rectangle/apple
      3. Confidence based on how clearly the measurements fit a category

    Returns (shape_name, confidence).
    """
    shr = measurements["shoulder_hip_ratio"]
    waist_hip = measurements["waist_hip_ratio"]
    waist_shoulder = measurements["waist_shoulder_ratio"]

    # Clear inverted triangle: shoulders much wider than hips
    if shr > 1.15:
        confidence = min(1.0, 0.6 + (shr - 1.15) * 2)
        return "inverted_triangle", round(confidence, 2)

    # Clear pear: hips much wider than shoulders
    if shr < 0.90:
        confidence = min(1.0, 0.6 + (0.90 - shr) * 2)
        return "pear", round(confidence, 2)

    # Middle range (0.90 - 1.15): Distinguish hourglass, rectangle, apple
    # Hourglass: waist is notably narrower than both shoulders and hips
    if waist_hip < 0.78 and waist_shoulder < 0.78:
        waist_definition = (1.0 - waist_hip) + (1.0 - waist_shoulder)
        confidence = min(1.0, 0.5 + waist_definition)
        return "hourglass", round(confidence, 2)

    # Apple: waist is similar to or wider than hips
    if waist_hip > 0.92:
        confidence = min(1.0, 0.5 + (waist_hip - 0.92) * 3)
        return "apple", round(confidence, 2)

    # Rectangle: everything is relatively similar width
    shr_balance = 1.0 - abs(shr - 1.0)  # How close SHR is to 1.0
    confidence = min(1.0, 0.5 + shr_balance * 0.3)
    return "rectangle", round(confidence, 2)


def analyze_body(image: np.ndarray) -> dict | None:
    """
    Analyze body proportions from a full-body photo.

    Args:
        image: OpenCV BGR image containing a full-body pose

    Returns:
        Dict with body shape classification and measurements, or None if
        no pose detected.
        Example: {
            "shape": "pear",
            "confidence": 0.78,
            "description": "Hips wider than shoulders...",
            "measurements": {
                "shoulder_hip_ratio": 0.85,
                "torso_leg_ratio": 0.48,
                "waist_hip_ratio": 0.82,
            }
        }
    """
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
    results = detect_pose(mp_image)

    if not results.pose_landmarks:
        return None

    landmarks = results.pose_landmarks[0]
    img_h, img_w = image.shape[:2]

    measurements = _extract_body_measurements(landmarks, img_w, img_h)
    if measurements is None:
        return None

    shape, confidence = _classify_body_shape(measurements)

    # Scale confidence by landmark visibility (lower visibility = less reliable)
    visibility_factor = measurements["avg_visibility"]
    adjusted_confidence = round(confidence * visibility_factor, 2)

    return {
        "shape": shape,
        "confidence": adjusted_confidence,
        "description": BODY_SHAPE_PROFILES[shape]["description"],
        "measurements": {
            "shoulder_hip_ratio": round(measurements["shoulder_hip_ratio"], 3),
            "torso_leg_ratio": round(measurements["torso_leg_ratio"], 3) if measurements["torso_leg_ratio"] else None,
            "waist_hip_ratio": round(measurements["waist_hip_ratio"], 3),
        },
    }
