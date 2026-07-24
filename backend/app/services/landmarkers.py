"""
Shared MediaPipe landmarker instances.

Three call sites need a landmarker and two of them need the same face model.
Building them at import time meant loading ~40MB of TFLite graphs twice, and
paying that cost even for `flask db upgrade` or a test run that never touches
an image. They are created lazily here instead, once per process.

MediaPipe task objects hold mutable inference state and are not safe to call
concurrently, so `detect` is wrapped behind a lock rather than exposing the
raw objects.
"""
import os
import threading

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

_MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

_face_landmarker = None
_pose_landmarker = None
_init_lock = threading.Lock()
_face_lock = threading.Lock()
_pose_lock = threading.Lock()


def _build_face_landmarker():
    options = vision.FaceLandmarkerOptions(
        base_options=python.BaseOptions(
            model_asset_path=os.path.join(_MODEL_DIR, "face_landmarker.task")
        ),
        output_face_blendshapes=False,
        output_facial_transformation_matrixes=False,
        num_faces=1,
    )
    return vision.FaceLandmarker.create_from_options(options)


def _build_pose_landmarker():
    options = vision.PoseLandmarkerOptions(
        base_options=python.BaseOptions(
            model_asset_path=os.path.join(_MODEL_DIR, "pose_landmarker.task")
        ),
        output_segmentation_masks=False,
        num_poses=1,
    )
    return vision.PoseLandmarker.create_from_options(options)


def detect_face(mp_image):
    """Run face mesh detection. Thread-safe."""
    global _face_landmarker
    if _face_landmarker is None:
        with _init_lock:
            if _face_landmarker is None:
                _face_landmarker = _build_face_landmarker()

    with _face_lock:
        return _face_landmarker.detect(mp_image)


def detect_pose(mp_image):
    """Run pose detection. Thread-safe."""
    global _pose_landmarker
    if _pose_landmarker is None:
        with _init_lock:
            if _pose_landmarker is None:
                _pose_landmarker = _build_pose_landmarker()

    with _pose_lock:
        return _pose_landmarker.detect(mp_image)


def warm_up() -> None:
    """
    Force both models to load.

    Called at boot on hosts where the first user request would otherwise
    absorb the several-second model load.
    """
    global _face_landmarker, _pose_landmarker
    with _init_lock:
        if _face_landmarker is None:
            _face_landmarker = _build_face_landmarker()
        if _pose_landmarker is None:
            _pose_landmarker = _build_pose_landmarker()
