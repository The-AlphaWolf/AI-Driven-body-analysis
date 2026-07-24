"""
Face shape detection using MediaPipe Face Mesh.

Uses 478 facial landmarks to compute geometric ratios between forehead width,
cheekbone width, jawline width, and face length. These ratios are compared
against ideal profiles for each face shape category to produce a classification
with a confidence score.

Landmark indices used:
  - Face width (cheekbones): 234 ↔ 454
  - Forehead width:          70 ↔ 300
  - Jawline width:          172 ↔ 397
  - Face length (vertical):  10 ↔ 152
"""
import math
import numpy as np
import mediapipe as mp

from app.services.landmarkers import detect_face

# ── Landmark index constants ───────────────────────────────────────────────
# These indices correspond to specific anatomical points on the face mesh
LM_FOREHEAD_TOP = 10       # Top of forehead (hairline center)
LM_CHIN = 152              # Bottom of chin
LM_LEFT_CHEEK = 234        # Left cheekbone (widest point)
LM_RIGHT_CHEEK = 454       # Right cheekbone (widest point)
LM_LEFT_FOREHEAD = 70      # Left forehead edge
LM_RIGHT_FOREHEAD = 300    # Right forehead edge
LM_LEFT_JAW = 172          # Left jawline
LM_RIGHT_JAW = 397         # Right jawline

# ── Ideal ratio profiles for each face shape ───────────────────────────────
# Format: (face_length/face_width, forehead/cheekbone, jaw/cheekbone)
#
# These thresholds are derived from facial geometry literature and serve as
# the "ideal" ratio vector for each shape. Classification is based on
# Euclidean distance from the observed ratios to each ideal vector.
FACE_SHAPE_PROFILES = {
    "oval": {
        "length_width_ratio": 1.35,     # Face is ~35% longer than wide
        "forehead_cheek_ratio": 0.90,    # Forehead slightly narrower than cheeks
        "jaw_cheek_ratio": 0.75,         # Jaw noticeably narrower than cheeks
        "description": "Balanced, gently curved jawline with forehead slightly wider than jaw"
    },
    "round": {
        "length_width_ratio": 1.05,     # Nearly equal length and width
        "forehead_cheek_ratio": 0.88,    # Forehead close to cheek width
        "jaw_cheek_ratio": 0.85,         # Jaw also close to cheek width (all similar)
        "description": "Full cheeks, soft jawline, face length approximately equal to width"
    },
    "square": {
        "length_width_ratio": 1.05,     # Nearly equal length and width
        "forehead_cheek_ratio": 0.95,    # Forehead ≈ cheek width
        "jaw_cheek_ratio": 0.95,         # Jaw ≈ cheek width (all measurements similar)
        "description": "Strong angular jawline, forehead and jaw similar width"
    },
    "heart": {
        "length_width_ratio": 1.20,     # Slightly longer than wide
        "forehead_cheek_ratio": 1.05,    # Forehead wider than cheeks
        "jaw_cheek_ratio": 0.65,         # Jaw much narrower (pointed chin)
        "description": "Wide forehead tapering to a narrow, sometimes pointed chin"
    },
    "oblong": {
        "length_width_ratio": 1.55,     # Noticeably long face
        "forehead_cheek_ratio": 0.92,    # Forehead close to cheek width
        "jaw_cheek_ratio": 0.85,         # Jaw close to cheek width (uniform width)
        "description": "Long face with relatively uniform width from forehead to jaw"
    },
    "diamond": {
        "length_width_ratio": 1.30,     # Moderately elongated
        "forehead_cheek_ratio": 0.78,    # Forehead notably narrower than cheeks
        "jaw_cheek_ratio": 0.70,         # Jaw also narrow — cheekbones are widest
        "description": "Prominent cheekbones with narrow forehead and pointed chin"
    },
}


def _euclidean_distance(p1: tuple, p2: tuple) -> float:
    """Compute 2D Euclidean distance between two (x, y) points."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def _extract_measurements(landmarks, img_w: int, img_h: int) -> dict:
    """
    Extract facial measurements from normalized landmark coordinates.

    Converts MediaPipe's normalized [0,1] coordinates to pixel values,
    then computes distances between key anatomical points.

    Returns a dict of measurements and their derived ratios.
    """
    def lm_pixel(idx):
        """Get pixel coordinates for a landmark index."""
        lm = landmarks[idx]
        return (lm.x * img_w, lm.y * img_h)

    # Raw distances in pixels
    face_width = _euclidean_distance(lm_pixel(LM_LEFT_CHEEK), lm_pixel(LM_RIGHT_CHEEK))
    face_length = _euclidean_distance(lm_pixel(LM_FOREHEAD_TOP), lm_pixel(LM_CHIN))
    forehead_width = _euclidean_distance(lm_pixel(LM_LEFT_FOREHEAD), lm_pixel(LM_RIGHT_FOREHEAD))
    jaw_width = _euclidean_distance(lm_pixel(LM_LEFT_JAW), lm_pixel(LM_RIGHT_JAW))

    # Avoid division by zero
    if face_width < 1 or face_length < 1:
        return None

    return {
        "face_width": face_width,
        "face_length": face_length,
        "forehead_width": forehead_width,
        "jaw_width": jaw_width,
        "length_width_ratio": face_length / face_width,
        "forehead_cheek_ratio": forehead_width / face_width,
        "jaw_cheek_ratio": jaw_width / face_width,
    }


def _classify_shape(measurements: dict) -> tuple[str, float]:
    """
    Classify face shape by computing distance from observed ratios
    to each ideal face shape profile.

    Uses a weighted Euclidean distance where the length-to-width ratio
    is given higher weight (it's the strongest discriminator).

    Returns (shape_name, confidence) where confidence is 0–1.
    """
    observed = np.array([
        measurements["length_width_ratio"],
        measurements["forehead_cheek_ratio"],
        measurements["jaw_cheek_ratio"],
    ])

    # Weights: length/width ratio is the strongest signal for discrimination
    weights = np.array([2.0, 1.0, 1.5])

    distances = {}
    for shape, profile in FACE_SHAPE_PROFILES.items():
        ideal = np.array([
            profile["length_width_ratio"],
            profile["forehead_cheek_ratio"],
            profile["jaw_cheek_ratio"],
        ])
        # Weighted Euclidean distance
        diff = (observed - ideal) * weights
        distances[shape] = np.sqrt(np.sum(diff ** 2))

    # Best match is the shape with smallest distance
    best_shape = min(distances, key=distances.get)
    best_distance = distances[best_shape]

    # Convert distance to confidence (inverse relationship).
    # A distance of 0 → confidence 1.0, larger distances → lower confidence.
    # Using exponential decay: confidence = exp(-k * distance)
    # k=3.0 chosen so that a distance of ~0.5 gives ~0.22 confidence
    confidence = float(np.exp(-3.0 * best_distance))
    confidence = max(0.1, min(1.0, confidence))  # Clamp to [0.1, 1.0]

    return best_shape, round(confidence, 2)


def analyze_face(image: np.ndarray) -> dict | None:
    """
    Analyze a face image to determine face shape.

    Args:
        image: OpenCV BGR image containing a face

    Returns:
        Dict with shape classification and confidence, or None if no face detected.
        Example: {
            "shape": "oval",
            "confidence": 0.87,
            "measurements": { ... },
            "description": "Balanced, gently curved jawline..."
        }
    """
    import cv2

    # MediaPipe expects RGB input
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
    results = detect_face(mp_image)

    if not results.face_landmarks:
        return None

    landmarks = results.face_landmarks[0]
    img_h, img_w = image.shape[:2]

    measurements = _extract_measurements(landmarks, img_w, img_h)
    if measurements is None:
        return None

    shape, confidence = _classify_shape(measurements)

    return {
        "shape": shape,
        "confidence": confidence,
        "description": FACE_SHAPE_PROFILES[shape]["description"],
        "measurements": {
            "length_width_ratio": round(measurements["length_width_ratio"], 3),
            "forehead_cheek_ratio": round(measurements["forehead_cheek_ratio"], 3),
            "jaw_cheek_ratio": round(measurements["jaw_cheek_ratio"], 3),
        },
    }
