"""Flask Web Application for AI Career Guidance Assistant.
Internship Task ID: AI-SS-005
Domain: Student Support & Internship Management NLP
Student: Sarbajit Das (Code: DAS013423)
Company: Data Alcott Systems
"""

import os
import sys
from flask import Flask, render_template, request, jsonify

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.assistant import CareerGuidanceAssistant

app = Flask(__name__)

# Initialize single assistant instance
assistant = CareerGuidanceAssistant()


@app.route("/")
def index():
    """Render main dashboard view."""
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Handle conversational user query."""
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()
    session_id = data.get("session_id", "web_default_session")

    if not user_message:
        return jsonify({
            "status": "error",
            "response": "Please enter a message to begin.",
            "intent": "empty"
        }), 400

    result = assistant.process_query(user_message, session_id=session_id)
    return jsonify({
        "status": "success",
        "response": result["response"],
        "intent": result["intent"],
        "confidence": result.get("confidence", 0.0),
        "data": result.get("data")
    })


@app.route("/api/careers", methods=["GET"])
def api_careers():
    """Return all career profiles."""
    careers = assistant.get_all_careers()
    return jsonify({
        "status": "success",
        "total": len(careers),
        "careers": careers
    })


@app.route("/api/career/<path:career_key>", methods=["GET"])
def api_single_career(career_key):
    """Return specific career details."""
    careers = assistant.get_all_careers()
    if career_key in careers:
        return jsonify({"status": "success", "career": careers[career_key]})
    return jsonify({"status": "error", "message": f"Career '{career_key}' not found"}), 404


@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    """Direct profile-based recommendation endpoint."""
    data = request.get_json() or {}
    skills = data.get("skills", [])
    interests = data.get("interests", "")
    top_n = int(data.get("top_n", 4))

    recommendations = assistant.recommender.recommend(
        user_skills=skills,
        user_interests=interests,
        top_n=top_n
    )
    return jsonify({
        "status": "success",
        "recommendations": recommendations
    })


@app.route("/api/trends", methods=["GET"])
def api_trends():
    """Return tech trends and market predictions."""
    trends = assistant.get_market_trends()
    return jsonify({
        "status": "success",
        "trends": trends
    })


@app.route("/api/reset", methods=["POST"])
def api_reset():
    """Reset dialog session profile."""
    data = request.get_json() or {}
    session_id = data.get("session_id", "web_default_session")
    session = assistant.dialog_manager.get_session(session_id)
    session.reset_profile()
    return jsonify({
        "status": "success",
        "message": "Session reset successfully"
    })


if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Starting AI Career Guidance Assistant Web Server...")
    print("📍 Local URL: http://127.0.0.1:5000")
    print("🎓 Student: Sarbajit Das (Code: DAS013423)")
    print("🏢 Company: Data Alcott Systems | Task: AI-SS-005")
    print("=" * 70)
    app.run(host="127.0.0.1", port=5000, debug=True)
