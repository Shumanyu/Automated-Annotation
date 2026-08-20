import os
import shutil
import subprocess
import tempfile

# "small" is a ~460MB download and slow on CPU; override for faster runs.
MODEL_SIZE = os.getenv("WHISPER_MODEL", "small")

_model = None


def _load_model():
    """Load Whisper on first use, so the import cost is only paid if audio
    transcription is actually enabled."""
    global _model
    if _model is None:
        import whisper

        _model = whisper.load_model(MODEL_SIZE)
    return _model


def extract_audio_and_transcribe(video_path):
    """Extract audio using ffmpeg and transcribe with Whisper."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg was not found on PATH. See the README for install steps."
        )

    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_wav.close()
    try:
        result = subprocess.run(
            [
                "ffmpeg", "-y", "-i", video_path,
                "-ac", "1", "-ar", "16000", temp_wav.name,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            # stderr used to be discarded, so a failed extraction surfaced
            # later as a confusing Whisper error about an empty file.
            detail = result.stderr.decode("utf-8", "replace").strip().splitlines()
            raise RuntimeError(
                "ffmpeg could not extract audio: "
                + (detail[-1] if detail else "no error output")
            )

        transcription = _load_model().transcribe(temp_wav.name)
        return transcription.get("text", "").strip()
    finally:
        if os.path.exists(temp_wav.name):
            os.remove(temp_wav.name)
