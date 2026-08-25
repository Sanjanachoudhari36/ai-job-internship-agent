import json
import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Job, InterviewSession
from app.schemas import (
    InterviewQuestionGenerateRequest, InterviewQuestion,
    InterviewEvaluateRequest, InterviewEvaluationResult
)
from app.auth import get_current_user
from app.agents.interview_agent import InterviewPreparationAgent
from app.agents.job_search_agent import JobSearchAgent

router = APIRouter(prefix="/interview", tags=["Interview Prep & Mock Simulator"])

@router.post("/questions", response_model=List[InterviewQuestion])
async def generate_interview_questions(
    payload: InterviewQuestionGenerateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = None
    if payload.job_id:
        job = JobSearchAgent.get_job_by_id(db, payload.job_id)

    role = payload.role_title or (job.title if job else "Software Engineer")
    comp = payload.company_name or (job.company if job else "Tech Company")

    return await InterviewPreparationAgent.generate_questions(
        job=job,
        role_title=role,
        company_name=comp,
        count=payload.count or 5
    )

@router.post("/evaluate", response_model=InterviewEvaluationResult)
async def evaluate_interview_response(
    payload: InterviewEvaluateRequest,
    user: User = Depends(get_current_user)
):
    return await InterviewPreparationAgent.evaluate_answer(
        question=payload.question,
        category=payload.category,
        user_answer=payload.user_answer,
        role_title=payload.role_title,
        company_name=payload.company_name
    )

@router.post("/save-session")
def save_interview_session(
    payload: Dict[str, Any],
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = InterviewSession(
        user_id=user.user_id,
        job_id=payload.get("job_id"),
        role_title=payload.get("role_title", "Software Engineer"),
        company_name=payload.get("company_name", "Tech Company"),
        interview_type=payload.get("interview_type", "Technical + Behavioral"),
        questions_data=json.dumps(payload.get("questions_data", [])),
        overall_score=float(payload.get("overall_score", 80.0)),
        strengths=json.dumps(payload.get("strengths", [])),
        improvements=json.dumps(payload.get("improvements", [])),
        status="completed"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"message": "Mock interview session saved successfully.", "session_id": session.session_id}

@router.get("/history")
def get_interview_history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == user.user_id
    ).order_by(InterviewSession.created_at.desc()).all()

    results = []
    for s in sessions:
        results.append({
            "session_id": s.session_id,
            "role_title": s.role_title,
            "company_name": s.company_name,
            "interview_type": s.interview_type,
            "overall_score": s.overall_score,
            "created_at": s.created_at,
            "questions_data": json.loads(s.questions_data) if s.questions_data else []
        })
    return results
