import cv2

def extract_keyframes(video_path, num_keyframes=12):
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(total // num_keyframes, 1)
    frames = []
    for i in range(num_keyframes):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i*step)
        ret, frame = cap.read()
        if not ret: break
        frames.append(frame[:, :, ::-1])
    cap.release()
    return frames