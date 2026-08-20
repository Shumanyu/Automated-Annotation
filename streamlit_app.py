import streamlit as st

from analytics import log_event
from audio_processor import extract_audio_and_transcribe
from export_utils import export_json, export_summary_pdf
from keyframe_extractor import extract_keyframes
from object_detector import detect_objects_in_frame
from search_utils import keyword_search
from summarizer import ai_summarize
from video_processor import cache_video, extract_frames_and_ocr

# --- Page Config & Theme ---
st.set_page_config(
    page_title="Enterprise Video Annotation",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': 'Enterprise-grade prototype for automated video annotation.'
    }
)


# --- Cached pipeline stages ---
# Streamlit reruns this script top to bottom on every widget interaction.
# Uncached, typing a single character into the keyword box would re-run OCR and
# Whisper across the entire video.

@st.cache_data(show_spinner=False)
def run_ocr(path, interval):
    return extract_frames_and_ocr(path, interval)


@st.cache_data(show_spinner=False)
def run_transcription(path):
    return extract_audio_and_transcribe(path)


@st.cache_data(show_spinner=False)
def run_summary(text, model):
    return ai_summarize(text, model)


@st.cache_data(show_spinner=False)
def run_object_detection(path, interval, model):
    return detect_objects_in_frame(path, interval, model)


@st.cache_data(show_spinner=False)
def run_keyframes(path, count):
    return extract_keyframes(path, count)


# --- Sidebar: User Inputs ---
st.sidebar.title("🛠️ Configuration")
video_file = st.sidebar.file_uploader("Upload video", type=["mp4", "mov", "avi", "mkv"])
enable_ocr = st.sidebar.checkbox("Enable OCR", True)
enable_audio = st.sidebar.checkbox("Enable Audio Transcription", True)
enable_objects = st.sidebar.checkbox("Enable Object Detection", False)
enable_keyframes = st.sidebar.checkbox("Enable Keyframe Extraction", False)
enable_analysis = st.sidebar.checkbox("Enable Analytics Logging", False)

frame_interval = st.sidebar.slider("Frame interval", 1, 120, 30)
summarizer_model = st.sidebar.selectbox(
    "Summarizer Model", ["bart-large-cnn", "t5-base", "gpt-3.5-turbo"]
)
object_model = st.sidebar.selectbox(
    "Object Detection Model", ["yolov5s", "yolov5m", "yolov5l"]
)

export_formats = st.sidebar.multiselect(
    "Export Formats", ["txt", "json", "pdf"], default=["txt", "json"]
)

# --- Main Interface ---
st.title("🚀 Enterprise-Grade Video Annotation")

if not video_file:
    st.info("Please upload a video to begin analysis.")
    st.stop()

temp_path = cache_video(video_file)
st.video(temp_path)

results = {}

# The summary always runs, so it counts toward the total. Counting only the
# optional toggles meant the summary pushed progress past 1.0 (which Streamlit
# rejects), and turning every toggle off divided by zero.
total_steps = 1 + sum([enable_ocr, enable_audio, enable_objects, enable_keyframes])
completed = 0
section = 0
progress = st.progress(0.0)


def track(event):
    if enable_analysis:
        log_event(event)


def advance():
    global completed
    completed += 1
    progress.progress(min(completed / total_steps, 1.0))


def heading(label):
    """Number sections by what actually ran, not by a fixed order."""
    global section
    section += 1
    return f"{section}. {label}"


def stage(label, fn, *args):
    """Run one pipeline stage, surfacing failures without killing the page."""
    try:
        return fn(*args)
    except Exception as exc:
        st.error(f"{label} failed: {exc}")
        return None


track("video_upload")

# --- OCR ---
if enable_ocr:
    st.subheader(heading("OCR Text Extraction"))
    with st.spinner("Reading text from frames..."):
        ocr_text = stage("OCR", run_ocr, temp_path, frame_interval)
    if ocr_text is not None:
        st.text_area("OCR Output", ocr_text, height=200)
        results['ocr'] = ocr_text
        track("ocr_done")
    advance()

# --- Audio Transcription ---
if enable_audio:
    st.subheader(heading("Audio Transcription"))
    with st.spinner("Transcribing audio..."):
        transcript = stage("Transcription", run_transcription, temp_path)
    if transcript is not None:
        st.text_area("Transcript", transcript, height=200)
        results['transcript'] = transcript
        track("transcript_done")
    advance()

# --- AI Summarization ---
st.subheader(heading("AI-Generated Summary"))
combined = "\n".join(
    part for part in (results.get('ocr', ''), results.get('transcript', '')) if part
)
with st.spinner("Summarizing..."):
    summary = stage("Summarization", run_summary, combined, summarizer_model)

if summary is not None:
    st.write(summary)
    results['summary'] = summary
    if "pdf" in export_formats:
        pdf_bytes = stage("PDF export", export_summary_pdf, summary)
        if pdf_bytes is not None:
            st.download_button(
                "Download Summary PDF", pdf_bytes, file_name="summary.pdf"
            )
    if "txt" in export_formats:
        st.download_button("Download Summary TXT", summary, file_name="summary.txt")
    track("summary_done")
advance()

# --- Keyword Search ---
with st.expander("Keyword Search"):
    keyword = st.text_input("Enter keyword to search:")
    if keyword:
        hits = keyword_search(combined, keyword)
        st.write(f"Occurrences: {len(hits)}")
        for ts, snippet in hits:
            st.markdown(f"- **{ts}**: {snippet}")
        results['search'] = hits
        track("search_done")

# --- Object Detection ---
if enable_objects:
    st.subheader(heading("Object Detection"))
    with st.spinner("Detecting objects..."):
        objects = stage(
            "Object detection", run_object_detection,
            temp_path, frame_interval, object_model,
        )
    if objects is not None:
        for img_bytes, labels in objects:
            st.image(img_bytes, caption=", ".join(labels), use_container_width=True)
        results['objects'] = objects
        track("objects_done")
    advance()

# --- Keyframe Extraction ---
if enable_keyframes:
    st.subheader(heading("Keyframe Gallery"))
    with st.spinner("Extracting keyframes..."):
        keyframes = stage("Keyframe extraction", run_keyframes, temp_path, 12)
    if keyframes is not None:
        cols = st.columns(4)
        for idx, frame in enumerate(keyframes):
            cols[idx % 4].image(frame, use_container_width=True)
        results['keyframes'] = keyframes
        track("keyframes_done")
    advance()

# --- Export JSON ---
if "json" in export_formats:
    # Detected frames and keyframes are raw image data, so the JSON export
    # carries their counts rather than megabytes of stringified bytes.
    payload = {
        "ocr": results.get('ocr', ''),
        "transcript": results.get('transcript', ''),
        "summary": results.get('summary', ''),
        "search": results.get('search', []),
        "object_frames": len(results.get('objects', [])),
        "keyframes": len(results.get('keyframes', [])),
    }
    st.download_button(
        "Download All Results JSON", export_json(payload), file_name="results.json"
    )
    track("export_json")

# The uploaded video deliberately stays in .cache_videos so reruns (and repeat
# uploads of the same file) reuse it. Deleting it here used to break the very
# next rerun, since Streamlit re-executes this script on every interaction.
