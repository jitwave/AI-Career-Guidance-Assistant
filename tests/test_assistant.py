"""Unit tests for CareerGuidanceAssistant (end-to-end dialogue and flow).
"""

import unittest
from src.assistant import CareerGuidanceAssistant


class TestCareerGuidanceAssistant(unittest.TestCase):
    def setUp(self):
        self.assistant = CareerGuidanceAssistant()

    def test_greeting_flow(self):
        res = self.assistant.process_query("Hello!", session_id="test_sess_1")
        self.assertEqual(res["intent"], "greeting")
        self.assertIn("Quick options", res["response"])

    def test_career_exploration_flow(self):
        # All careers summary
        res1 = self.assistant.process_query("List all careers", session_id="test_sess_2")
        self.assertEqual(res1["intent"], "career_paths")
        self.assertIn("AI/ML Engineer", res1["response"])

        # Specific career deep dive
        res2 = self.assistant.process_query("Tell me about DevOps & Cloud Engineer", session_id="test_sess_2")
        self.assertEqual(res2["intent"], "career_deep_dive")
        self.assertIn("DevOps & Cloud Engineer", res2["response"])
        self.assertIn("Salary Compensation", res2["response"])

    def test_salary_flow(self):
        res = self.assistant.process_query("What is the salary of a Cyber Security Engineer?", session_id="test_sess_3")
        self.assertEqual(res["intent"], "salary_inquiry")
        self.assertIn("Salary Insights", res["response"])
        self.assertIn("Entry Level", res["response"])

    def test_interview_prep_flow(self):
        res = self.assistant.process_query("Interview tips for Data Scientist", session_id="test_sess_4")
        self.assertEqual(res["intent"], "interview_prep")
        self.assertIn("Interview Preparation Guide", res["response"])
        self.assertIn("Technical & Architecture", res["response"])

    def test_multi_turn_slot_filling(self):
        sess_id = "slot_fill_user"
        # Turn 1: trigger recommendation without skills
        r1 = self.assistant.process_query("Recommend a career for me", session_id=sess_id)
        self.assertEqual(r1["intent"], "prompt_for_skills")

        # Turn 2: provide skills
        r2 = self.assistant.process_query("Python, SQL, Machine Learning", session_id=sess_id)
        self.assertEqual(r2["intent"], "slot_fill_skills")

        # Turn 3: provide interests
        r3 = self.assistant.process_query("I love building predictive AI models", session_id=sess_id)
        self.assertEqual(r3["intent"], "recommendation_result")
        self.assertIn("Personalized Career Recommendations", r3["response"])

    def test_reset_flow(self):
        sess_id = "reset_user"
        self.assistant.process_query("I know Python and Docker", session_id=sess_id)
        session = self.assistant.dialog_manager.get_session(sess_id)
        self.assertGreater(len(session.user_profile["skills"]), 0)

        # Reset
        res = self.assistant.process_query("reset profile", session_id=sess_id)
        self.assertEqual(res["intent"], "reset")
        self.assertEqual(len(session.user_profile["skills"]), 0)


if __name__ == "__main__":
    unittest.main()
