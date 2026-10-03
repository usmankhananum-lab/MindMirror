import unittest
from unittest.mock import patch

from modules.evaluator import (
    EvaluatorAgent,
    extract_json_payload,
    generate_evaluation_report,
)
from prompts.prompts import build_evaluator_messages


class EvaluatorPromptTests(unittest.TestCase):
    def test_build_evaluator_messages_structure(self):
        messages = build_evaluator_messages(
            topic="Recursion",
            level="Beginner",
            initial_explanation="Functions calling themselves until a base case is hit.",
            conversation=[
                {"role": "user", "content": "What is a base case?"},
                {"role": "assistant", "content": "It stops the loop."},
            ],
        )
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("Recursion", messages[1]["content"])
        self.assertIn("Functions calling themselves", messages[1]["content"])
        self.assertIn("[Learner]: What is a base case?", messages[1]["content"])


class JSONExtractionTests(unittest.TestCase):
    def test_extract_clean_json(self):
        text = '{"score": 8, "summary": "Good job!"}'
        payload = extract_json_payload(text)
        self.assertEqual(payload["score"], 8)

    def test_extract_markdown_wrapped_json(self):
        text = '```json\n{"score": 7, "summary": "Decent"}\n```'
        payload = extract_json_payload(text)
        self.assertEqual(payload["score"], 7)

    def test_extract_embedded_json(self):
        text = 'Here is the report:\n{"score": 9, "summary": "Great"}\nHope this helps!'
        payload = extract_json_payload(text)
        self.assertEqual(payload["score"], 9)

    def test_invalid_json_raises_value_error(self):
        with self.assertRaises(ValueError):
            extract_json_payload("No JSON here!")


class EvaluatorAgentTests(unittest.TestCase):
    @patch("modules.evaluator.chat_completion")
    def test_evaluate_session_normalizes_report(self, mock_completion):
        mock_completion.return_value = '''```json
{
  "score": 9,
  "strengths": ["Clear base case explanation"],
  "gaps": ["Did not mention call stack memory"],
  "revision_concepts": ["Call stack", "Stack overflow"],
  "summary": "Solid explanation with minor gaps."
}
```'''
        report = generate_evaluation_report(
            topic="Recursion",
            level="Intermediate",
            initial_explanation="Recursion is when a function calls itself.",
        )
        self.assertEqual(report["score"], 9)
        self.assertFalse(report["is_weak"])
        self.assertEqual(len(report["revision_concepts"]), 3)
        self.assertEqual(report["strengths"], ["Clear base case explanation"])

    @patch("modules.evaluator.chat_completion")
    def test_vague_explanation_marked_weak(self, mock_completion):
        mock_completion.return_value = '''{
  "score": 4,
  "strengths": ["Attempted response"],
  "gaps": ["Explanation was extremely vague and lacked details"],
  "revision_concepts": ["Basics", "Definitions", "Examples"],
  "summary": "Needs significant revision."
}'''
        agent = EvaluatorAgent(weak_threshold=7)
        report = agent.evaluate_session(
            topic="Quantum Computing",
            level="Beginner",
            initial_explanation="It is fast physics magic.",
        )
        self.assertEqual(report["score"], 4)
        self.assertTrue(report["is_weak"])

    def test_evaluator_rejects_empty_inputs(self):
        agent = EvaluatorAgent()
        with self.assertRaises(ValueError):
            agent.evaluate_session("", "Beginner", "Valid explanation")
        with self.assertRaises(ValueError):
            agent.evaluate_session("Topic", "", "Valid explanation")
        with self.assertRaises(ValueError):
            agent.evaluate_session("Topic", "Beginner", "")


if __name__ == "__main__":
    unittest.main()
