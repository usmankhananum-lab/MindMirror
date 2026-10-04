# 🧠 MindMirror

> **"You only know it if you can teach it."**

MindMirror is an AI-powered learning and self-evaluation tool based on the **Feynman Technique**. Instead of explaining a topic to you, the AI plays a confused beginner and asks questions while *you* teach. At the end, an Evaluator Agent scores your explanation and shows exactly what you understood and what you didn't.

Built as a 2-day hackathon MVP with Python, the Grok API and Streamlit.

---

## Table of Contents

- [The Problem](#the-problem)
- [How It Works](#how-it-works)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Roadmap](#roadmap)
- [Team](#team)

---

## The Problem

Students often believe they understand a topic after reading or memorising it, but struggle to explain it clearly in their own words. Most learning tools give information or quizzes. They rarely test whether you can actually **teach** a concept.

MindMirror closes that gap with an interactive loop: you teach the AI, the AI asks clarifying questions, and an evaluator pinpoints your real strengths and gaps.

## How It Works

1. **Teach**: choose a topic and the audience level, then explain it in your own words.
2. **Get questioned**: the Confused Student Agent asks 3 to 5 beginner-style follow-up questions, one per round.
3. **Answer**: you answer each question.
4. **Get evaluated**: the Evaluator Agent reads the whole conversation and produces a report.
5. **Practise again**: weak topics are saved so you can return and improve.

## Features

- Topic input with an **"Explain it like I'm a…"** audience level (default: Complete Beginner)
- **AI Confused Student Agent** that asks questions and never teaches the topic
- **3 to 5 question rounds** with a progress bar
- **Evaluation report**: clarity score (1 to 10), strengths, gaps and 3 concepts to revise
- **Download Report** as a text file
- **Session History** with timestamps
- **Weak-topic memory** and **Practice This Topic Again**
- Friendly error messages and retry on API failures


## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application logic and integration |
| Grok API | AI for the Student and Evaluator agents |
| Streamlit | Web interface |
| JSON / Session State | Lightweight memory and session data |
| GitHub | Source control and collaboration |

## Architecture

```
Learner ⇄ Streamlit UI (app.py)
              │
              ├── Confused Student Agent (modules/student_agent.py) ─┐
              ├── Evaluator Agent        (modules/evaluator.py)      ─┼─► Grok API (services/llm.py)
              └── Memory Manager         (services/memory.py) ──► memory.json
```

- **Confused Student Agent**: input is the topic, learner level and conversation history; output is one beginner-style question.
- **Evaluator Agent**: input is the topic and the full conversation; output is the clarity score, strengths, gaps and three revision concepts.
- **Memory Manager**: saves completed sessions and weak topics to JSON.
- Prompts live in `prompts/prompts.py`, separate from the code.

## Project Structure

```
MindMirror/
├── app.py                  # Streamlit app and UI flow
├── modules/
│   ├── student_agent.py    # Confused Student Agent
│   └── evaluator.py        # Evaluator Agent
├── services/
│   ├── llm.py              # Grok API client
│   └── memory.py           # Session and weak-topic memory
├── prompts/
│   └── prompts.py          # Prompt templates
├── memory.json             # Saved sessions
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.9 or newer
- A Grok API key

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/MindMirror.git
cd MindMirror

# 2. (Optional) create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Run the app

https://mindmirror-vndjxbqxxgammcvs5yndwx.streamlit.app/

## Usage

1. Enter the topic you want to teach.
2. Pick the audience level and write your explanation.
3. Choose the number of question rounds and click **Start Teaching**.
4. Answer each question from the AI student.
5. Read your evaluation report, then **Download Report**, **Practice This Topic Again** or **Teach a New Topic**.

## Reliability and Security

- Maximum of 5 AI rounds per session
- API errors are handled with a retry option instead of crashing
- API credentials are kept outside the source code, in Streamlit secrets

## Roadmap

- [ ] Voice-based teaching and speech-to-text
- [ ] Urdu and Roman Urdu support
- [ ] Spaced-repetition reminders
- [ ] Persistent user accounts

## Team

| Member | Role |
|---|---|
| **Anum Usman Khan** | Team Lead: coordination, testing, PRD, demo and submission |
| **Syed Ghulam Ahmed** | Grok API integration and Confused Student Agent |
| **Aquib Ali** | Evaluator Agent and Memory |
| **Noor-ul-Ain** | Streamlit UI and integration |

---

Built for a 2-day hackathon. *You only know it if you can teach it.*
