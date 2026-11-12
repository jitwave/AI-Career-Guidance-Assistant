
"""Interactive Command-Line Interface (CLI) for AI Career Guidance Assistant.
Internship Task ID: AI-SS-005
Domain: Student Support & Internship Management NLP
Student: Sarbajit Das (Code: DAS013423)
Company: Data Alcott Systems
"""

import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.assistant import CareerGuidanceAssistant

BANNER = r"""
========================================================================================
   ___    ____   ____                                ____       _     _                      
  / _ \  |  _ \ |  _ \  ___   _ __ ___  _ __  ___   / ___|_   _(_) __| | __ _ _ __   ___ ___ 
 / /_\ \ | | | || | | |/ _ \ | '_ ` _ \| '_ \/ __| | |  _| | | | |/ _` |/ _` | '_ \ / __/ _ \
|  _  | || |_| || |_| | (_) || | | | | | |_) \__ \ | |_| | |_| | | (_| | (_| | | | | (_|  __/
|_| |_|_||____/ |____/ \___/ |_| |_| |_| .__/|___/  \____|\__,_|_|\__,_|\__,_|_| |_|\___\___|
                                        |_|                                                    
   AI CAREER GUIDANCE ASSISTANT | Conversational AI & NLP System
   Task ID: AI-SS-005 | Domain: Student Support NLP
   Student: Sarbajit Das | Student Code: DAS013423
   Company: Data Alcott Systems (www.dataalcott.com)
========================================================================================
"""

MENU_OPTIONS = """
📌 Quick Action Commands:
  [1] 💼 Explore All 13 Careers Catalog
  [2] 🎯 Run Guided Profile Recommendation
  [3] 💰 Salary Insights & Pay Scales
  [4] 📈 2026 Tech Industry Trends
  [5] 📝 Top Interview Questions & Tips
  [6] 🔄 Reset Conversation / Profile
  [0] 🚪 Exit Application
  ...Or just type ANY career question naturally! (e.g. 'Tell me about DevOps')
----------------------------------------------------------------------------------------
"""


def main():
    print(BANNER)
    print("⏳ Initializing AI NLP Models and Career Knowledge Base...")
    try:
        assistant = CareerGuidanceAssistant()
        print("✅ Assistant Ready! Model trained on career intent corpus.\n")
    except Exception as e:
        print(f"❌ Initialization Error: {e}")
        return

    print(MENU_OPTIONS)
    session_id = "cli_user_session"

    while True:
        try:
            user_input = input("👤 You > ").strip()
            if not user_input:
                continue

            # Check numeric shortcut menus
            if user_input == "0" or user_input.lower() in {"exit", "quit", "bye"}:
                print("\n🤖 Assistant: Thank you for consulting the AI Career Guidance Assistant. Keep learning and thriving! Goodbye! 👋\n")
                break

            elif user_input == "1":
                query = "List all careers"
            elif user_input == "2":
                skills = input("   Enter your skills (e.g., Python, SQL, Machine Learning): ").strip()
                interests = input("   Enter your interests (e.g., AI models, data insights, web apps): ").strip()
                query = f"Recommend a career for skills: {skills}. Interests: {interests}"
            elif user_input == "3":
                role = input("   Enter specific role for salary (or press Enter for overview): ").strip()
                query = f"Salary of {role}" if role else "Tech salary overview"
            elif user_input == "4":
                query = "What are the latest industry trends?"
            elif user_input == "5":
                role = input("   Enter role for interview prep (e.g., Data Scientist): ").strip()
                query = f"Interview preparation for {role}" if role else "Interview tips"
            elif user_input == "6":
                query = "reset profile"
            else:
                query = user_input

            print("\n🤖 Assistant is thinking...\n")
            result = assistant.process_query(query, session_id=session_id)
            print("🤖 Assistant:")
            print("-" * 70)
            print(result["response"])
            print("-" * 70)
            print()

        except (KeyboardInterrupt, EOFError):
            print("\n\nSession terminated by user. Goodbye!")
            break
        except Exception as err:
            print(f"\n❌ Error processing query: {err}\n")


if __name__ == "__main__":
    main()
