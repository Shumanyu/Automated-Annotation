import os
from functools import lru_cache

import streamlit as st

# Model id behind each option offered in the UI. The pipeline used to be
# hardcoded to bart-large-cnn, so picking "t5-base" silently ran BART.
HF_MODELS = {
    "bart-large-cnn": "facebook/bart-large-cnn",
    "t5-base": "t5-base",
}

# BART and T5 both cap encoder input at 1024 tokens; ~4 chars per token gives a
# safe character budget to trim to before the tokenizer sees it.
MAX_INPUT_CHARS = 4000


def _api_key():
    key = os.getenv("OPENAI_API_KEY")
    try:
        if "openai" in st.secrets:
            key = st.secrets.openai.api_key
    except Exception:
        # st.secrets raises outright when no secrets.toml exists; the
        # environment variable is a perfectly good answer on its own.
        pass
    return key


@lru_cache(maxsize=2)
def _hf_summarizer(model_id: str):
    """Load a HuggingFace pipeline on first use.

    Loading at import time pulled ~1.6GB of weights before the app could render
    a single widget, even for users who had selected an OpenAI model.
    """
    from transformers import pipeline

    return pipeline("summarization", model=model_id)


def _openai_client():
    from openai import OpenAI

    key = _api_key()
    if not key:
        # Raised here rather than at import, so the HuggingFace models stay
        # usable without an OpenAI account.
        raise ValueError(
            "OpenAI API key not found. Set OPENAI_API_KEY or add it to "
            "Streamlit secrets to use the GPT models."
        )
    return OpenAI(api_key=key)


def ai_summarize(
    text: str,
    model_name: str = "bart-large-cnn",
    max_length: int = 200,
    min_length: int = 50,
) -> str:
    """Summarize text with the selected model.

    Supports HuggingFace ('bart-large-cnn', 't5-base') and OpenAI chat models.
    """
    text = (text or "").strip()
    if not text:
        return "Nothing to summarize — enable OCR or audio transcription first."

    if model_name in HF_MODELS:
        summarizer = _hf_summarizer(HF_MODELS[model_name])
        # Asking for a summary longer than the source makes these models
        # ramble or fail outright, so clamp to the input length.
        budget = max(len(text.split()), 1)
        upper = max(min(max_length, budget), 1)
        lower = min(min_length, max(upper - 1, 1))
        output = summarizer(
            text[:MAX_INPUT_CHARS],
            max_length=upper,
            min_length=lower,
            do_sample=False,
            truncation=True,
        )
        return output[0]["summary_text"]

    response = _openai_client().chat.completions.create(
        model=model_name,
        messages=[{
            "role": "user",
            "content": f"Summarize the following text concisely:\n\n{text}",
        }],
    )
    return response.choices[0].message.content.strip()
