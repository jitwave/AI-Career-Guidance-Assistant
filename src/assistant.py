"""Unified AI Career Guidance Assistant Engine.
Coordinates Knowledge Base, NLP Intent Engine, Dialog Manager,
and Recommendation Systems to deliver rich, contextual responses.
"""

import os
import json
import random
from typing import Dict, Any, List, Optional, Tuple

from src.nlp_engine import NLPEngine
from src.recommender import CareerRecommender
from src.dialog_manager import DialogManager


class CareerGuidanceAssistant:
    """The central conversational assistant for career guidance."""

    def __init__(
        self,
        careers_path: Optional[str] = None,
        intents_path: Optional[str] = None,
        trends_path: Optional[str] = None
    ):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.careers_path = careers_path or os.path.join(base_dir, "data", "careers.json")
        self.intents_path = intents_path or os.path.join(base_dir, "data", "intents.json")
        self.trends_path = trends_path or os.path.join(base_dir, "data", "trends.json")

        self.careers_data = self._load_json(self.careers_path)
        self.trends_data = self._load_json(self.trends_path)

        # Initialize sub-engines
        self.nlp = NLPEngine(intents_path=self.intents_path)
        self.recommender = CareerRecommender(careers_data=self.careers_data)
        self.dialog_manager = DialogManager()

    def _load_json(self, path: str) -> Dict[str, Any]:
        """Safely load JSON files."""
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def get_all_careers(self) -> Dict[str, Any]:
        """Return raw career database."""
        return self.careers_data

    def get_market_trends(self) -> Dict[str, Any]:
        """Return industry trends data."""
        return self.trends_data

    def process_query(self, user_input: str, session_id: str = "default") -> Dict[str, Any]:
        """Main conversational processing pipeline."""
        text = (user_input or "").strip()
        session = self.dialog_manager.get_session(session_id)
        session.add_message("user", text)

        if not text:
            msg = "Please type a message or ask a question about tech careers, salaries, skills, or interview tips!"
            session.add_message("assistant", msg)
            return {"response": msg, "intent": "empty", "confidence": 1.0, "data": None}

        # Handle reset commands
        if text.lower() in {"reset", "clear", "restart", "clear profile", "reset profile"}:
            session.reset_profile()
            msg = "🔄 Your career profile and conversation state have been reset. What would you like to explore now?"
            session.add_message("assistant", msg)
            return {"response": msg, "intent": "reset", "confidence": 1.0, "data": None}

        # Check multi-turn slot filling states
        if session.state == "AWAITING_SKILLS":
            return self._handle_awaiting_skills(text, session)

        if session.state == "AWAITING_INTERESTS":
            return self._handle_awaiting_interests(text, session)

        # Extract entities from input
        detected_career = self.nlp.extract_career_entity(text, self.careers_data)
        detected_skills = self.nlp.extract_skills(text, self.recommender.all_skills)

        if detected_skills:
            self.dialog_manager.update_profile_skills(session_id, detected_skills)

        # Classify Intent
        intent, confidence = self.nlp.classify_intent(text)

        # Dispatch response generation
        result = self._dispatch_intent(
            intent=intent,
            confidence=confidence,
            text=text,
            detected_career=detected_career,
            detected_skills=detected_skills,
            session=session
        )

        session.add_message("assistant", result["response"])
        return result

    def _handle_awaiting_skills(self, text: str, session) -> Dict[str, Any]:
        """Handle user input when chatbot is expecting skills."""
        detected_skills = self.nlp.extract_skills(text, self.recommender.all_skills)
        # Also split by commas if user typed arbitrary skills
        raw_items = [s.strip() for s in text.replace('and', ',').split(',') if s.strip()]
        combined_skills = list(set(detected_skills + raw_items))

        if combined_skills:
            self.dialog_manager.update_profile_skills(session.session_id, combined_skills)
            session.state = "AWAITING_INTERESTS"
            skills_str = ", ".join(session.user_profile["skills"])
            response = (
                f"🎯 **Skills Recorded**: {skills_str}\n\n"
                f"Next, what domains or project types interest you most? "
                f"(For example: *Machine Learning models, building web apps, cloud infrastructure, ethical hacking, or data analytics*)."
            )
            return {"response": response, "intent": "slot_fill_skills", "confidence": 1.0, "data": None}
        else:
            response = (
                "I couldn't quite extract specific skills from that. "
                "Could you list a few technical skills or languages you know separated by commas? (e.g. *Python, SQL, HTML, Docker*)"
            )
            return {"response": response, "intent": "slot_fill_skills_retry", "confidence": 0.5, "data": None}

    def _handle_awaiting_interests(self, text: str, session) -> Dict[str, Any]:
        """Handle user input when chatbot is expecting interests."""
        self.dialog_manager.update_profile_interests(session.session_id, text)
        session.state = "IDLE"

        # Compute recommendations
        skills = session.user_profile["skills"]
        interests = session.user_profile["interests"]
        recs = self.recommender.recommend(user_skills=skills, user_interests=interests, top_n=3)

        formatted = self._format_recommendations_response(recs, skills, interests)
        return {
            "response": formatted,
            "intent": "recommendation_result",
            "confidence": 1.0,
            "data": recs
        }

    def _dispatch_intent(
        self,
        intent: str,
        confidence: float,
        text: str,
        detected_career: Optional[str],
        detected_skills: List[str],
        session
    ) -> Dict[str, Any]:
        """Dispatch intent to appropriate response generator."""
        if intent == "greeting":
            responses = self.nlp.tag_responses.get("greeting", [
                "Hello! Welcome to the AI Career Guidance Assistant. What career path would you like to explore today?"
            ])
            resp = random.choice(responses)
            resp += (
                "\n\n💡 **Quick options to try**:\n"
                "• *'Explore all careers'*\n"
                "• *'Recommend a career for Python, SQL, and Machine Learning'*\n"
                "• *'What is the salary of an AI/ML Engineer?'*\n"
                "• *'Interview questions for Data Scientist'*\n"
                "• *'What are the 2026 tech trends?'*"
            )
            return {"response": resp, "intent": intent, "confidence": confidence, "data": None}

        elif intent == "goodbye":
            responses = self.nlp.tag_responses.get("goodbye", ["Goodbye! Best of luck on your career journey!"])
            return {"response": random.choice(responses), "intent": intent, "confidence": confidence, "data": None}

        elif intent == "help":
            responses = self.nlp.tag_responses.get("help", ["Ask about careers, salaries, skills, or interview tips!"])
            return {"response": responses[0], "intent": intent, "confidence": confidence, "data": None}

        elif intent == "career_paths":
            if detected_career:
                resp = self._format_career_deep_dive(detected_career)
                return {"response": resp, "intent": "career_deep_dive", "confidence": confidence, "data": self.careers_data[detected_career]}
            else:
                resp = self._format_all_careers_summary()
                return {"response": resp, "intent": intent, "confidence": confidence, "data": list(self.careers_data.keys())}

        elif intent == "skill_analysis":
            if detected_career:
                resp = self._format_career_skills(detected_career, session.user_profile["skills"])
                return {"response": resp, "intent": "skill_analysis", "confidence": confidence, "data": self.careers_data[detected_career]}
            else:
                resp = (
                    "Which career path would you like to see required skills for?\n"
                    "For example, ask: *'Skills needed for AI/ML Engineer'* or *'Prerequisites for DevOps & Cloud Engineer'*."
                )
                return {"response": resp, "intent": intent, "confidence": confidence, "data": None}

        elif intent in {"recommendation", "set_profile"}:
            current_skills = session.user_profile["skills"]
            # If user provided skills in this message or profile already has skills
            if len(current_skills) >= 1 or len(detected_skills) >= 1:
                all_skills = list(set(current_skills + detected_skills))
                recs = self.recommender.recommend(user_skills=all_skills, user_interests=text, top_n=3)
                resp = self._format_recommendations_response(recs, all_skills, text)
                return {"response": resp, "intent": "recommendation", "confidence": confidence, "data": recs}
            else:
                session.state = "AWAITING_SKILLS"
                resp = (
                    "I'd love to generate a personalized career recommendation for you! 🎯\n\n"
                    "To start, **what programming languages, technical skills, or tools do you currently know or enjoy?** "
                    "(e.g. *Python, SQL, React, Linux, Statistics, C++*)"
                )
                return {"response": resp, "intent": "prompt_for_skills", "confidence": confidence, "data": None}

        elif intent == "salary_inquiry":
            if detected_career:
                resp = self._format_career_salary(detected_career)
                return {"response": resp, "intent": "salary_inquiry", "confidence": confidence, "data": self.careers_data[detected_career]["salary_range"]}
            else:
                resp = self._format_salary_overview()
                return {"response": resp, "intent": intent, "confidence": confidence, "data": None}

        elif intent == "industry_trends":
            resp = self._format_trends_response()
            return {"response": resp, "intent": intent, "confidence": confidence, "data": self.trends_data}

        elif intent == "interview_prep":
            if detected_career:
                resp = self._format_interview_prep(detected_career)
                return {"response": resp, "intent": "interview_prep", "confidence": confidence, "data": self.careers_data[detected_career]}
            else:
                resp = (
                    "I can provide targeted interview tips and technical questions for any tech role! 💼\n"
                    "Which role are you preparing for? (e.g. *'Interview tips for Data Scientist'* or *'Interview prep for Cyber Security'*)"
                )
                return {"response": resp, "intent": intent, "confidence": confidence, "data": None}

        elif intent == "company_research":
            if detected_career:
                resp = self._format_top_companies(detected_career)
                return {"response": resp, "intent": "company_research", "confidence": confidence, "data": self.careers_data[detected_career]["top_hiring_companies"]}
            else:
                resp = (
                    "Top global companies hiring across technology sectors include Google, Microsoft, Amazon, Meta, NVIDIA, and high-growth innovators.\n\n"
                    "Name a specific career role (e.g., *'Top hiring companies for Full Stack Developer'*) to see targeted recruiters!"
                )
                return {"response": resp, "intent": intent, "confidence": confidence, "data": None}

        elif intent == "learning_roadmap":
            if detected_career:
                resp = self._format_learning_roadmap(detected_career)
                return {"response": resp, "intent": "learning_roadmap", "confidence": confidence, "data": self.careers_data[detected_career]["learning_roadmap"]}
            else:
                resp = (
                    "Which career roadmap would you like to see?\n"
                    "For example: *'Learning roadmap for AI/ML Engineer'* or *'Roadmap for Cloud Solutions Architect'*."
                )
                return {"response": resp, "intent": intent, "confidence": confidence, "data": None}

        elif intent == "thank_you":
            responses = self.nlp.tag_responses.get("thank_you", ["You're welcome! Let me know if you need anything else!"])
            return {"response": random.choice(responses), "intent": intent, "confidence": confidence, "data": None}

        # Fallback handling
        return self._handle_fallback(text, detected_career, detected_skills)

    def _handle_fallback(self, text: str, detected_career: Optional[str], detected_skills: List[str]) -> Dict[str, Any]:
        """Handle unrecognized queries gracefully with smart defaults."""
        if detected_career:
            resp = self._format_career_deep_dive(detected_career)
            return {"response": resp, "intent": "career_deep_dive", "confidence": 0.8, "data": self.careers_data[detected_career]}

        if detected_skills:
            recs = self.recommender.recommend(user_skills=detected_skills, top_n=3)
            resp = self._format_recommendations_response(recs, detected_skills, "")
            return {"response": resp, "intent": "auto_recommend", "confidence": 0.8, "data": recs}

        fallback_msg = (
            "I'm not completely certain I understood your query. 🤔\n\n"
            "Here are some helpful things you can ask me:\n"
            "• **Career Details**: *'Tell me about Data Scientist'* or *'What does a DevOps Engineer do?'*\n"
            "• **Personalized Recommendations**: *'Recommend careers for Python, SQL, Docker'*\n"
            "• **Salary Comparison**: *'What is the salary of a Cyber Security Engineer?'*\n"
            "• **Skill Prerequisites**: *'Skills required for Full Stack Developer'*\n"
            "• **Roadmaps & Prep**: *'Learning roadmap for Cloud Architect'* or *'Interview tips for AI Engineer'*\n"
            "• **Market Trends**: *'What are the latest tech trends in 2026?'*"
        )
        return {"response": fallback_msg, "intent": "fallback", "confidence": 0.0, "data": None}

    # Formatting Helper Functions
    def _format_career_deep_dive(self, career_key: str) -> str:
        """Format an in-depth career profile."""
        c = self.careers_data[career_key]
        sal = c.get('salary_range', {})
        progression = " ➔ ".join(c.get('career_progression', []))
        skills_str = ", ".join(c.get('core_skills', []))
        tools_str = ", ".join(c.get('tools_and_technologies', []))
        companies_str = ", ".join(c.get('top_hiring_companies', []))

        return (
            f"💼 **{c['title']}** ({c['category']})\n"
            f"{'='*60}\n"
            f"📌 **Role Overview**:\n{c['description']}\n\n"
            f"⚡ **Demand Level**: {c.get('demand_level', 'High')} | 📈 **Growth Rate**: {c.get('growth_rate', '20%+ Yearly')}\n\n"
            f"🔧 **Core Skills**:\n{skills_str}\n\n"
            f"🛠️ **Tools & Frameworks**:\n{tools_str}\n\n"
            f"💰 **Salary Compensation**:\n"
            f"  • Entry Level: {sal.get('entry', 'N/A')}\n"
            f"  • Mid Level:   {sal.get('mid', 'N/A')}\n"
            f"  • Senior Level: {sal.get('senior', 'N/A')}\n\n"
            f"🏢 **Top Hiring Companies**:\n{companies_str}\n\n"
            f"🚀 **Career Progression**:\n{progression}\n\n"
            f"💡 *Tip: Ask for 'Interview tips for {c['title']}' or 'Learning roadmap for {c['title']}'!*"
        )

    def _format_all_careers_summary(self) -> str:
        """Format a categorized catalog of all careers."""
        categories: Dict[str, List[str]] = {}
        for key, c in self.careers_data.items():
            cat = c.get('category', 'Other')
            categories.setdefault(cat, []).append(key)

        output = "🎓 **Available Career Exploration Tracks**:\n"
        output += "We support 13 high-growth industry career tracks:\n\n"
        for cat, titles in categories.items():
            output += f"📁 **{cat}**:\n"
            for t in titles:
                sal = self.careers_data[t].get('salary_range', {}).get('entry', '')
                output += f"  • 💼 **{t}** (Entry: {sal})\n"
            output += "\n"

        output += "💬 *Ask about any role to get full details (e.g. 'Tell me about AI/ML Engineer')!*"
        return output

    def _format_career_skills(self, career_key: str, user_skills: List[str]) -> str:
        """Format required skills and personal skill gap comparison."""
        c = self.careers_data[career_key]
        core = c.get('core_skills', [])
        tools = c.get('tools_and_technologies', [])
        user_skills_lower = {s.lower() for s in user_skills}

        matched = [s for s in core if s.lower() in user_skills_lower]
        missing = [s for s in core if s.lower() not in user_skills_lower]

        res = f"🔧 **Skill Requirements for {c['title']}**:\n\n"
        res += f"📌 **Core Competencies**: {', '.join(core)}\n"
        res += f"🛠️ **Key Tools & Technologies**: {', '.join(tools)}\n\n"

        if user_skills:
            readiness = round((len(matched) / max(len(core), 1)) * 100)
            res += f"📊 **Your Match & Skill Gap Analysis** (Readiness: {readiness}%):\n"
            if matched:
                res += f"  ✅ **Skills You Have**: {', '.join(matched)}\n"
            if missing:
                res += f"  ⏳ **Skills to Learn**: {', '.join(missing)}\n"
            res += f"\n💡 *Focus on mastering '{missing[0] if missing else 'Advanced System Architecture'}' next!*"
        else:
            res += "💡 *Tell me your skills (e.g. 'I know Python and SQL') to see your personalized skill gap!*"

        return res

    def _format_recommendations_response(
        self,
        recs: List[Dict[str, Any]],
        user_skills: List[str],
        user_interests: str
    ) -> str:
        """Format ranked career recommendations."""
        res = "🎯 **Personalized Career Recommendations**\n"
        res += f"{'='*60}\n"
        if user_skills:
            res += f"👤 **Your Profile Skills**: {', '.join(user_skills)}\n"
        if user_interests:
            res += f"💡 **Interests/Keywords**: {user_interests}\n"
        res += "\nBased on our hybrid similarity and skill-overlap matching, here are your best career fits:\n\n"

        for idx, r in enumerate(recs, 1):
            res += f"### {idx}. 💼 {r['title']} — **{r['match_percentage']}% Fit**\n"
            res += f"   📌 *{r['description']}*\n"
            res += f"   💰 **Salary**: {r['salary_range'].get('mid', 'N/A')} (Mid-Level)\n"
            res += f"   📈 **Demand**: {r['demand_level']} ({r.get('growth_rate', '')})\n"
            if r['matched_skills']:
                res += f"   ✅ **Your Matching Skills**: {', '.join(r['matched_skills'])}\n"
            if r['missing_skills']:
                res += f"   ⏳ **Skills to Learn**: {', '.join(r['missing_skills'][:4])}\n"
            if r['top_companies']:
                res += f"   🏢 **Top Recruiters**: {', '.join(r['top_companies'])}\n"
            res += "\n"

        res += "💡 *Type 'Interview tips for [Role]' or 'Roadmap for [Role]' to prepare for any of these paths!*"
        return res

    def _format_career_salary(self, career_key: str) -> str:
        """Format salary breakdown for a specific career."""
        c = self.careers_data[career_key]
        sal = c.get('salary_range', {})
        return (
            f"💰 **Salary Insights: {c['title']}**\n"
            f"{'='*60}\n"
            f"• 🟢 **Entry Level (0-2 years)**:  {sal.get('entry', 'N/A')}\n"
            f"• 🟡 **Mid Level (3-6 years)**:    {sal.get('mid', 'N/A')}\n"
            f"• 🔴 **Senior Level (7+ years)**:  {sal.get('senior', 'N/A')}\n\n"
            f"📊 **Market Demand**: {c.get('demand_level', 'High')} | **Growth**: {c.get('growth_rate', '20% YoY')}\n"
            f"🏢 **Top Paying Recruiters**: {', '.join(c.get('top_hiring_companies', [])[:5])}\n\n"
            f"💡 *Note: Compensation packages vary by location, tier-1 tech hubs, and specialized domain expertise.*"
        )

    def _format_salary_overview(self) -> str:
        """Format comparative salary overview across roles."""
        summary = self.trends_data.get('salary_insights_summary', {})
        highest = summary.get('highest_starting_packages', [])

        res = "💰 **Tech Career Compensation Overview (2026)**\n"
        res += f"{'='*60}\n"
        res += "🏆 **Top Entry-Level Starting Compensation**:\n"
        for item in highest:
            res += f"  • {item}\n"
        res += "\n🚀 **Fastest Salary Growth Velocity Roles**:\n"
        for item in summary.get('highest_growth_velocity', []):
            res += f"  • {item}\n"
        res += "\n💼 *Ask for any specific career salary (e.g. 'Salary of DevOps Engineer') to see entry, mid, and senior brackets!*"
        return res

    def _format_trends_response(self) -> str:
        """Format 2026 industry trends and market forecast."""
        trends = self.trends_data.get('top_trends', [])
        preds = self.trends_data.get('market_predictions', [])

        res = "📊 **Industry & Job Market Trends (2025 - 2027)**\n"
        res += f"{'='*60}\n"
        res += f"📌 *{self.trends_data.get('overview', '')}*\n\n"
        res += "🚀 **Top High-Growth Technology Domains**:\n"

        for t in trends[:5]:
            res += f"**{t['rank']}. {t['domain']}** (📈 Growth: {t['growth_rate']} | Demand: {t['demand_index']})\n"
            res += f"   • *Key Driver*: {t['key_drivers']}\n"
            res += f"   • *Hot Skills*: {', '.join(t['high_demand_skills'][:5])}\n\n"

        res += "🔮 **Key Market Predictions**:\n"
        for p in preds[:3]:
            res += f"  ⚡ {p}\n"

        return res

    def _format_interview_prep(self, career_key: str) -> str:
        """Format interview tips and questions for a career."""
        c = self.careers_data[career_key]
        tips = c.get('interview_tips', [])
        questions = c.get('interview_questions', [])

        res = f"📝 **Interview Preparation Guide: {c['title']}**\n"
        res += f"{'='*60}\n"
        res += "🎯 **Strategic Preparation Tips**:\n"
        for idx, tip in enumerate(tips, 1):
            res += f"  {idx}. {tip}\n"

        res += "\n❓ **Common Technical & Architecture Interview Questions**:\n"
        for idx, q in enumerate(questions, 1):
            res += f"  Q{idx}: {q}\n"

        res += f"\n💡 *Practice answering these with the STAR method (Situation, Task, Action, Result) for behavioral questions, and clean whiteboard architecture for system design!*"
        return res

    def _format_top_companies(self, career_key: str) -> str:
        """Format top companies hiring for a role."""
        c = self.careers_data[career_key]
        comps = c.get('top_hiring_companies', [])
        industries = c.get('top_industries', [])

        res = f"🏢 **Top Recruiters for {c['title']}**\n"
        res += f"{'='*60}\n"
        res += f"🌟 **Leading Employers**: {', '.join(comps)}\n"
        res += f"🏭 **Key Industry Sectors**: {', '.join(industries)}\n\n"
        res += "💡 *Tip: Check out company careers portals, alumni networks on LinkedIn, and open-source contributions to stand out to these recruiters!*"
        return res

    def _format_learning_roadmap(self, career_key: str) -> str:
        """Format step-by-step phased roadmap for a career."""
        c = self.careers_data[career_key]
        roadmap = c.get('learning_roadmap', [])

        res = f"🗺️ **4-Phase Learning Roadmap: {c['title']}**\n"
        res += f"{'='*60}\n"
        for step in roadmap:
            res += f"• {step}\n\n"
        res += f"💡 *Follow each phase sequentially and build at least one end-to-end project per phase to showcase on GitHub!*"
        return res
