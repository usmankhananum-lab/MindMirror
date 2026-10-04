"""Small, centralized wrapper around the Groq chat-completions API."""
from __future__ import annotations
import os
from typing import Any
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "openai/gpt-oss-20b"

class LLMError(RuntimeError):
    """Raised when the model cannot be called or returns no usable text."""

def chat_completion(messages: list[dict[str, str]], *, temperature: float = 0.6,
                    max_tokens: int = 256, model: str | None = None) -> str:
    """Call Groq. Configure GROQ_API_KEY in env or Streamlit secrets."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("GROQ_API_KEY")
        except Exception:
            api_key = None
    if not api_key:
        raise LLMError("GROQ_API_KEY is not configured.")
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        response: Any = client.chat.completions.create(
            model=model or os.getenv("GROQ_MODEL", DEFAULT_MODEL),
            messages=messages, temperature=temperature, max_tokens=max_tokens,
        )
        result = response.choices[0].message.content
        if not result or not result.strip():
            raise LLMError("The model returned an empty response.")
        return result.strip()
    except LLMError:
        raise
    except Exception as exc:
        raise LLMError(f"Groq request failed: {exc}") from exc
