import cv2
import tempfile
import yolov5

def detect_objects_in_frame(video_path, interval, model_name):
    model = yolov5.load(model_name)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 1
    idx = 0
    results = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % interval == 0:
            detections = model(frame).pandas().xyxy[0]
            labels = detections['name'].tolist()
            _, buf = cv2.imencode('.jpg', frame)
            results.append((buf.tobytes(), labels))
        idx += 1
    cap.release()
    return results