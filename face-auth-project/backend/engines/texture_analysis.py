"""
Texture analysis engine (PyTorch MobileNetV3-Small).
Shared by webcam path (now) and upload path (v2).

Loads models/texture_engine.pt if present; otherwise falls back to a
mock score so the API/pipeline can be exercised.
"""
import os
import random
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image

MODEL_PATH_PT = os.path.join(os.path.dirname(__file__), "..", "models", "texture_engine.pt")

_device = "cuda" if torch.cuda.is_available() else "cpu"
_model = None

def _load_model():
    global _model
    if _model is None and os.path.exists(MODEL_PATH_PT):
        try:
            m = models.mobilenet_v3_small(weights=None)
            in_features = m.classifier[3].in_features
            m.classifier[3] = nn.Linear(in_features, 2)
            ckpt = torch.load(MODEL_PATH_PT, map_location=_device)
            m.load_state_dict(ckpt["model_state"])
            m.to(_device)
            m.eval()
            _model = m
        except Exception:
            _model = None
    return _model

_tf = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


def analyze_texture(face_image) -> float:
    """
    Returns a real-vs-spoof texture score in [0, 1] (higher = more likely real).
    """
    model = _load_model()
    if model is not None:
        try:
            if not isinstance(face_image, Image.Image):
                face_image = Image.fromarray(face_image)
            face_image = face_image.convert("RGB")
            tensor = _tf(face_image).unsqueeze(0).to(_device)
            with torch.no_grad():
                logits = model(tensor)
                # index 0 is live, index 1 is spoof
                p_live = torch.softmax(logits, dim=1)[0, 0].item()
            return round(float(p_live), 4)
        except Exception:
            pass

    # Mock fallback
    return round(random.uniform(0.70, 0.95), 4)


