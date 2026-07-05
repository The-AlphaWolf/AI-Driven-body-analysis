"""
Skin tone classification using k-means clustering in LAB color space.

Pipeline:
  1. Extract skin pixel ROIs from face landmarks (cheeks + forehead)
  2. Convert to LAB color space (perceptually uniform, lighting-resilient)
  3. Apply CLAHE normalization on the L channel to handle lighting variation
  4. Run k-means clustering (K=3) to find the dominant skin color
  5. Classify depth (fair → deep) from the L* lightness channel
  6. Classify undertone (warm/cool/neutral) from a* and b* channels
  7. Assess confidence based on pixel lightness standard deviation

Why LAB?
  - L* (lightness) is independent of color → robust depth classification
  - a* (green-red axis) and b* (blue-yellow axis) directly encode the
    chromatic information needed to distinguish warm vs cool undertones
  - Perceptually uniform: equal numeric differences ≈ equal visual differences
"""
import cv2
import numpy as np
from sklearn.cluster import KMeans
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os

_model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'face_landmarker.task')
_base_options = python.BaseOptions(model_asset_path=_model_path)
_options = vision.FaceLandmarkerOptions(
    base_options=_base_options,
    output_face_blendshapes=False,
    output_facial_transformation_matrixes=False,
    num_faces=1
)
_face_landmarker = vision.FaceLandmarker.create_from_options(_options)

# ── Landmark indices for skin sampling regions ─────────────────────────────
# These landmarks sit on actual skin, away from hair, eyes, mouth
SKIN_SAMPLE_LANDMARKS = {
    "left_cheek": [50, 101, 36, 205],     # Points on left cheek
    "right_cheek": [280, 330, 266, 425],   # Points on right cheek
    "forehead": [10, 67, 109, 297],        # Points on forehead center
}

# Radius (in pixels) around each landmark to sample
SAMPLE_RADIUS = 12

# ── Depth classification thresholds (L* values in LAB) ─────────────────────
# L* ranges from 0 (black) to 100 (white). These thresholds are calibrated
# against the Fitzpatrick scale as a rough approximation.
DEPTH_THRESHOLDS = [
    (80, "fair"),       # L* > 80
    (65, "light"),      # 65 < L* ≤ 80
    (50, "medium"),     # 50 < L* ≤ 65
    (35, "tan"),        # 35 < L* ≤ 50
    (0,  "deep"),       # L* ≤ 35
]

# ── Undertone classification thresholds ────────────────────────────────────
# In LAB space:
#   a* > 0 = red, a* < 0 = green
#   b* > 0 = yellow, b* < 0 = blue
# Warm undertones have higher b* (yellow bias)
# Cool undertones have higher a* relative to b* (pink/blue bias)
WARM_B_THRESHOLD = 18      # b* above this → warm
COOL_A_THRESHOLD = 14      # a* above this AND b* below warm → cool
NEUTRAL_MARGIN = 3         # If both are within this margin of thresholds → neutral


def _sample_skin_pixels(image: np.ndarray, landmarks, img_w: int, img_h: int) -> np.ndarray:
    """
    Extract skin pixel samples from regions around landmark points.

    For each landmark in our sampling set, we grab a circular patch of
    pixels (radius = SAMPLE_RADIUS). This ensures we're sampling actual
    skin and not hair, eyes, or background.

    Returns a 2D array of shape (N, 3) in BGR color space.
    """
    all_pixels = []

    for region_landmarks in SKIN_SAMPLE_LANDMARKS.values():
        for lm_idx in region_landmarks:
            lm = landmarks[lm_idx]
            cx, cy = int(lm.x * img_w), int(lm.y * img_h)

            # Define bounding box for the sampling circle
            y_min = max(0, cy - SAMPLE_RADIUS)
            y_max = min(img_h, cy + SAMPLE_RADIUS)
            x_min = max(0, cx - SAMPLE_RADIUS)
            x_max = min(img_w, cx + SAMPLE_RADIUS)

            # Extract patch and create circular mask
            patch = image[y_min:y_max, x_min:x_max]
            if patch.size == 0:
                continue

            # Create circular mask
            ph, pw = patch.shape[:2]
            Y, X = np.ogrid[:ph, :pw]
            center_y, center_x = ph // 2, pw // 2
            mask = ((X - center_x) ** 2 + (Y - center_y) ** 2) <= SAMPLE_RADIUS ** 2

            pixels = patch[mask]
            if len(pixels) > 0:
                all_pixels.append(pixels)

    if not all_pixels:
        return np.array([])

    return np.vstack(all_pixels)


def _classify_depth(l_value: float) -> str:
    """
    Classify skin depth from the L* (lightness) value.

    L* ranges from 0 (darkest) to 100 (lightest).
    """
    for threshold, label in DEPTH_THRESHOLDS:
        if l_value > threshold:
            return label
    return "deep"


def _classify_undertone(a_value: float, b_value: float) -> str:
    """
    Classify skin undertone from a* and b* channels.

    a* > 0: red/pink bias, a* < 0: green bias
    b* > 0: yellow bias, b* < 0: blue bias

    Warm: High b* (yellow/golden cast)
    Cool: High a* with lower b* (pink/red cast)
    Neutral: Balanced a* and b*
    """
    if b_value > WARM_B_THRESHOLD:
        return "warm"
    elif a_value > COOL_A_THRESHOLD and b_value < WARM_B_THRESHOLD - NEUTRAL_MARGIN:
        return "cool"
    else:
        return "neutral"


def _lab_to_hex(lab_color: np.ndarray) -> str:
    """Convert a single LAB color to hex string via BGR intermediate."""
    lab_pixel = np.uint8([[lab_color.astype(np.uint8)]])
    bgr_pixel = cv2.cvtColor(lab_pixel, cv2.COLOR_LAB2BGR)
    b, g, r = bgr_pixel[0][0]
    return f"#{r:02x}{g:02x}{b:02x}"


def analyze_skin_tone(image: np.ndarray) -> dict | None:
    """
    Analyze skin tone from a face image.

    Args:
        image: OpenCV BGR image containing a face (same image used for face analysis)

    Returns:
        Dict with skin tone classification, or None if analysis fails.
        Example: {
            "depth": "medium",
            "undertone": "warm",
            "hex_color": "#C4956A",
            "confidence": 0.85,
            "low_confidence_flag": False
        }
    """
    # ── Step 1: Detect face and get landmarks ──────────────────────────
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
    results = _face_landmarker.detect(mp_image)

    if not results.face_landmarks:
        return None

    landmarks = results.face_landmarks[0]
    img_h, img_w = image.shape[:2]

    # ── Step 2: Sample skin pixels ─────────────────────────────────────
    skin_pixels = _sample_skin_pixels(image, landmarks, img_w, img_h)
    if len(skin_pixels) < 50:  # Need minimum samples for reliable clustering
        return None

    # ── Step 3: Convert to LAB and apply CLAHE ─────────────────────────
    # Reshape for color conversion (needs 2D image-like shape)
    pixel_row = skin_pixels.reshape(1, -1, 3).astype(np.uint8)
    lab_row = cv2.cvtColor(pixel_row, cv2.COLOR_BGR2LAB)
    lab_pixels = lab_row.reshape(-1, 3).astype(np.float32)

    # Apply CLAHE-style normalization on L channel
    # (For sampled pixels, we normalize L to reduce lighting bias)
    l_channel = lab_pixels[:, 0]
    l_mean = np.mean(l_channel)
    l_std = np.std(l_channel)

    # Normalize L channel to reduce lighting variation
    if l_std > 0:
        lab_pixels[:, 0] = np.clip(
            (l_channel - l_mean) / l_std * 20 + 55,  # Center around L*=55
            0, 100
        )

    # ── Step 4: K-means clustering (K=3) ───────────────────────────────
    # K=3 captures: dominant skin tone, shadow regions, highlight regions
    # The dominant cluster (largest) represents the true skin color
    kmeans = KMeans(n_clusters=3, n_init=10, random_state=42)
    kmeans.fit(lab_pixels)

    # Find the dominant cluster (largest membership)
    labels, counts = np.unique(kmeans.labels_, return_counts=True)
    dominant_idx = labels[np.argmax(counts)]
    dominant_centroid = kmeans.cluster_centers_[dominant_idx]

    # ── Step 5: Classify depth and undertone ────────────────────────────
    l_star, a_star, b_star = dominant_centroid

    depth = _classify_depth(l_star)
    undertone = _classify_undertone(a_star, b_star)

    # Convert dominant color to hex for display
    # Use original (unnormalized) dominant color for accurate hex
    original_kmeans = KMeans(n_clusters=3, n_init=10, random_state=42)
    original_lab = cv2.cvtColor(
        skin_pixels.reshape(1, -1, 3).astype(np.uint8),
        cv2.COLOR_BGR2LAB
    ).reshape(-1, 3).astype(np.float32)
    original_kmeans.fit(original_lab)
    original_labels, original_counts = np.unique(original_kmeans.labels_, return_counts=True)
    original_dominant = original_kmeans.cluster_centers_[
        original_labels[np.argmax(original_counts)]
    ]
    hex_color = _lab_to_hex(original_dominant)

    # ── Step 6: Confidence assessment ──────────────────────────────────
    # High std in lightness suggests mixed lighting (shadows, overexposure)
    # which makes classification less reliable
    raw_l_std = np.std(cv2.cvtColor(
        skin_pixels.reshape(1, -1, 3).astype(np.uint8),
        cv2.COLOR_BGR2LAB
    ).reshape(-1, 3)[:, 0].astype(np.float32))

    # Confidence decreases with lighting variance
    # std < 10: good lighting, std > 30: poor lighting
    confidence = float(np.clip(1.0 - (raw_l_std - 10) / 30, 0.3, 1.0))
    low_confidence_flag = raw_l_std > 25

    return {
        "depth": depth,
        "undertone": undertone,
        "hex_color": hex_color,
        "confidence": round(confidence, 2),
        "low_confidence_flag": low_confidence_flag,
    }
