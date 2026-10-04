"""Evaluator Agent: analyzes a completed teach-back session and produces
a structured report (clarity score, strengths, gaps, revision concepts)
per PRD FR-05 to FR-09."""
from __future__ import annotations

import json
import re

from prompts.prompts import build_evaluator_messages
from services.llm import chat_completion, LLMError


class EvaluatorError(RuntimeError):
    """Raised when the evaluator cannot produce a usable report."""


def _parse_evaluator_json(raw_text: str) -> dict:
    """Strips markdown code fences if present and parses JSON cleanly."""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text.strip(), flags=re.MULTILINE)
    return json.loads(cleaned)


def _clamp_score(value) -> int:
    try:
        score = int(round(float(value)))
    except (TypeError, ValueError):
        score = 5
    return max(1, min(10, score))


def _as_str_list(value) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _first_present(result: dict, *keys: str) -> list[str]:
    """Checks several possible key names, since models don't always use
    the exact field name asked for (e.g. 'weaknesses' instead of 'gaps')."""
    for key in keys:
        found = _as_str_list(result.get(key))
        if found:
            return found
    return []


def _normalize(result: dict) -> dict:
    """Ensures the result always has the exact shape the UI expects,
    even if the model returns slightly malformed JSON."""
    strengths = _first_present(result, "strengths", "positives", "what_went_well")
    gaps = _first_present(result, "gaps", "weaknesses", "areas_to_improve", "missing_points")
    revision_concepts = _first_present(
        result, "revision_concepts", "concepts_to_revise", "next_steps", "topics_to_review"
    )

    # FR-09 requires exactly three revision concepts.
    if len(revision_concepts) > 3:
        revision_concepts = revision_concepts[:3]
    while len(revision_concepts) < 3:
        revision_concepts.append("Review this topic again in more depth.")

    if not strengths:
        strengths = ["No clear strengths identified from this session."]
    if not gaps:
        gaps = ["No specific gaps identified — explanation covered the basics."]

    return {
        "clarity_score": _clamp_score(result.get("clarity_score")),
        "strengths": strengths,
        "gaps": gaps,
        "revision_concepts": revision_concepts,
    }


def evaluate_session(topic: str, qa_pairs: list[dict[str, str]], retries: int = 2) -> dict:
    """
    Analyzes the full teach-back conversation and returns a structured report:
        {
            "clarity_score": int (1-10),
            "strengths": [str, ...],
            "gaps": [str, ...],
            "revision_concepts": [str, str, str],
        }

    Retries on transient API/JSON failures (large structured responses can
    occasionally get truncated), then falls back to a safe default report
    rather than crashing the app (PRD FR-13).
    """
    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("Topic is required to evaluate a session.")

    last_error = None
    for attempt in range(retries + 1):
        try:
            raw = chat_completion(
                build_evaluator_messages(topic, qa_pairs),
                temperature=0.3,
                max_tokens=2048,
            )
            print(f"[evaluate_session] Raw model output: {raw!r}")
            parsed = _parse_evaluator_json(raw)
            normalized = _normalize(parsed)
            print(f"[evaluate_session] Normalized result: {normalized!r}")
            return normalized
        except (LLMError, json.JSONDecodeError, ValueError) as e:
            last_error = e
            print(f"[evaluate_session] Attempt {attempt + 1}/{retries + 1} failed: {e}")

    print(f"[evaluate_session] All attempts failed. Last error: {last_error}")
    # Safe fallback so the UI can still show a report instead of crashing.
    return {
        "clarity_score": 5,
        "strengths": ["Unable to generate a full evaluation right now."],
        "gaps": ["The evaluation service did not return a usable response. Please try again."],
        "revision_concepts": [
            "Try evaluating this session again.",
            "Review your explanation once more.",
            "Check your internet/API connection.",
        ],
    }
