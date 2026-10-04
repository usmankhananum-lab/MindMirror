"""Confused Student Agent: asks one beginner question per explanation round."""
from __future__ import annotations

from prompts.prompts import build_student_messages
from services.llm import chat_completion


class ConfusedStudentAgent:
    """Generate focused follow-up questions for a Feynman learning session."""

    def __init__(self, model: str | None = None):
        self.model = model

    def ask_question(
        self,
        topic: str,
        level: str,
        explanation: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        for value, label in ((topic, "Topic"), (level, "Learner level"),
                             (explanation, "Explanation")):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{label} is required.")

        raw = chat_completion(
            build_student_messages(topic, level, explanation, history),
            temperature=0.7,
            max_tokens=600,
            model=self.model,
        )
        question = raw.strip().splitlines()[0].strip()
        # Normalize common model formatting while preserving one question.
        question = question.lstrip("-*•0123456789. )")
        if "?" in question:
            question = question[: question.find("?") + 1]
        else:
            question = question.rstrip(".! ") + "?"
        if not question or question == "?":
            raise ValueError("The student agent returned an empty question.")
        return question


def generate_student_question(
    topic: str,
    level: str,
    explanation: str,
    history: list[dict[str, str]] | None = None,
) -> str:
    """Convenience function for callers that do not need an agent instance."""
    return ConfusedStudentAgent().ask_question(topic, level, explanation, history)


def validate_round_count(rounds: int) -> int:
    """Validate the PRD's supported 3–5 question rounds."""
    if isinstance(rounds, bool) or not isinstance(rounds, int) or not 3 <= rounds <= 5:
        raise ValueError("Round count must be an integer from 3 to 5.")
    return rounds
