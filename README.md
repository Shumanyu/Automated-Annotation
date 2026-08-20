# Automated Video Annotation

A Streamlit app that takes a video and produces a searchable, exportable set of
annotations from it: on-screen text via OCR, a spoken-word transcript via
Whisper, an AI-generated summary, detected objects, and a keyframe gallery.

Everything runs locally except the optional GPT summarizer.

## What it does

| Stage | Backed by | Notes |
|---|---|---|
| OCR text extraction | Tesseract (`pytesseract`) | Samples one frame every *N*, timestamps each hit |
| Audio transcription | OpenAI Whisper (local) | ffmpeg extracts 16kHz mono audio first |
| Summarization | BART / T5 locally, or GPT via API | Only the selected model is downloaded |
| Keyword search | stdlib `re` | Reports the timestamp each hit falls under |
| Object detection | YOLOv5 | Optional; off by default |
| Keyframe gallery | OpenCV | Evenly spaced samples |
| Export | `fpdf2`, JSON, plain text | Choose formats in the sidebar |

## Requirements

Two system binaries have to be installed separately — they are not Python
packages.

### Tesseract OCR

- **Ubuntu/Debian**: `sudo apt install tesseract-ocr`
- **macOS**: `brew install tesseract`
- **Windows**: install from [Tesseract Releases](https://github.com/tesseract-ocr/tesseract/releases),
  default path `C:\Program Files\Tesseract-OCR`, then add that folder to your
  `PATH`. Verify with `tesseract --version`.

If you cannot edit `PATH`, point at the binary directly instead:

```bash
export TESSERACT_CMD="C:/Program Files/Tesseract-OCR/tesseract.exe"
```

### FFmpeg

- **Ubuntu/Debian**: `sudo apt install ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Windows**: grab a static build from [ffmpeg.org](https://ffmpeg.org/download.html),
  extract it, and add its `bin` folder to `PATH`. Verify with `ffmpeg -version`.

## Install and run

```bash
pip install -r requirements.txt
```

```bash
streamlit run streamlit_app.py
```

The app opens at <http://localhost:8501>. Upload a video, pick your stages in
the sidebar, and results appear as each stage finishes.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `TESSERACT_CMD` | system `PATH` | Absolute path to the Tesseract binary |
| `WHISPER_MODEL` | `small` | Whisper size — `tiny` and `base` are far faster on CPU |
| `OPENAI_API_KEY` | unset | Only needed for the `gpt-3.5-turbo` summarizer |

The OpenAI key can also live in Streamlit secrets:

```toml
# .streamlit/secrets.toml
[openai]
api_key = "sk-..."
```

Both HuggingFace models work with no key at all.

## Notes on behaviour

- **Uploads are cached.** Videos land in `.cache_videos/`, keyed by name and
  size, so reruns and repeat uploads reuse them. The directory is gitignored
  and safe to delete; it is not cleaned automatically.
- **Stages are cached too.** Streamlit re-executes the whole script on every
  widget interaction, so each stage is wrapped in `@st.cache_data`. Without
  that, typing in the keyword box would re-run OCR and Whisper on the video.
- **Models download on first use**, not at startup — BART is ~1.6GB and
  Whisper `small` ~460MB. The first run of a given model is slow.
- **A failing stage does not kill the page.** Errors are surfaced in place and
  the remaining stages still run.

## Development

```bash
pip install -r requirements-dev.txt
```

```bash
pytest -q
```

`requirements-dev.txt` deliberately omits torch, Whisper and YOLOv5 so the test
suite stays fast; the tests cover the pure logic (search, exports, cache keys,
summarizer dispatch).

CI runs three gates on every push and PR: `compileall` for syntax, `ruff` for
lint, and `pytest`.

## Project layout

```
streamlit_app.py       UI, stage orchestration, caching
video_processor.py     upload caching + frame sampling and OCR
audio_processor.py     ffmpeg audio extraction + Whisper transcription
summarizer.py          HuggingFace / OpenAI summarization
object_detector.py     YOLOv5 detection over sampled frames
keyframe_extractor.py  evenly spaced frame sampling
search_utils.py        timestamped keyword search
export_utils.py        JSON and PDF export
analytics.py           best-effort local event log
```
