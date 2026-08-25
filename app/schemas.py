from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# ----------------- Auth Schemas -----------------
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    education: Optional[str] = None
    graduation_year: Optional[int] = None
    skills: Optional[List[str]] = None
    experience: Optional[str] = None
    projects: Optional[str] = None
    preferred_locations: Optional[List[str]] = None
    preferred_roles: Optional[List[str]] = None
    profile_summary: Optional[str] = None

class UserOut(BaseModel):
    user_id: int
    name: str
    email: str
    education: Optional[str] = ""
    graduation_year: Optional[int] = None
    skills: List[str] = []
    experience: Optional[str] = ""
    projects: Optional[str] = ""
    preferred_locations: List[str] = []
    preferred_roles: List[str] = []
    resume_filename: Optional[str] = None
    resume_text: Optional[str] = ""
    profile_summary: Optional[str] = ""
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ----------------- Job Schemas -----------------
class JobCreate(BaseModel):
    company: str
    title: str
    description: str
    skills_required: List[str] = []
    education_required: Optional[str] = "Bachelor's in CS or related field"
    experience_required: Optional[str] = "0-1 years"
    location: Optional[str] = "Remote / Hybrid"
    salary_or_stipend: Optional[str] = "Competitive"
    deadline: Optional[str] = "Open until filled"
    source: Optional[str] = "Platform Database"
    job_type: Optional[str] = "internship"
    is_remote: Optional[bool] = False
    company_logo: Optional[str] = None

class JobOut(BaseModel):
    job_id: int
    company: str
    title: str
    description: str
    skills_required: List[str] = []
    education_required: Optional[str] = ""
    experience_required: Optional[str] = ""
    location: Optional[str] = ""
    salary_or_stipend: Optional[str] = ""
    deadline: Optional[str] = ""
    source: Optional[str] = ""
    job_type: Optional[str] = ""
    is_remote: Optional[bool] = False
    company_logo: Optional[str] = None
    posted_at: Optional[datetime] = None
    match_score: Optional[float] = None
    match_breakdown: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

# ----------------- Matching Schemas -----------------
class MatchScoreBreakdown(BaseModel):
    skill_score: float = 0.0          # Weight: 40%
    education_score: float = 0.0      # Weight: 15%
    experience_score: float = 0.0     # Weight: 15%
    project_score: float = 0.0        # Weight: 15%
    location_score: float = 0.0       # Weight: 5%
    other_score: float = 0.0          # Weight: 10%
    overall_match_score: float = 0.0
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    experience_status: str = "Satisfied"
    education_status: str = "Satisfied"
    recommendations: List[str] = []
    fit_summary: str = ""

# ----------------- Resume Analysis & Tailoring -----------------
class ResumeAnalysisRequest(BaseModel):
    job_id: Optional[int] = None
    job_description: Optional[str] = None
    target_role: Optional[str] = None

class ResumeAnalysisResponse(BaseModel):
    ats_score: int
    extracted_skills: List[str]
    missing_keywords: List[str]
    strengths: List[str]
    improvements: List[str]
    bullet_suggestions: List[Dict[str, str]]
    tailored_resume_preview: str

class CoverLetterRequest(BaseModel):
    job_id: Optional[int] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    job_description: Optional[str] = None
    tone: Optional[str] = "Professional and Enthusiastic"
    key_highlights: Optional[str] = None

class CoverLetterResponse(BaseModel):
    cover_letter: str
    company_name: str
    job_title: str
    highlights_used: List[str]

# ----------------- Application Tracker Schemas -----------------
class ApplicationCreate(BaseModel):
    job_id: int
    status: Optional[str] = "saved"
    notes: Optional[str] = ""
    tailored_resume: Optional[str] = ""
    cover_letter: Optional[str] = ""

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    applied_date: Optional[datetime] = None
    interview_date: Optional[datetime] = None
    tailored_resume: Optional[str] = None
    cover_letter: Optional[str] = None

class ApplicationOut(BaseModel):
    application_id: int
    user_id: int
    job_id: int
    status: str
    applied_date: Optional[datetime] = None
    interview_date: Optional[datetime] = None
    notes: Optional[str] = ""
    match_score: Optional[float] = 0.0
    tailored_resume: Optional[str] = ""
    cover_letter: Optional[str] = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    job: Optional[JobOut] = None

    class Config:
        from_attributes = True

# ----------------- Interview Simulator Schemas -----------------
class InterviewQuestionGenerateRequest(BaseModel):
    job_id: Optional[int] = None
    role_title: Optional[str] = "Software Engineer"
    company_name: Optional[str] = "Tech Company"
    question_types: List[str] = ["Technical", "HR", "Company-Specific", "Problem-Solving"]
    count: int = 5

class InterviewQuestion(BaseModel):
    id: int
    question: str
    category: str
    difficulty: str
    context: str
    sample_key_points: List[str]

class InterviewEvaluateRequest(BaseModel):
    question_id: int
    question: str
    category: str
    user_answer: str
    role_title: str
    company_name: str

class InterviewEvaluationResult(BaseModel):
    score: int
    feedback: str
    strengths: List[str]
    weaknesses: List[str]
    model_answer: str
    tips_for_improvement: List[str]

# ----------------- Multi-Agent Orchestrator Pipeline -----------------
class OrchestratorRunRequest(BaseModel):
    job_id: int
    include_cover_letter: bool = True
    include_resume_tailoring: bool = True
    include_interview_prep: bool = True

class AgentStepLog(BaseModel):
    agent_name: str
    icon: str
    status: str  # pending, running, completed, error
    message: str
    timestamp: str
    data: Optional[Dict[str, Any]] = None

class OrchestratorRunResponse(BaseModel):
    session_id: str
    overall_status: str
    steps: List[AgentStepLog]
    results: Dict[str, Any]

# ----------------- AI Workflow Builder Schemas -----------------
class WorkflowNodeConfig(BaseModel):
    id: str
    agent_type: str   # 'job_search', 'matcher', 'resume_ats', 'cover_letter', 'tracker', 'interview_prep', 'condition', 'notification'
    label: str
    icon: str
    config: Dict[str, Any] = {}
    connections: List[str] = []

class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    trigger_type: Optional[str] = "manual"
    nodes: List[Dict[str, Any]] = []
    icon: Optional[str] = "fa-diagram-project"
    is_active: Optional[bool] = True

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    trigger_type: Optional[str] = None
    nodes: Optional[List[Dict[str, Any]]] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None

class WorkflowOut(BaseModel):
    workflow_id: int
    user_id: int
    name: str
    description: Optional[str] = ""
    trigger_type: str = "manual"
    nodes: List[Dict[str, Any]] = []
    icon: str = "fa-diagram-project"
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class WorkflowRunRequest(BaseModel):
    job_id: Optional[int] = None
    override_params: Optional[Dict[str, Any]] = None

class WorkflowRunResponse(BaseModel):
    workflow_id: int
    workflow_name: str
    execution_id: str
    status: str
    steps_executed: List[AgentStepLog]
    artifacts: Dict[str, Any]
