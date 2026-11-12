"""Unit tests for CareerRecommender (skill matching, scoring, skill gap analysis).
"""

import os
import json
import unittest
from src.recommender import CareerRecommender


class TestCareerRecommender(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        careers_path = os.path.join(base_dir, "data", "careers.json")
        with open(careers_path, "r", encoding="utf-8") as f:
            careers_data = json.load(f)
        cls.recommender = CareerRecommender(careers_data=careers_data)

    def test_recommender_initialization(self):
        self.assertGreater(len(self.recommender.career_keys), 10)
        self.assertIn("Python", self.recommender.all_skills)

    def test_recommendation_ranking(self):
        # AI/ML skills
        user_skills = ["Python", "Machine Learning", "Deep Learning", "TensorFlow"]
        user_interests = "building neural networks and predictive models"
        recs = self.recommender.recommend(user_skills=user_skills, user_interests=user_interests, top_n=3)

        self.assertEqual(len(recs), 3)
        top_rec = recs[0]
        # Should rank AI/ML or Data Scientist highest
        self.assertIn(top_rec["career_key"], ["AI/ML Engineer", "Data Scientist"])
        self.assertGreater(top_rec["match_percentage"], 60)
        self.assertIn("Python", top_rec["matched_skills"])

    def test_web_dev_recommendation(self):
        # Full stack skills
        user_skills = ["JavaScript", "React", "Node.js", "HTML5/CSS3"]
        recs = self.recommender.recommend(user_skills=user_skills, top_n=2)
        top_titles = [r["title"] for r in recs]
        self.assertIn("Full Stack Developer", top_titles)

    def test_skill_gap_analysis(self):
        gap = self.recommender.get_skill_gap("AI/ML Engineer", ["Python", "Statistics"])
        self.assertEqual(gap["career"], "AI/ML Engineer")
        self.assertIn("Python", gap["matched_core_skills"])
        self.assertIn("Deep Learning", gap["missing_core_skills"])
        self.assertGreater(gap["readiness_percentage"], 0)


if __name__ == "__main__":
    unittest.main()
