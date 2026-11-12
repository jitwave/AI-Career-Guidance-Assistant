"""NLP Engine for AI Career Guidance Assistant.
Handles text preprocessing, tokenization, lemmatization, stop-word removal,
TF-IDF feature extraction, hybrid machine-learning intent classification,
and career/skill entity recognition.
"""

import os
import re
import json
import logging
from typing import List, Dict, Any, Tuple, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Attempt NLTK imports with robust fallback
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    from nltk.tokenize import word_tokenize
    _HAS_NLTK = True
except ImportError:
    _HAS_NLTK = False

logger = logging.getLogger(__name__)

# Fallback English stop words if NLTK stopwords aren't downloaded
FALLBACK_STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're",
    "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he',
    'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's",
    'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
    'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are',
    'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do',
    'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because',
    'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
    'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to',
    'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
    'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
    'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
    'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't',
    'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll',
    'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't",
    'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't",
    'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn',
    "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't",
    'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
}


class NLPEngine:
    """Core Natural Language Processing and Intent Classification engine."""

    def __init__(self, intents_path: Optional[str] = None):
        self._init_nltk_components()
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), lowercase=True)
        self.classifier = MultinomialNB(alpha=0.1)
        self.is_trained = False
        self.intents_data: List[Dict[str, Any]] = []
        self.tag_responses: Dict[str, List[str]] = {}

        if intents_path and os.path.exists(intents_path):
            self.load_and_train_intents(intents_path)

    def _init_nltk_components(self):
        """Safely initialize NLTK lemmatizer and stopwords with fallback."""
        self.lemmatizer = None
        self.stop_words = set(FALLBACK_STOPWORDS)

        if _HAS_NLTK:
            try:
                self.lemmatizer = WordNetLemmatizer()
                # Test call to ensure wordnet is present
                self.lemmatizer.lemmatize("testing")
            except (LookupError, Exception):
                try:
                    nltk.download('wordnet', quiet=True)
                    self.lemmatizer = WordNetLemmatizer()
                except Exception:
                    self.lemmatizer = None

            try:
                self.stop_words = set(stopwords.words('english'))
            except (LookupError, Exception):
                try:
                    nltk.download('stopwords', quiet=True)
                    self.stop_words = set(stopwords.words('english'))
                except Exception:
                    self.stop_words = set(FALLBACK_STOPWORDS)

    def tokenize(self, text: str) -> List[str]:
        """Tokenize text using NLTK or regex fallback."""
        if _HAS_NLTK:
            try:
                return word_tokenize(text)
            except (LookupError, Exception):
                try:
                    nltk.download('punkt', quiet=True)
                    nltk.download('punkt_tab', quiet=True)
                    return word_tokenize(text)
                except Exception:
                    pass
        # Robust regex fallback preserving C++, C#, .NET, CI/CD
        return re.findall(r'[a-zA-Z0-9#\+\.\-]+', text)

    def lemmatize_token(self, token: str) -> str:
        """Lemmatize a single token if lemmatizer is available."""
        if self.lemmatizer:
            try:
                return self.lemmatizer.lemmatize(token.lower())
            except Exception:
                pass
        return token.lower()

    def preprocess_text(self, text: str, remove_stopwords: bool = True) -> str:
        """Clean and normalize text for model vectorization."""
        if not text:
            return ""
        # Clean special chars while keeping programming language symbols
        cleaned = re.sub(r'[^\w\s\+\#\/\.\-]', ' ', text.lower())
        tokens = self.tokenize(cleaned)
        
        filtered = []
        for t in tokens:
            t_lem = self.lemmatize_token(t)
            if remove_stopwords and t_lem in self.stop_words:
                continue
            if len(t_lem.strip()) > 0:
                filtered.append(t_lem)

        return " ".join(filtered)

    def load_and_train_intents(self, filepath: str):
        """Load intents from JSON and train TF-IDF Naive Bayes model."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.intents_data = data.get('intents', [])
        corpus_texts = []
        labels = []

        for item in self.intents_data:
            tag = item['tag']
            self.tag_responses[tag] = item.get('responses', [])
            for pattern in item.get('patterns', []):
                cleaned_pattern = self.preprocess_text(pattern, remove_stopwords=False)
                if cleaned_pattern:
                    corpus_texts.append(cleaned_pattern)
                    labels.append(tag)

        if corpus_texts and labels:
            X = self.vectorizer.fit_transform(corpus_texts)
            self.classifier.fit(X, labels)
            self.is_trained = True

    def classify_intent(self, text: str, min_confidence: float = 0.28) -> Tuple[str, float]:
        """Classify user intent using hybrid ML + Rule-based pattern matching."""
        if not text or not text.strip():
            return "unknown", 0.0

        lowered = text.lower().strip()

        # 1. Rule-based exact/substring priority for high-stakes intents
        rule_intent = self._rule_based_check(lowered)
        if rule_intent:
            return rule_intent, 1.0

        # 2. ML Classification via TF-IDF + Naive Bayes
        if self.is_trained:
            cleaned = self.preprocess_text(text, remove_stopwords=False)
            if cleaned:
                X = self.vectorizer.transform([cleaned])
                probs = self.classifier.predict_proba(X)[0]
                best_idx = np.argmax(probs)
                best_score = float(probs[best_idx])
                best_tag = self.classifier.classes_[best_idx]

                if best_score >= min_confidence:
                    return best_tag, best_score

        # 3. Fallback matching over raw patterns
        for item in self.intents_data:
            tag = item['tag']
            for pattern in item.get('patterns', []):
                if pattern.lower() in lowered or lowered in pattern.lower():
                    return tag, 0.75

        return "unknown", 0.0

    def _rule_based_check(self, text: str) -> Optional[str]:
        """Fast-path deterministic rule matching for common conversational keywords."""
        # Single-token greetings
        if text in {"hi", "hello", "hey", "hola", "greetings", "start"}:
            return "greeting"
        
        # Single-token exits
        if text in {"bye", "goodbye", "exit", "quit"}:
            return "goodbye"

        # Help
        if text in {"help", "menu", "commands", "features", "options"}:
            return "help"

        # Gratitude
        if any(w in text for w in ["thank you", "thanks", "appreciate"]):
            return "thank_you"

        # Salary query keywords
        if any(w in text for w in ["salary", "pay", "package", "compensation", "lpa", "earn"]):
            return "salary_inquiry"

        # Trends query keywords
        if any(w in text for w in ["trend", "demand in 2026", "market trend", "growing jobs", "future of jobs", "market demand"]):
            return "industry_trends"

        # Interview prep keywords
        if any(w in text for w in ["interview", "questions asked", "crack the interview", "interview tips", "interview prep"]):
            return "interview_prep"

        # Company research keywords
        if any(w in text for w in ["top companies", "who is hiring", "top recruiters", "best companies to work"]):
            return "company_research"

        # Learning roadmap keywords
        if any(w in text for w in ["roadmap", "how to become", "study plan", "where do i start learning"]):
            return "learning_roadmap"

        # Recommendation intent keywords
        if any(w in text for w in ["recommend", "suggest", "what should i choose", "match my", "best career for me"]):
            return "recommendation"

        # Career list keywords
        if any(w in text for w in ["list all careers", "all jobs", "explore careers", "show careers", "career options", "what careers"]):
            return "career_paths"

        # Profile declaration keywords
        if any(w in text for w in ["my skills are", "i know", "i have experience in", "my background is"]):
            return "set_profile"

        return None

    def extract_career_entity(self, text: str, careers: Dict[str, Any]) -> Optional[str]:
        """Extract a career title or alias from the user query."""
        lowered = text.lower()

        # Mapping of common abbreviations and aliases to exact career keys
        aliases = {
            "ai/ml engineer": "AI/ML Engineer",
            "ai engineer": "AI/ML Engineer",
            "ml engineer": "AI/ML Engineer",
            "machine learning engineer": "AI/ML Engineer",
            "artificial intelligence": "AI/ML Engineer",
            "data scientist": "Data Scientist",
            "data science": "Data Scientist",
            "data analyst": "Data Analyst",
            "business analyst": "Data Analyst",
            "software engineer": "Software Engineer",
            "sde": "Software Engineer",
            "software developer": "Software Engineer",
            "programmer": "Software Engineer",
            "full stack developer": "Full Stack Developer",
            "full stack": "Full Stack Developer",
            "fullstack": "Full Stack Developer",
            "web developer": "Full Stack Developer",
            "devops & cloud engineer": "DevOps & Cloud Engineer",
            "devops engineer": "DevOps & Cloud Engineer",
            "devops": "DevOps & Cloud Engineer",
            "sre": "DevOps & Cloud Engineer",
            "cyber security engineer": "Cyber Security Engineer",
            "cyber security": "Cyber Security Engineer",
            "cybersecurity": "Cyber Security Engineer",
            "security engineer": "Cyber Security Engineer",
            "ethical hacker": "Cyber Security Engineer",
            "pentester": "Cyber Security Engineer",
            "cloud solutions architect": "Cloud Solutions Architect",
            "cloud architect": "Cloud Solutions Architect",
            "solutions architect": "Cloud Solutions Architect",
            "cloud engineer": "Cloud Solutions Architect",
            "product manager": "Product Manager",
            "pm": "Product Manager",
            "mobile application developer": "Mobile Application Developer",
            "mobile developer": "Mobile Application Developer",
            "android developer": "Mobile Application Developer",
            "ios developer": "Mobile Application Developer",
            "flutter developer": "Mobile Application Developer",
            "ui/ux designer": "UI/UX Designer",
            "ui ux": "UI/UX Designer",
            "ui designer": "UI/UX Designer",
            "ux designer": "UI/UX Designer",
            "product designer": "UI/UX Designer",
            "blockchain developer": "Blockchain Developer",
            "blockchain": "Blockchain Developer",
            "web3 developer": "Blockchain Developer",
            "smart contract developer": "Blockchain Developer",
            "embedded systems & iot engineer": "Embedded Systems & IoT Engineer",
            "embedded engineer": "Embedded Systems & IoT Engineer",
            "iot engineer": "Embedded Systems & IoT Engineer",
            "embedded systems": "Embedded Systems & IoT Engineer",
            "firmware engineer": "Embedded Systems & IoT Engineer"
        }

        # Also add exact title keys to alias dictionary
        for title in careers.keys():
            aliases[title.lower()] = title

        # Check all candidates sorted by length descending (longest match wins)
        sorted_candidates = sorted(aliases.keys(), key=len, reverse=True)
        for cand in sorted_candidates:
            pattern = r'(?:\b|(?<=[\s,;]))' + re.escape(cand) + r'(?:\b|(?=[\s,;]))'
            if re.search(pattern, lowered):
                exact_key = aliases[cand]
                if exact_key in careers:
                    return exact_key

        return None

    def extract_skills(self, text: str, all_skills: List[str]) -> List[str]:
        """Extract technical skills mentioned in user text."""
        lowered = text.lower()
        found_skills = []

        # Sort candidate skills by length descending to match multi-word skills first
        sorted_skills = sorted(set(all_skills), key=len, reverse=True)
        
        for skill in sorted_skills:
            s_clean = skill.lower()
            # Boundary-safe match
            pattern = r'(?:\b|(?<=[\s,;]))' + re.escape(s_clean) + r'(?:\b|(?=[\s,;]))'
            if re.search(pattern, lowered):
                found_skills.append(skill)
                # Remove matched slice to prevent duplicate sub-word matching
                lowered = re.sub(pattern, ' ', lowered)

        return found_skills
