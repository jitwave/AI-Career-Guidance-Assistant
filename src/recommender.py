"""Profile-Based Career Recommendation Engine.
Matches user skills, interests, and profile against careers using a hybrid
formulation of TF-IDF Cosine Similarity, Skill Overlap, and Skill Gap Analysis.
"""

import json
from typing import List, Dict, Any, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class CareerRecommender:
    """Intelligent recommender calculating career fit scores and skill gap roadmaps."""

    def __init__(self, careers_data: Dict[str, Any]):
        self.careers = careers_data
        self.all_skills = self._extract_all_skills()
        self.career_keys = list(self.careers.keys())
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), lowercase=True)
        self._build_career_corpus()

    def _extract_all_skills(self) -> List[str]:
        """Aggregate unique skill keywords from all careers."""
        skills = set()
        for info in self.careers.values():
            for s in info.get('core_skills', []):
                skills.add(s)
            for t in info.get('tools_and_technologies', []):
                skills.add(t)
        return sorted(list(skills))

    def _build_career_corpus(self):
        """Prepare vectorized textual representation of each career profile."""
        corpus = []
        for key in self.career_keys:
            career = self.careers[key]
            text_parts = [
                career.get('title', ''),
                career.get('category', ''),
                career.get('description', ''),
                " ".join(career.get('core_skills', [])),
                " ".join(career.get('tools_and_technologies', [])),
                " ".join(career.get('top_industries', []))
            ]
            corpus.append(" ".join(text_parts))

        if corpus:
            self.career_matrix = self.vectorizer.fit_transform(corpus)
        else:
            self.career_matrix = None

    def recommend(
        self,
        user_skills: Optional[List[str]] = None,
        user_interests: Optional[str] = "",
        top_n: int = 4
    ) -> List[Dict[str, Any]]:
        """Compute top career recommendations based on user skills and interests."""
        user_skills = [s.strip() for s in (user_skills or []) if s.strip()]
        user_interests = (user_interests or "").strip()

        # If user provided nothing, return top featured careers with baseline demand
        if not user_skills and not user_interests:
            return self._get_default_featured_careers(top_n)

        # 1. Cosine similarity over text profile (interests + skills)
        combined_profile_text = f"{user_interests} {' '.join(user_skills)}".strip()
        cosine_scores = [0.0] * len(self.career_keys)

        if self.career_matrix is not None and combined_profile_text:
            profile_vec = self.vectorizer.transform([combined_profile_text])
            cosine_scores = cosine_similarity(profile_vec, self.career_matrix)[0]

        # 2. Skill overlap calculation
        user_skills_lower = {s.lower() for s in user_skills}
        recommendations = []

        for idx, key in enumerate(self.career_keys):
            career = self.careers[key]
            career_core = career.get('core_skills', [])
            career_tools = career.get('tools_and_technologies', [])
            all_career_skills = career_core + career_tools

            # Skill matching
            matched_core = [s for s in career_core if s.lower() in user_skills_lower]
            matched_tools = [s for s in career_tools if s.lower() in user_skills_lower]
            all_matched = matched_core + matched_tools

            missing_core = [s for s in career_core if s.lower() not in user_skills_lower]
            missing_tools = [s for s in career_tools if s.lower() not in user_skills_lower]

            # Skill coverage computation
            core_coverage = len(matched_core) / max(len(career_core), 1)
            tool_coverage = len(matched_tools) / max(len(career_tools), 1)
            combined_skill_score = (0.75 * core_coverage) + (0.25 * tool_coverage)

            cos_score = float(cosine_scores[idx])

            # Composite weighting
            if user_skills and user_interests:
                base_score = (0.60 * combined_skill_score) + (0.40 * cos_score)
            elif user_skills:
                base_score = (0.80 * combined_skill_score) + (0.20 * cos_score)
            else:
                base_score = cos_score

            # Realistic candidate fit calibration
            scaled_score = base_score * 1.3
            if len(matched_core) >= 3:
                scaled_score = max(scaled_score, 0.75 + (len(matched_core) * 0.04))
            elif len(matched_core) >= 2:
                scaled_score = max(scaled_score, 0.65 + (len(matched_core) * 0.04))
            elif len(matched_core) == 1 or len(matched_tools) >= 1:
                scaled_score = max(scaled_score, 0.45)

            match_percentage = min(98, max(12, round(scaled_score * 100)))

            recommendations.append({
                "career_key": key,
                "title": career.get('title', key),
                "category": career.get('category', ''),
                "description": career.get('description', ''),
                "match_percentage": match_percentage,
                "demand_level": career.get('demand_level', 'High'),
                "salary_range": career.get('salary_range', {}),
                "growth_rate": career.get('growth_rate', ''),
                "matched_skills": all_matched,
                "missing_skills": missing_core,
                "recommended_tools": missing_tools[:5],
                "top_companies": career.get('top_hiring_companies', [])[:4],
                "learning_roadmap": career.get('learning_roadmap', [])
            })

        # Rank by match percentage descending
        recommendations.sort(key=lambda x: x['match_percentage'], reverse=True)
        return recommendations[:top_n]

    def _get_default_featured_careers(self, top_n: int) -> List[Dict[str, Any]]:
        """Return popular baseline careers when no profile is provided."""
        featured_keys = [
            "AI/ML Engineer",
            "Data Scientist",
            "Full Stack Developer",
            "DevOps & Cloud Engineer"
        ]
        results = []
        for key in featured_keys[:top_n]:
            if key in self.careers:
                c = self.careers[key]
                results.append({
                    "career_key": key,
                    "title": c.get('title', key),
                    "category": c.get('category', ''),
                    "description": c.get('description', ''),
                    "match_percentage": 85,
                    "demand_level": c.get('demand_level', 'High'),
                    "salary_range": c.get('salary_range', {}),
                    "growth_rate": c.get('growth_rate', ''),
                    "matched_skills": [],
                    "missing_skills": c.get('core_skills', []),
                    "recommended_tools": c.get('tools_and_technologies', [])[:5],
                    "top_companies": c.get('top_hiring_companies', [])[:4],
                    "learning_roadmap": c.get('learning_roadmap', [])
                })
        return results

    def get_skill_gap(self, career_key: str, user_skills: List[str]) -> Dict[str, Any]:
        """Detailed skill gap analysis against a targeted career path."""
        if career_key not in self.careers:
            return {"error": f"Career '{career_key}' not found."}

        career = self.careers[career_key]
        user_skills_lower = {s.lower() for s in user_skills}

        core = career.get('core_skills', [])
        tools = career.get('tools_and_technologies', [])

        matched = [s for s in core if s.lower() in user_skills_lower]
        missing = [s for s in core if s.lower() not in user_skills_lower]
        matched_tools = [t for t in tools if t.lower() in user_skills_lower]
        missing_tools = [t for t in tools if t.lower() not in user_skills_lower]

        readiness = round((len(matched) / max(len(core), 1)) * 100)

        return {
            "career": career_key,
            "readiness_percentage": readiness,
            "matched_core_skills": matched,
            "missing_core_skills": missing,
            "matched_tools": matched_tools,
            "missing_tools": missing_tools,
            "total_core_skills": len(core),
            "roadmap": career.get('learning_roadmap', [])
        }
