from functools import lru_cache

import cv2


@lru_cache(maxsize=3)
def _load_model(model_name):
    """Load and cache YOLO weights.

    The model used to be re-read from disk on every call.
    """
    try:
        import yolov5
    except ImportError as exc:
        # yolov5 is intentionally not in requirements.txt: it depends on the
        # non-headless opencv build, which overwrites opencv-python-headless
        # and then needs libGL at import time.
        raise RuntimeError(
            "Object detection needs the optional yolov5 dependency. Install it "
            "with: pip install -r requirements-optional.txt"
        ) from exc

    # The yolov5 package resolves weights by filename, not by bare model name.
    return yolov5.load(f"{model_name}.pt")


def detect_objects_in_frame(video_path, interval, model_name):
    interval = max(int(interval), 1)
    model = _load_model(model_name)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    idx = 0
    results = []
    try:
        while True:
            # grab() advances without decoding, so skipped frames stay cheap.
            if not cap.grab():
                break
            if idx % interval == 0:
                ret, frame = cap.retrieve()
                if not ret:
                    break
                detections = model(frame).pandas().xyxy[0]
                labels = detections['name'].tolist()
                _, buf = cv2.imencode('.jpg', frame)
                results.append((buf.tobytes(), labels))
            idx += 1
    finally:
        cap.release()
    return results
