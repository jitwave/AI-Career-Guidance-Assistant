"""Unit tests for NLPEngine (tokenization, lemmatization, intent classification, entity extraction).
"""

import os
import unittest
from src.nlp_engine import NLPEngine


class TestNLPEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        intents_path = os.path.join(base_dir, "data", "intents.json")
        cls.nlp = NLPEngine(intents_path=intents_path)
        cls.sample_careers = {
            "AI/ML Engineer": {},
            "Data Scientist": {},
            "DevOps & Cloud Engineer": {},
            "Full Stack Developer": {},
            "Cyber Security Engineer": {}
        }
        cls.sample_skills = ["Python", "SQL", "Machine Learning", "Docker", "React", "Linux"]

    def test_tokenization_and_preprocessing(self):
        text = "Hello! I am learning Python & Machine Learning."
        cleaned = self.nlp.preprocess_text(text)
        self.assertIn("python", cleaned)
        self.assertIn("machine", cleaned)
        # Stopword 'i', 'am' should be removed
        tokens = cleaned.split()
        self.assertNotIn("i", tokens)
        self.assertNotIn("am", tokens)

    def test_greeting_intent(self):
        intent, conf = self.nlp.classify_intent("hi there")
        self.assertEqual(intent, "greeting")
        self.assertGreater(conf, 0.3)

    def test_salary_intent(self):
        intent, conf = self.nlp.classify_intent("what is the salary of a devops engineer?")
        self.assertEqual(intent, "salary_inquiry")
        self.assertGreater(conf, 0.3)

    def test_trends_intent(self):
        intent, conf = self.nlp.classify_intent("what are the latest tech trends in 2026?")
        self.assertEqual(intent, "industry_trends")
        self.assertGreater(conf, 0.3)

    def test_interview_prep_intent(self):
        intent, conf = self.nlp.classify_intent("give me interview questions for data science")
        self.assertEqual(intent, "interview_prep")
        self.assertGreater(conf, 0.3)

    def test_career_entity_extraction(self):
        # Exact and alias matches
        career1 = self.nlp.extract_career_entity("Tell me about Data Scientist", self.sample_careers)
        self.assertEqual(career1, "Data Scientist")

        career2 = self.nlp.extract_career_entity("What does an ai engineer do?", self.sample_careers)
        self.assertEqual(career2, "AI/ML Engineer")

        career3 = self.nlp.extract_career_entity("How to crack devops?", self.sample_careers)
        self.assertEqual(career3, "DevOps & Cloud Engineer")

    def test_skills_extraction(self):
        text = "I have experience with Python, SQL, and Docker containerization."
        found = self.nlp.extract_skills(text, self.sample_skills)
        self.assertIn("Python", found)
        self.assertIn("SQL", found)
        self.assertIn("Docker", found)
        self.assertNotIn("React", found)


if __name__ == "__main__":
    unittest.main()
