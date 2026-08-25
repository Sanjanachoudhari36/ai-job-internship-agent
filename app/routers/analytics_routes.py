import json
import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Job, Application, InterviewSession
from app.auth import get_current_user
from app.agents.job_matching_agent import JobMatchingAgent
from app.agents.tracker_agent import ApplicationTrackingAgent

router = APIRouter(prefix="/analytics", tags=["Dashboard Analytics"])

@router.get("/dashboard")
def get_dashboard_data(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Total opportunities
    total_jobs = db.query(Job).count()
    all_jobs = db.query(Job).all()

    # Calculate match scores for all opportunities
    scored_jobs = []
    for job in all_jobs:
        match_breakdown = JobMatchingAgent.calculate_match(user, job)
        scored_jobs.append({
            "job_id": job.job_id,
            "company": job.company,
            "title": job.title,
            "job_type": job.job_type,
            "location": job.location,
            "deadline": job.deadline,
            "salary_or_stipend": job.salary_or_stipend,
            "match_score": match_breakdown.overall_match_score,
            "strong_match": match_breakdown.matched_skills[:3],
            "missing": match_breakdown.missing_skills[:2]
        })

    scored_jobs.sort(key=lambda x: x["match_score"], reverse=True)

    best_match = scored_jobs[0] if scored_jobs else None
    good_match = scored_jobs[1] if len(scored_jobs) > 1 else None

    # Pipeline summary
    pipeline_data = ApplicationTrackingAgent.get_pipeline_summary(db, user.user_id)

    # Profile completion score
    profile_score = 20  # Base for registration
    if user.education:
        profile_score += 15
    if user.get_skills_list() and len(user.get_skills_list()) >= 3:
        profile_score += 20
    if user.experience and len(user.experience) > 20:
        profile_score += 15
    if user.projects and len(user.projects) > 20:
        profile_score += 15
    if user.resume_text and len(user.resume_text) > 50:
        profile_score += 15

    # Mock Interview stats
    mock_sessions = db.query(InterviewSession).filter(InterviewSession.user_id == user.user_id).all()
    avg_interview_score = 0.0
    if mock_sessions:
        avg_interview_score = round(sum(s.overall_score for s in mock_sessions) / len(mock_sessions), 1)

    return {
        "recommended_opportunities_count": total_jobs,
        "best_match": best_match,
        "good_match": good_match,
        "upcoming_deadlines": pipeline_data["deadlines"],
        "upcoming_interviews": pipeline_data["upcoming_interviews"],
        "applications_breakdown": pipeline_data["stages_breakdown"],
        "total_applications": pipeline_data["total_applications"],
        "profile_completion_percent": min(profile_score, 100),
        "mock_interviews_completed": len(mock_sessions),
        "average_interview_score": avg_interview_score,
        "top_recommendations": scored_jobs[:5]
    }
