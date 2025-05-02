import os
import streamlit as st
from transformers import pipeline
from openai import OpenAI

# Determine API key: environment variable or Streamlit secrets
api_key = os.getenv("OPENAI_API_KEY")
if hasattr(st, 'secrets') and 'openai' in st.secrets:
    api_key = st.secrets.openai.api_key
if not api_key:
    raise ValueError(
        "OpenAI API key not found. Set OPENAI_API_KEY or Streamlit secrets."
    )

# Initialize OpenAI client with explicit key
openai = OpenAI(api_key=api_key)

# Initialize Hugging Face summarizer
hf_summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn"
)


def ai_summarize(
    text: str,
    model_name: str = "bart-large-cnn",
    max_length: int = 200,
    min_length: int = 50
) -> str:
    """
    Generate a summary using the specified model.
    Supports Hugging Face ('bart-large-cnn', 't5-base') and OpenAI ('gpt-3.5-turbo').
    """
    # Use Hugging Face for BART/T5 models
    if model_name in ["bart-large-cnn", "t5-base"]:
        output = hf_summarizer(
            text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False
        )
        return output[0]["summary_text"]

    # Use OpenAI for GPT models
    prompt = "Summarize the following text concisely:" + text
    response = openai.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()