import json
import os
import tempfile
import unittest

from services.memory import (
    MemoryManager,
    is_weak_topic,
    load_memory,
    save_session,
)


class MemoryManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file = os.path.join(self.temp_dir.name, "test_memory.json")
        self.manager = MemoryManager(file_path=self.test_file, weak_threshold=7)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_nonexistent_file(self):
        sessions = self.manager.load_memory()
        self.assertEqual(sessions, [])

    def test_load_corrupted_file(self):
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("invalid json content")
        sessions = self.manager.load_memory()
        self.assertEqual(sessions, [])

    def test_weak_topic_helper(self):
        self.assertTrue(is_weak_topic(5, threshold=7))
        self.assertTrue(is_weak_topic(6, threshold=7))
        self.assertFalse(is_weak_topic(7, threshold=7))
        self.assertFalse(is_weak_topic(9, threshold=7))

    def test_save_and_load_session(self):
        session_data = {
            "topic": "Photosynthesis",
            "level": "Beginner",
            "score": 5,
            "strengths": ["Understood light requirement"],
            "gaps": ["Missed Calvin cycle details"],
            "revision_concepts": ["Calvin cycle", "Chloroplasts", "ATP generation"],
            "summary": "Needs work on dark reactions.",
        }

        saved = self.manager.save_session(session_data)
        self.assertIn("id", saved)
        self.assertIn("timestamp", saved)
        self.assertTrue(saved["is_weak"])

        all_sessions = self.manager.load_memory()
        self.assertEqual(len(all_sessions), 1)
        self.assertEqual(all_sessions[0]["topic"], "Photosynthesis")

    def test_get_weak_topics(self):
        self.manager.save_session({"topic": "Weak Topic 1", "score": 4})
        self.manager.save_session({"topic": "Strong Topic", "score": 9})
        self.manager.save_session({"topic": "Weak Topic 2", "score": 6})

        weak_topics = self.manager.get_weak_topics()
        self.assertEqual(len(weak_topics), 2)
        weak_names = {t["topic"] for t in weak_topics}
        self.assertEqual(weak_names, {"Weak Topic 1", "Weak Topic 2"})

    def test_get_and_delete_session(self):
        saved = self.manager.save_session({"topic": "To Delete", "score": 8})
        session_id = saved["id"]

        retrieved = self.manager.get_session_by_id(session_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["topic"], "To Delete")

        deleted = self.manager.delete_session(session_id)
        self.assertTrue(deleted)
        self.assertIsNone(self.manager.get_session_by_id(session_id))

    def test_update_existing_session(self):
        saved = self.manager.save_session({"topic": "Initial Practice", "score": 4})
        session_id = saved["id"]
        self.assertTrue(saved["is_weak"])

        # User practices again and improves score
        updated_data = dict(saved)
        updated_data["score"] = 9

        updated = self.manager.save_session(updated_data)
        self.assertEqual(updated["id"], session_id)
        self.assertFalse(updated["is_weak"])

        all_sessions = self.manager.load_memory()
        self.assertEqual(len(all_sessions), 1)
        self.assertEqual(all_sessions[0]["score"], 9)


if __name__ == "__main__":
    unittest.main()
