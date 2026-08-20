from summarizer import HF_MODELS, ai_summarize


def test_importing_does_not_require_an_openai_key(monkeypatch):
    """Regression: the module raised ValueError at import time when
    OPENAI_API_KEY was unset, which took the whole app down even for users
    who had selected a HuggingFace model."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    import importlib

    import summarizer

    importlib.reload(summarizer)


def test_empty_text_short_circuits():
    """Must not load a 1.6GB model just to summarize nothing."""
    assert "Nothing to summarize" in ai_summarize("")
    assert "Nothing to summarize" in ai_summarize("   \n  ")


def test_t5_maps_to_its_own_checkpoint():
    """Regression: the pipeline was hardcoded to BART, so picking t5-base in
    the UI silently ran a different model than the one displayed."""
    assert HF_MODELS["t5-base"] == "t5-base"
    assert HF_MODELS["bart-large-cnn"] == "facebook/bart-large-cnn"
