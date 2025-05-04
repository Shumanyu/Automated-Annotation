import cv2
import pytesseract
import os
from pathlib import Path
pytesseract.pytesseract.tesseract_cmd = os.getenv(
    'TESSERACT_CMD', pytesseract.pytesseract.tesseract_cmd
)
#has errors need correction
CACHE_DIR = Path(".cache_videos")
CACHE_DIR.mkdir(exist_ok=True)


def cache_video(uploaded_file):
    """Save uploaded file to cache and return local path."""
    vid_hash = hash(uploaded_file.name + str(uploaded_file.size))
    path = CACHE_DIR / f"video_{vid_hash}.mp4"
    if not path.exists():
        with open(path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
    return str(path)


def extract_frames_and_ocr(video_path: str, interval: int = 30) -> str:
    """Extract OCR text with timestamps from video frames."""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 1.0
    frame_idx = 0
    texts = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % interval == 0:
            timestamp = frame_idx / fps
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(gray)
            if text.strip():
                texts.append(f"[{timestamp:.1f}s] {text.strip()}")
        frame_idx += 1
    cap.release()
    return "
            ".join(texts)
