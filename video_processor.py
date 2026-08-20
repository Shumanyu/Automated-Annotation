import hashlib
import os
from pathlib import Path

import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = os.getenv(
    'TESSERACT_CMD', pytesseract.pytesseract.tesseract_cmd
)

CACHE_DIR = Path(".cache_videos")
CACHE_DIR.mkdir(exist_ok=True)


def cache_key(name: str, size: int) -> str:
    """Stable cache key for an upload.

    Python's built-in hash() is salted per process, so it cannot be used here:
    the same upload would land on a different filename after every restart and
    the cache would never hit.
    """
    return hashlib.sha256(f"{name}:{size}".encode()).hexdigest()[:16]


def cache_video(uploaded_file):
    """Save uploaded file to cache and return local path."""
    path = CACHE_DIR / f"video_{cache_key(uploaded_file.name, uploaded_file.size)}.mp4"
    if not path.exists():
        with open(path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
    return str(path)


def extract_frames_and_ocr(video_path: str, interval: int = 30) -> str:
    """Extract OCR text with timestamps from video frames."""
    interval = max(int(interval), 1)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 0:
        fps = 1.0

    frame_idx = 0
    texts = []
    try:
        while True:
            # grab() advances without decoding, so skipped frames stay cheap.
            if not cap.grab():
                break
            if frame_idx % interval == 0:
                ret, frame = cap.retrieve()
                if not ret:
                    break
                timestamp = frame_idx / fps
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                text = pytesseract.image_to_string(gray)
                if text.strip():
                    texts.append(f"[{timestamp:.1f}s] {text.strip()}")
            frame_idx += 1
    finally:
        cap.release()

    return "\n".join(texts)
