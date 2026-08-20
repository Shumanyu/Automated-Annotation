import cv2


def extract_keyframes(video_path, num_keyframes=12):
    """Sample evenly spaced frames from the video as RGB arrays."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    frames = []
    try:
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total <= 0:
            # Some containers report no frame count; read sequentially instead.
            while len(frames) < num_keyframes:
                ret, frame = cap.read()
                if not ret:
                    break
                frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            return frames

        step = max(total // num_keyframes, 1)
        for i in range(num_keyframes):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i * step)
            ret, frame = cap.read()
            if not ret:
                break
            # cvtColor returns a contiguous array; frame[:, :, ::-1] would hand
            # Streamlit a negative-stride view that some encoders reject.
            frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    finally:
        cap.release()
    return frames
