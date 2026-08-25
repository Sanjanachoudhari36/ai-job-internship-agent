import datetime
import json
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Profile information
    education = Column(String(255), default="")  # e.g., "B.Tech Computer Science"
    graduation_year = Column(Integer, nullable=True)  # e.g., 2026
    skills = Column(Text, default="[]")  # JSON encoded list of strings
    experience = Column(Text, default="")  # Description or JSON summary
    projects = Column(Text, default="")  # JSON or text description of key projects
    preferred_locations = Column(Text, default="[]")  # JSON encoded list of strings
    preferred_roles = Column(Text, default="[]")  # JSON encoded list of strings
    
    # Resume data
    resume_filename = Column(String(255), nullable=True)
    resume_text = Column(Text, default="")
    profile_summary = Column(Text, default="")
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    interview_sessions = relationship("InterviewSession", back_populates="user", cascade="all, delete-orphan")
    workflows = relationship("Workflow", back_populates="user", cascade="all, delete-orphan")

    def get_skills_list(self):
        try:
            return json.loads(self.skills) if self.skills else []
        except Exception:
            return [s.strip() for s in self.skills.split(",") if s.strip()] if self.skills else []

    def get_preferred_locations_list(self):
        try:
            return json.loads(self.preferred_locations) if self.preferred_locations else []
        except Exception:
            return [s.strip() for s in self.preferred_locations.split(",") if s.strip()] if self.preferred_locations else []

    def get_preferred_roles_list(self):
        try:
            return json.loads(self.preferred_roles) if self.preferred_roles else []
        except Exception:
            return [s.strip() for s in self.preferred_roles.split(",") if s.strip()] if self.preferred_roles else []


class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company = Column(String(200), nullable=False, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    skills_required = Column(Text, default="[]")  # JSON encoded list of strings
    education_required = Column(String(200), default="Bachelor's in CS or related field")
    experience_required = Column(String(100), default="0-1 years / Freshers eligible")
    location = Column(String(150), default="Remote / Hybrid")
    salary_or_stipend = Column(String(100), default="Competitive")
    deadline = Column(String(100), default="Open until filled")
    source = Column(String(100), default="Campus / AI Aggregator")
    job_type = Column(String(50), default="internship")  # "internship", "full-time", "contract"
    is_remote = Column(Boolean, default=False)
    company_logo = Column(String(255), nullable=True)
    posted_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    interview_sessions = relationship("InterviewSession", back_populates="job", cascade="all, delete-orphan")

    def get_skills_list(self):
        try:
            return json.loads(self.skills_required) if self.skills_required else []
        except Exception:
            return [s.strip() for s in self.skills_required.split(",") if s.strip()] if self.skills_required else []


class Application(Base):
    __tablename__ = "applications"

    application_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.job_id"), nullable=False, index=True)
    
    # Status: 'saved', 'applied', 'assessment', 'interview', 'selected', 'rejected'
    status = Column(String(50), default="saved", index=True)
    applied_date = Column(DateTime, nullable=True)
    interview_date = Column(DateTime, nullable=True)
    notes = Column(Text, default="")
    match_score = Column(Float, default=0.0)
    
    # AI generated artifacts saved with this application
    tailored_resume = Column(Text, default="")
    cover_letter = Column(Text, default="")
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    session_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.job_id"), nullable=True, index=True)
    
    role_title = Column(String(200), default="Software Engineer")
    company_name = Column(String(200), default="Tech Corp")
    interview_type = Column(String(50), default="Technical + Behavioral")
    
    # JSON list of questions, answers, feedback, and scores
    questions_data = Column(Text, default="[]")
    overall_score = Column(Float, default=0.0)
    strengths = Column(Text, default="[]")  # JSON
    improvements = Column(Text, default="[]")  # JSON
    status = Column(String(50), default="completed")
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="interview_sessions")
    job = relationship("Job", back_populates="interview_sessions")


class Workflow(Base):
    __tablename__ = "workflows"

    workflow_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    trigger_type = Column(String(50), default="manual")  # "manual", "on_new_job", "on_save_job"
    nodes = Column(Text, default="[]")  # JSON list of workflow agent steps/nodes
    icon = Column(String(50), default="fa-diagram-project")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="workflows")

    def get_nodes_list(self):
        try:
            return json.loads(self.nodes) if self.nodes else []
        except Exception:
            return []


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    execution_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    workflow_id = Column(Integer, ForeignKey("workflows.workflow_id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.job_id"), nullable=True)
    
    status = Column(String(50), default="completed")  # "running", "completed", "failed"
    steps_log = Column(Text, default="[]")  # JSON list of step logs
    results = Column(Text, default="{}")  # JSON output artifacts
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
