"""Evaluator Agent: evaluates user explanations and Q&A to generate structured report."""
from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any

from prompts.prompts import build_evaluator_messages
from services.llm import chat_completion

WEAK_SCORE_THRESHOLD = 7


def extract_json_payload(text: str) -> dict[str, Any]:
    """Extract and parse JSON object from LLM output, handling markdown blocks or plain text."""
    text = text.strip()
    # Strip markdown codeblock backticks if present
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

    # Try direct parse
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    # Search for first '{' to last '}'
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Failed to parse valid JSON from evaluator response: {text[:100]}...")


class EvaluatorAgent:
    """Evaluate a Feynman learning session and generate a structured gap report."""

    def __init__(self, model: str | None = None, weak_threshold: int = WEAK_SCORE_THRESHOLD):
        self.model = model
        self.weak_threshold = weak_threshold

    def evaluate_session(
        self,
        topic: str,
        level: str,
        initial_explanation: str,
        conversation: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """Evaluate explanation and conversation history, returning a normalized report dict."""
        for value, label in (
            (topic, "Topic"),
            (level, "Learner level"),
            (initial_explanation, "Initial explanation"),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{label} is required.")

        messages = build_evaluator_messages(topic, level, initial_explanation, conversation)
        raw_response = chat_completion(
            messages,
            temperature=0.3,
            max_tokens=600,
            model=self.model,
        )

        parsed = extract_json_payload(raw_response)
        return self._normalize_report(topic, level, parsed)

    def _normalize_report(self, topic: str, level: str, raw: dict[str, Any]) -> dict[str, Any]:
        """Validate and format fields according to PRD requirements."""
        # 1. Score (1 to 10)
        raw_score = raw.get("score")
        try:
            score = int(raw_score)
        except (TypeError, ValueError):
            score = 5
        score = max(1, min(10, score))

        # 2. Strengths
        strengths = raw.get("strengths", [])
        if not isinstance(strengths, list):
            strengths = [str(strengths)] if strengths else []
        strengths = [str(s).strip() for s in strengths if str(s).strip()]
        if not strengths:
            strengths = ["Learner initiated explanation of topic."]

        # 3. Gaps (with quotes/evidence references)
        gaps = raw.get("gaps", [])
        if not isinstance(gaps, list):
            gaps = [str(gaps)] if gaps else []
        gaps = [str(g).strip() for g in gaps if str(g).strip()]
        if not gaps:
            gaps = ["No major knowledge gaps identified."]

        # 4. Revision concepts (exactly 3 items required by PRD)
        raw_revisions = raw.get("revision_concepts", [])
        if not isinstance(raw_revisions, list):
            raw_revisions = [str(raw_revisions)] if raw_revisions else []
        revisions = [str(r).strip() for r in raw_revisions if str(r).strip()]

        # Ensure exactly 3 revision concepts
        while len(revisions) < 3:
            default_concepts = [
                f"Core fundamentals of {topic}",
                f"Practical examples and applications of {topic}",
                f"Key terminology and edge cases in {topic}",
            ]
            for default_item in default_concepts:
                if default_item not in revisions and len(revisions) < 3:
                    revisions.append(default_item)

        revisions = revisions[:3]

        # 5. Summary
        summary = str(raw.get("summary", "")).strip()
        if not summary:
            summary = f"Session evaluated with clarity score of {score}/10."

        is_weak = score < self.weak_threshold

        return {
            "topic": topic.strip(),
            "level": level.strip(),
            "score": score,
            "is_weak": is_weak,
            "strengths": strengths,
            "gaps": gaps,
            "revision_concepts": revisions,
            "summary": summary,
            "timestamp": datetime.now().isoformat(),
        }


def generate_evaluation_report(
    topic: str,
    level: str,
    initial_explanation: str,
    conversation: list[dict[str, str]] | None = None,
    weak_threshold: int = WEAK_SCORE_THRESHOLD,
) -> dict[str, Any]:
    """Convenience function for generating an evaluation report."""
    agent = EvaluatorAgent(weak_threshold=weak_threshold)
    return agent.evaluate_session(topic, level, initial_explanation, conversation)
