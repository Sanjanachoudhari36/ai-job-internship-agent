from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Job
from app.schemas import (
    ResumeAnalysisRequest, ResumeAnalysisResponse,
    CoverLetterRequest, CoverLetterResponse,
    OrchestratorRunRequest, OrchestratorRunResponse
)
from app.auth import get_current_user
from app.agents.resume_agent import ResumeAgent
from app.agents.cover_letter_agent import CoverLetterAgent
from app.agents.orchestrator import OrchestratorAgent
from app.agents.job_search_agent import JobSearchAgent

router = APIRouter(prefix="/agents", tags=["AI Agents Engine"])

@router.post("/analyze-resume", response_model=ResumeAnalysisResponse)
async def analyze_resume_endpoint(
    payload: ResumeAnalysisRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = None
    if payload.job_id:
        job = JobSearchAgent.get_job_by_id(db, payload.job_id)

    return await ResumeAgent.analyze_and_tailor(
        user=user,
        job=job,
        custom_jd=payload.job_description,
        target_role=payload.target_role
    )

@router.post("/generate-cover-letter", response_model=CoverLetterResponse)
async def generate_cover_letter_endpoint(
    payload: CoverLetterRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = None
    if payload.job_id:
        job = JobSearchAgent.get_job_by_id(db, payload.job_id)

    return await CoverLetterAgent.generate_cover_letter(
        user=user,
        job=job,
        company_name=payload.company_name,
        job_title=payload.job_title,
        job_description=payload.job_description,
        tone=payload.tone or "Professional and Enthusiastic",
        key_highlights=payload.key_highlights
    )

@router.post("/orchestrate", response_model=OrchestratorRunResponse)
async def orchestrate_agent_pipeline(
    payload: OrchestratorRunRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await OrchestratorAgent.run_full_pipeline(
        db=db,
        user=user,
        job_id=payload.job_id,
        include_cover_letter=payload.include_cover_letter,
        include_resume_tailoring=payload.include_resume_tailoring,
        include_interview_prep=payload.include_interview_prep
    )
