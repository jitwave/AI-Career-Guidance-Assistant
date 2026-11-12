# 🤖 AI Career Guidance Assistant 

[![Python Version](https://img.shields.io/badge/Python-3.14%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Flask-3.1.3-green.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![NLP Engine](https://img.shields.io/badge/NLP-NLTK%20%7C%20Scikit--Learn-orange.svg)](https://scikit-learn.org/)
[![Internship](https://img.shields.io/badge/Task%20ID-AI--SS--005-purple.svg)](https://www.dataalcott.com)
[![Student Code](https://img.shields.io/badge/Student%20Code-DAS013423-informational.svg)](#)
[![Status](https://img.shields.io/badge/Status-Completed-success.svg)](#)

> **Free Online AI & Data Science Internship**  
> **Domain**: Student Support & Internship Management NLP  
> **Task Name**: AI Career Guidance Assistant  
> **Student Name**: Sarbajit Das  
> **Student Code**: `DAS013423`  
> **Company**: Data Alcott Systems ([www.dataalcott.com](https://www.dataalcott.com))  
> **Location**: Work From Home Remote  

---

## 📌 Project Overview

The **AI Career Guidance Assistant** is an intelligent conversational chatbot and decision-support system designed to empower students and early-career software professionals to explore career paths, discover prerequisite skills, understand compensation trends, identify personalized skill gaps, and prepare for interviews.

Using Natural Language Processing (NLP), hybrid machine-learning intent classification, and vector-space recommendation algorithms, this assistant provides tailored guidance grounded in candidate profiles without requiring external database servers (leveraging clean, structured JSON knowledge stores).

Dual interfaces are provided:
1. **Interactive Terminal CLI**: Rapid command-line user interaction with ASCII headers and colored prompts.
2. **Modern Glassmorphic Web Application (Flask)**: Interactive conversational chat, 13-track Career Explorer card catalog, interactive skill-gap assessment pills, and a 2026 tech trends dashboard.

---

## 🎯 Learning Objectives

| Objective | Description | Implementation in Project |
| :--- | :--- | :--- |
| **NLP Fundamentals** | Learn text preprocessing, tokenization, lemmatization, and stop-word removal. | Implemented in `src/nlp_engine.py` using NLTK WordNetLemmatizer, custom regex tokenizers preserving tech keywords (e.g. `C++`, `C#`, `.NET`), and stop-word filtering. |
| **Career Domain Knowledge** | Understand various career paths, salary brackets, and industry requirements. | Modeled 13 industry domains in `data/careers.json` with progression tracks, recruiters, and interview questions. |
| **Intent Classification** | Build an ML model to understand career-related queries. | Supervised text classification via TF-IDF Vectorization and Multinomial Naive Bayes (`src/nlp_engine.py`) with deterministic rule fallbacks. |
| **Profile-Based Recommendations** | Suggest career paths based on student interests and skills. | Hybrid matching formulation (`src/recommender.py`) combining TF-IDF cosine similarity with Jaccard skill-set coverage. |
| **Dialog Management** | Create multi-turn conversation flows and slot filling. | Finite state machine (`src/dialog_manager.py`) managing session states (`AWAITING_SKILLS`, `AWAITING_INTERESTS`, `IDLE`). |
| **Knowledge Base Integration** | Connect career information database to the chatbot. | Zero-database JSON data layer (`careers.json`, `intents.json`, `trends.json`). |

---

## ✨ Features Implemented

### 🚀 Core Features
- [x] **Greeting & Introduction**: Welcomes students and provides quick suggestion options.
- [x] **Career Path Exploration**: 13 comprehensive tech tracks with role overviews and progressions.
- [x] **Skill Requirement Analysis**: Dissects required core competencies and tools per domain.
- [x] **Industry Trends Insights**: High-growth tech domains, CAGR velocity, and hiring predictions.
- [x] **Profile-Based Recommendations**: Mathematical matching combining TF-IDF cosine similarity with Jaccard skill-set coverage.
- [x] **Dialog Management & Slot Filling**: Multi-turn conversation handling user skills and interests interactively.

### ⭐ Bonus Features
- [x] **Salary Insights**: Detailed entry, mid, and senior salary brackets in INR LPA and USD.
- [x] **Job Market Predictions**: 2025-2027 market demand trends and work-mode distributions.
- [x] **Top Recruiter Research**: Hiring companies identified for each career track (e.g., Google, Amazon, Microsoft, Palo Alto Networks, Bosch).
- [x] **Interview Preparation Tips**: Real-world technical questions and strategic preparation advice.
- [x] **4-Phase Learning Roadmaps**: Structured step-by-step learning progression per career.
- [x] **Modern Web Interface**: Responsive Flask UI with tabs for Chat, Career Explorer, Skill Matcher, and Market Trends.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph UI_Layer [User Interface Layer]
        CLI["Terminal CLI App (cli_app.py)"]
        WEB["Flask Web UI (app.py / templates)"]
    end

    subgraph Core_Engine [AI & Dialog Engine]
        DM["Dialog Manager (src/dialog_manager.py)"]
        NLP["NLP Engine & Intent Classifier (src/nlp_engine.py)"]
        REC["Recommendation & Skill Gap Engine (src/recommender.py)"]
    end

    subgraph Data_Layer [Knowledge Base (JSON Store)]
        CAREERS[("careers.json (13 Tracks)")]
        INTENTS[("intents.json (Patterns & Responses)")]
        TRENDS[("trends.json (Market Predictions)")]
    end

    CLI -->|User Query| DM
    WEB -->|HTTP POST /api/chat| DM
    DM --> NLP
    NLP --> INTENTS
    DM --> REC
    REC --> CAREERS
    DM --> TRENDS
    DM -->|Response| CLI
    DM -->|JSON Response| WEB
```

---

## 📁 Project Directory Structure

```
5th sem internship/
├── data/
│   ├── careers.json              # 13 high-demand career tracks
│   ├── intents.json              # Conversational patterns & responses
│   └── trends.json               # 2026 tech trends & compensation data
├── src/
│   ├── __init__.py
│   ├── nlp_engine.py             # Preprocessing, TF-IDF, Naive Bayes classifier
│   ├── recommender.py            # Cosine similarity & skill gap analyzer
│   ├── dialog_manager.py         # Multi-turn stateful session manager
│   └── assistant.py              # Unified assistant engine
├── templates/
│   └── index.html                # Responsive web app UI (Chat + Explorer)
├── static/
│   ├── css/
│   │   └── style.css             # Glassmorphic dark UI styling
│   └── js/
│       └── chat.js               # Async UI interactions & API client
├── tests/
│   ├── __init__.py
│   ├── test_nlp.py               # NLP unit tests
│   ├── test_recommender.py       # Recommender unit tests
│   └── test_assistant.py         # End-to-end dialog unit tests
├── .gitignore                    # Git ignore file
├── app.py                        # Flask Web Application entrypoint
├── cli_app.py                    # Terminal interactive interface
├── requirements.txt              # Frozen dependencies
├── PROJECT_REPORT.md             # Formal internship project report
└── README.md                     # Documentation & setup guide
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.10+ (Tested on Python 3.14.4)
- Git

### 1. Clone or Open Project
```bash
cd "5th sem internship"
```

### 2. Activate Virtual Environment & Install Dependencies
```bash
# Windows
.venv\Scripts\activate
pip install -r requirements.txt

# Or to initialize a fresh virtual environment:
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

### 3. Download Required NLTK Resources
```bash
.venv\Scripts\python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet')"
```

---

## 🚀 Running the Assistant

### Option A: Web Application (Recommended)
Launch the Flask web server:
```bash
.venv\Scripts\python app.py
```
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

**Web Views & Tabs:**
1. 💬 **AI Counselor**: Real-time conversational chat with quick suggestion pills.
2. 💼 **Career Explorer**: Interactive cards for all 13 careers with search, category filtering, and modal deep dives.
3. 🎯 **Skill Matcher**: Select skills from clickable pills or custom text to get match percentages and view skill gaps (matched vs missing).
4. 📈 **Market Trends**: Visual cards showcasing 2026 industry growth rates, salaries, and hiring predictions.

---

### Option B: Terminal CLI Interface
Launch the interactive command-line application:
```bash
.venv\Scripts\python cli_app.py
```

**Interactive Menu Options:**
- `[1]` 💼 Explore All 13 Careers Catalog
- `[2]` 🎯 Run Guided Profile Recommendation
- `[3]` 💰 Salary Insights & Pay Scales
- `[4]` 📈 2026 Tech Industry Trends
- `[5]` 📝 Top Interview Questions & Tips
- `[6]` 🔄 Reset Conversation / Profile
- `[0]` 🚪 Exit Application
- ...Or type any natural language query (e.g. *"Tell me about Data Scientist"* or *"What skills do I need for DevOps?"*).

---

## 🧪 Running Automated Unit Tests

Execute the automated test suite covering all layers (NLP, recommendation math, slot filling, and dialogue):
```bash
.venv\Scripts\python -m unittest discover -s tests -p "test_*.py" -v
```

**Sample Output:**
```
test_career_exploration_flow (test_assistant.TestCareerGuidanceAssistant.test_career_exploration_flow) ... ok
test_greeting_flow (test_assistant.TestCareerGuidanceAssistant.test_greeting_flow) ... ok
test_interview_prep_flow (test_assistant.TestCareerGuidanceAssistant.test_interview_prep_flow) ... ok
test_multi_turn_slot_filling (test_assistant.TestCareerGuidanceAssistant.test_multi_turn_slot_filling) ... ok
test_reset_flow (test_assistant.TestCareerGuidanceAssistant.test_reset_flow) ... ok
test_salary_flow (test_assistant.TestCareerGuidanceAssistant.test_salary_flow) ... ok
test_career_entity_extraction (test_nlp.TestNLPEngine.test_career_entity_extraction) ... ok
test_greeting_intent (test_nlp.TestNLPEngine.test_greeting_intent) ... ok
test_interview_prep_intent (test_nlp.TestNLPEngine.test_interview_prep_intent) ... ok
test_salary_intent (test_nlp.TestNLPEngine.test_salary_intent) ... ok
test_skills_extraction (test_nlp.TestNLPEngine.test_skills_extraction) ... ok
test_tokenization_and_preprocessing (test_nlp.TestNLPEngine.test_tokenization_and_preprocessing) ... ok
test_trends_intent (test_nlp.TestNLPEngine.test_trends_intent) ... ok
test_recommendation_ranking (test_recommender.TestCareerRecommender.test_recommendation_ranking) ... ok
test_recommender_initialization (test_recommender.TestCareerRecommender.test_recommender_initialization) ... ok
test_skill_gap_analysis (test_recommender.TestCareerRecommender.test_skill_gap_analysis) ... ok
test_web_dev_recommendation (test_recommender.TestCareerRecommender.test_web_dev_recommendation) ... ok

----------------------------------------------------------------------
Ran 17 tests in 9.614s

OK (All 17 Unit Tests Passed)
```

---

## 🌐 REST API Documentation

| HTTP Method | Endpoint | Description | Sample Payload |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/chat` | Main conversational query | `{"message": "Tell me about AI/ML Engineer", "session_id": "user_1"}` |
| `GET` | `/api/careers` | Retrieve all 13 career profiles | None |
| `GET` | `/api/career/<key>` | Retrieve single career details | None |
| `POST` | `/api/recommend` | Direct profile recommendation | `{"skills": ["Python", "SQL"], "interests": "Machine Learning", "top_n": 3}` |
| `GET` | `/api/trends` | Fetch 2026 tech trends & compensation | None |
| `POST` | `/api/reset` | Clear session history and profile | `{"session_id": "user_1"}` |

---

## 📅 1-Week Project Timeline Implementation

- **Day 1 – Research & Planning**: Established project architecture, tokenization pipelines, and conversation flows.
- **Day 2 – Career Data & Intent Setup**: Modeled 13 high-demand careers in `data/careers.json` and 13 intent categories in `data/intents.json`.
- **Day 3 – NLP & Conversation Engine**: Built NLTK lemmatization, regex tokenization, and TF-IDF Multinomial Naive Bayes classifier in `src/nlp_engine.py`.
- **Day 4 – Career Recommendation Engine**: Formulated hybrid cosine similarity and skill-overlap matching in `src/recommender.py`.
- **Day 5 – Trends & Insights**: Aggregated 2025-2027 market trends, salary brackets, and hiring predictions in `data/trends.json`.
- **Day 6 – Testing & Web Interface**: Developed the modern glassmorphism Flask Web UI, interactive terminal CLI, and built 17 automated tests.
- **Day 7 – Documentation & Submission**: Authored formal `PROJECT_REPORT.md` and complete `README.md`.

---

## ❓ Frequently Asked Questions (FAQ)

**Q: What is the AI Career Guidance Assistant?**  
A: It is an intelligent conversational AI chatbot designed for students to explore tech careers, evaluate skill prerequisites, uncover personal skill gaps, and explore real-world industry compensation benchmarks.

**Q: Does this project require an external database like MySQL or MongoDB?**  
A: No database server is required. Career data, intent definitions, and market trends are stored in structured, lightning-fast JSON files (`data/careers.json`, `data/intents.json`, `data/trends.json`).

**Q: How does the recommendation algorithm calculate match scores?**  
A: It utilizes a hybrid model: TF-IDF vector space cosine similarity (for semantic understanding of user interests) combined with Jaccard core-skill coverage and tool familiarity. It explicitly categorizes matched skills versus missing skills to bridge.

---

## 🎓 Internship Submission Credentials

- **Task ID**: `AI-SS-005`
- **Domain**: `Student Support & Internship Management NLP`
- **Student Name**: `Sarbajit Das`
- **Student Code**: `DAS013423`
- **Company**: `Data Alcott Systems` ([www.dataalcott.com](https://www.dataalcott.com))
- **Status**: Completed & Verified ✅
