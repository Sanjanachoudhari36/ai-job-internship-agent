# AI Job & Internship Automation Platform

An **Agentic AI-powered Career Automation Platform** that intelligently discovers job and internship opportunities, evaluates candidate-job compatibility using a 6-factor weighted algorithm, personalizes resumes and cover letters, manages applications across a Kanban pipeline with deadline alerts, and prepares candidates for interviews through interactive AI mock simulations.

Built according to the project specification sheet ([spec.md](spec.md)) as the single source of truth.

---

## 🌟 Key Features & 7-Agent Architecture

The platform coordinates **7 specialized AI agents**:

| # | Agent Name | Primary Responsibility |
|---|------------|------------------------|
| **1** | 🤖 **Orchestrator Agent** | Coordinates multi-agent workflows, state management, and real-time execution telemetry. |
| **2** | 🔍 **Job Search Agent** | Discovers opportunities, normalizes data (role, company, salary/stipend, location, deadline), and deduplicates listings. |
| **3** | 🎯 **Job Matching Agent** | Calculates 6-factor compatibility scores (Skills 40%, Education 15%, Experience 15%, Projects 15%, Location 5%, Other 10%). |
| **4** | 📄 **Resume Agent** | Parses PDF/DOCX/TXT resumes, computes ATS compatibility (0-100), detects missing keywords, and generates impact-driven bullet points. |
| **5** | ✉️ **Cover Letter Agent** | Synthesizes candidate background + resume + target job description into tailored, high-converting cover letters with customizable tones. |
| **6** | 📊 **Application Tracking Agent** | Manages Kanban pipeline stages (`Saved` → `Applied` → `Assessment` → `Interview` → `Selected`/`Rejected`) with deadline alarms. |
| **7** | 🎤 **Interview Preparation Agent** | Generates technical, behavioral (STAR method), and company-specific questions; conducts interactive voice/text mock interviews with instant AI scoring. |

---

## 🚀 Quick Start & Local Setup Guide

Follow these steps to run the application on your local machine.

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.12)
- **Git** (optional)
- *Note: No Node.js or npm build step is required!* The frontend is pre-bundled and served directly via FastAPI.

---

### 2. Setup Virtual Environment (Recommended)

Open your terminal or PowerShell in the project directory:

#### **On Windows (PowerShell):**
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate
```

#### **On macOS / Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

---

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

---

### 4. Configuration (Optional)

Copy the example environment file:

```bash
# On Windows PowerShell:
Copy-Item .env.example .env

# On Mac/Linux:
cp .env.example .env
```

> **Note on AI Keys:** The platform includes a **built-in heuristic intelligence engine**, allowing all 7 agents, ATS analyzers, cover letters, and mock interviews to function **100% out of the box without any external API keys**.
> If you wish to connect live LLMs, simply add your `GEMINI_API_KEY`, `OPENAI_API_KEY`, or `GROQ_API_KEY` into `.env`.

---

### 5. Launch the Platform

You can start the platform using either of the following commands:

#### **Option A: One-Click Runner (Recommended)**
```bash
python run.py
```

#### **Option B: Direct Uvicorn Dev Server**
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

### 6. Access the Application

Once started, open your browser:

- 🌐 **Web Application:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- 📚 **Interactive Swagger API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 📖 **ReDoc API Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 👤 Default Demo Candidate Credentials

The database is automatically pre-seeded on first run with sample opportunities and a pre-configured candidate:

- **Email:** `student@example.com`
- **Password:** `password123`

*(You can also register a new account directly from the UI).*

---

## 🗂️ Project Directory Structure

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app entry point, CORS, routes & static mounts
│   ├── config.py                # App configuration, settings & environment variables
│   ├── database.py              # SQLAlchemy DB engine & session handling
│   ├── models.py                # Database models (User, Job, Application, InterviewSession)
│   ├── schemas.py               # Pydantic request/response validation schemas
│   ├── auth.py                  # JWT authentication & password verification
│   ├── seed_data.py             # Realistic opportunities & demo candidate dataset
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── ai_provider.py       # Unified LLM wrapper (Gemini/OpenAI/Groq/Ollama/Heuristics)
│   │   ├── orchestrator.py      # Agent 1: Workflow coordinator
│   │   ├── job_search_agent.py  # Agent 2: Job discovery & deduplication
│   │   ├── job_matching_agent.py# Agent 3: 6-factor weighted compatibility scorer (Spec Sec 8)
│   │   ├── resume_agent.py      # Agent 4: Resume parser (PDF/DOCX/TXT), ATS analyzer & tailoring
│   │   ├── cover_letter_agent.py# Agent 5: Personalized cover letter synthesis
│   │   ├── tracker_agent.py     # Agent 6: Pipeline state & deadline monitor
│   │   └── interview_agent.py   # Agent 7: Tech/HR question generator & mock evaluator
│   └── routers/
│       ├── __init__.py
│       ├── auth_routes.py       # /api/auth (register, login, me)
│       ├── profile_routes.py    # /api/profile (get, update, upload-resume)
│       ├── job_routes.py        # /api/jobs (list, filter, get, create)
│       ├── match_routes.py      # /api/match (calculate match, recommendations)
│       ├── agent_routes.py      # /api/agents (orchestrate, resume-tailor, cover-letter)
│       ├── application_routes.py# /api/applications (Kanban CRUD, update stage, notes)
│       ├── interview_routes.py  # /api/interview (generate questions, evaluate response)
│       └── analytics_routes.py  # /api/analytics (dashboard KPI metrics, deadlines)
├── static/
│   ├── index.html               # Main SPA shell
│   ├── css/
│   │   └── style.css            # Dark glassmorphic design system
│   └── js/
│       ├── api.js               # Centralized API client & state management
│       ├── app.js               # Router, modal system & toast notifications
│       └── components/
│           ├── dashboard.js     # AI Career Dashboard
│           ├── jobs.js          # Opportunities explorer & 1-click match modal
│           ├── resume.js        # AI Resume Studio & ATS analyzer
│           ├── cover_letter.js  # Smart Cover Letter generator & exporter
│           ├── tracker.js       # Drag-and-drop Kanban board & deadline alerts
│           ├── interview.js     # Interactive Mock Interview terminal (voice/text)
│           ├── orchestrator.js  # Live 7-Agent Pipeline visualizer
│           └── profile.js       # Candidate profile & skills manager
├── requirements.txt             # Python package dependencies
├── .env.example                 # Environment variables template
├── run.py                       # One-click startup script
├── README.md                    # Project documentation
└── spec.md                      # Specification sheet (single source of truth)
```

---

## 📊 Job Matching Algorithm (Section 8)

The compatibility score is computed as:

$$\text{Match Score} = (\text{Skill Match} \times 0.40) + (\text{Education Match} \times 0.15) + (\text{Experience Match} \times 0.15) + (\text{Project Match} \times 0.15) + (\text{Location Match} \times 0.05) + (\text{Other Criteria} \times 0.10)$$

---

## 🔒 Security & Privacy (Section 11)

- **Human-in-the-Loop Safeguards:** Important external actions (such as final application submissions) require explicit candidate confirmation.
- **Secure File Processing:** Resumes are processed locally and securely stored per authenticated user directory.
- **JWT Auth & Hash Protection:** Passwords securely hashed with standard key derivation functions.

---

## 🧪 Verification & Automated Testing

To run the automated verification suite:

```bash
python -c "import app.main; print('FastAPI App and Multi-Agent Engine loaded successfully!')"
```
