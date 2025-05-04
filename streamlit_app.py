import streamlit as st
from video_processor import extract_frames_and_ocr, cache_video
from audio_processor import extract_audio_and_transcribe
from summarizer import ai_summarize
from search_utils import keyword_search
from object_detector import detect_objects_in_frame
from keyframe_extractor import extract_keyframes
from analytics import log_event
from export_utils import export_summary_pdf, export_json
import tempfile
import os

# --- Page Config & Theme ---
st.set_page_config(
    page_title="Enterprise Video Annotation",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': 'Enterprise-grade prototype for automated video annotation.'
    }
)

# --- Sidebar: User Inputs ---
st.sidebar.title("🛠️ Configuration")
video_file = st.sidebar.file_uploader("Upload video", type=["mp4","mov","avi","mkv"])
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

if video_file:
    # Caching: Save & reuse video path
    temp_path = cache_video(video_file)
    log_event("video_upload") if enable_analysis else None

    # Display video player
    st.video(temp_path)

    # Prepare result containers
    results = {}
    progress = st.progress(0)
    step_count = sum([enable_ocr, enable_audio, enable_objects, enable_keyframes])
    step = 0

    # --- OCR ---
    if enable_ocr:
        st.subheader("1. OCR Text Extraction 📄")
        ocr_text = extract_frames_and_ocr(temp_path, frame_interval)
        st.text_area("OCR Output", ocr_text, height=200)
        results['ocr'] = ocr_text
        step += 1
        progress.progress(step/step_count)
        log_event("ocr_done") if enable_analysis else None

    # --- Audio Transcription ---
    if enable_audio:
        st.subheader("2. Audio Transcription 🔊")
        transcript = extract_audio_and_transcribe(temp_path)
        st.text_area("Transcript", transcript, height=200)
        results['transcript'] = transcript
        step += 1
        progress.progress(step/step_count)
        log_event("transcript_done") if enable_analysis else None

    # --- AI Summarization ---
    st.subheader("3. AI-Generated Summary 🤖")
    combined = "\n".join([results.get('ocr',''), results.get('transcript','')])
    summary = ai_summarize(combined, summarizer_model)
    st.write(summary)
    results['summary'] = summary
    if "pdf" in export_formats:
        pdf_bytes = export_summary_pdf(summary)
        st.download_button("Download Summary PDF", pdf_bytes, file_name="summary.pdf")
    if "txt" in export_formats:
        st.download_button("Download Summary TXT", summary, file_name="summary.txt")
    step += 1
    progress.progress(step/step_count)
    log_event("summary_done") if enable_analysis else None

    # --- Keyword Search ---
    with st.expander("🔍 Keyword Search"):
        keyword = st.text_input("Enter keyword to search:")
        if keyword:
            hits = keyword_search(combined, keyword)
            st.write(f"Occurrences: {len(hits)}")
            for ts, snippet in hits:
                st.markdown(f"- **{ts}**: {snippet}")
            results['search'] = hits
            log_event("search_done") if enable_analysis else None

    # --- Object Detection ---
    if enable_objects:
        st.subheader("4. Object Detection 🔎")
        objects = detect_objects_in_frame(temp_path, frame_interval, object_model)
        for img_bytes, labels in objects:
            st.image(img_bytes, caption=", ".join(labels), use_column_width=True)
        results['objects'] = objects
        step += 1
        progress.progress(step/step_count)
        log_event("objects_done") if enable_analysis else None

    # --- Keyframe Extraction ---
    if enable_keyframes:
        st.subheader("5. Keyframe Gallery 📸")
        keyframes = extract_keyframes(temp_path, num_keyframes=12)
        cols = st.columns(4)
        for idx, frame in enumerate(keyframes):
            cols[idx % 4].image(frame, use_column_width=True)
        results['keyframes'] = keyframes
        step += 1
        progress.progress(step/step_count)
        log_event("keyframes_done") if enable_analysis else None

    # --- Export JSON --- no need    
   ''' if "json" in export_formats:
        json_bytes = export_json(results)
        st.download_button("Download All Results JSON", json_bytes, file_name="results.json")
        log_event("export_json") if enable_analysis else None
'''
    # Cleanup
    os.remove(temp_path)

else:
    st.info("Please upload a video to begin analysis.")
