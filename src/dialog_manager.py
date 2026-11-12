"""Dialog and Session Manager for AI Career Guidance Assistant.
Manages multi-turn conversation states, slot filling, contextual profile tracking,
and personalized dialogue generation.
"""

from typing import Dict, Any, List, Optional, Tuple


class DialogSession:
    """Represents an individual user session with history and slot memory."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state = "IDLE"  # IDLE, AWAITING_SKILLS, AWAITING_INTERESTS
        self.user_profile: Dict[str, Any] = {
            "name": "Student",
            "skills": [],
            "interests": "",
            "target_career": None,
            "education": None
        }
        self.history: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str):
        """Append to conversation history."""
        self.history.append({"role": role, "content": content})

    def reset_profile(self):
        """Reset profile memory and state."""
        self.state = "IDLE"
        self.user_profile = {
            "name": "Student",
            "skills": [],
            "interests": "",
            "target_career": None,
            "education": None
        }


class DialogManager:
    """Coordinates conversational turn flow and state machine transitions."""

    def __init__(self):
        self.sessions: Dict[str, DialogSession] = {}

    def get_session(self, session_id: str = "default") -> DialogSession:
        """Retrieve or initialize user session."""
        if session_id not in self.sessions:
            self.sessions[session_id] = DialogSession(session_id)
        return self.sessions[session_id]

    def update_profile_skills(self, session_id: str, new_skills: List[str]):
        """Append newly detected skills to user profile."""
        session = self.get_session(session_id)
        existing = set(session.user_profile["skills"])
        for s in new_skills:
            existing.add(s)
        session.user_profile["skills"] = sorted(list(existing))

    def update_profile_interests(self, session_id: str, interests_text: str):
        """Update user interests."""
        session = self.get_session(session_id)
        current = session.user_profile.get("interests", "")
        if current:
            session.user_profile["interests"] = f"{current} {interests_text}".strip()
        else:
            session.user_profile["interests"] = interests_text.strip()
