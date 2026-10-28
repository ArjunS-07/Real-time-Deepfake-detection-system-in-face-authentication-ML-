"""
Shared preprocessing: face detection, alignment, normalization.
Used by both the webcam path (now) and the upload path (v2).

Currently returns MOCK-friendly output (best-effort MediaPipe detection
with a graceful fallback) so the rest of the pipeline can run even before
this is fully tuned.
"""
import numpy as np

try:
    import mediapipe as mp
    _mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
    )
    _mp_face_detection = mp.solutions.face_detection.FaceDetection(
        model_selection=0,
        min_detection_confidence=0.5,
    )
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    _mp_face_mesh = None
    _mp_face_detection = None
    MEDIAPIPE_AVAILABLE = False

FACE_MARGIN = 0.35  # Matches FACE_MARGIN in 01_clean_and_organize.py used during training


def detect_and_align(image: "PIL.Image.Image"):
    """
    Detect the face, crop/align it, and return:
        (face_crop: PIL.Image or None, landmarks: list[(x,y)] or None)

    Returns (None, None) if no face is detected.
    Uses FACE_MARGIN = 0.35 to match the crop distribution used to train texture_engine.pt.
    """
    if not MEDIAPIPE_AVAILABLE:
        # TODO(real-model): raise/log clearly once mediapipe is installed in the env
        return image, None

    rgb = np.array(image)
    h, w, _ = rgb.shape

    # 1. 3D Facial Landmarks via FaceMesh (normalized [0, 1] for landmark coherence and biological cues)
    landmarks = None
    mesh_results = _mp_face_mesh.process(rgb)
    if mesh_results.multi_face_landmarks:
        landmarks = [
            (lm.x, lm.y, lm.z) for lm in mesh_results.multi_face_landmarks[0].landmark
        ]

    # 2. Face crop via FaceDetection with 0.35 margin (exact same crop as training pipeline)
    det_results = _mp_face_detection.process(rgb) if _mp_face_detection else None

    if det_results and det_results.detections:
        best = max(
            det_results.detections,
            key=lambda d: d.location_data.relative_bounding_box.width
            * d.location_data.relative_bounding_box.height,
        )
        box = best.location_data.relative_bounding_box
        x1 = box.xmin * w
        y1 = box.ymin * h
        bw = box.width * w
        bh = box.height * h

        mx = bw * FACE_MARGIN
        my = bh * FACE_MARGIN
        x_min = max(0, int(x1 - mx))
        y_min = max(0, int(y1 - my))
        x_max = min(w, int(x1 + bw + 2 * mx))
        y_max = min(h, int(y1 + bh + 2 * my))
    elif landmarks:
        # Fallback to FaceMesh landmarks bounding box with 0.35 margin
        xs = [p[0] * w for p in landmarks]
        ys = [p[1] * h for p in landmarks]
        bw = max(xs) - min(xs)
        bh = max(ys) - min(ys)
        mx = bw * FACE_MARGIN
        my = bh * FACE_MARGIN
        x_min = max(0, int(min(xs) - mx))
        y_min = max(0, int(min(ys) - my))
        x_max = min(w, int(max(xs) + mx))
        y_max = min(h, int(max(ys) + my))
    else:
        return None, None

    if x_max <= x_min or y_max <= y_min:
        return None, None

    face_crop = image.crop((x_min, y_min, x_max, y_max))
    return face_crop, landmarks


def normalize(face_image: "PIL.Image.Image", size=(224, 224)):
    """Resize + normalize a face crop for model input."""
    return face_image.resize(size)

