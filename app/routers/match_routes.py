from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Job, User
from app.schemas import MatchScoreBreakdown, JobOut
from app.auth import get_current_user
from app.agents.job_matching_agent import JobMatchingAgent
from app.agents.job_search_agent import JobSearchAgent

router = APIRouter(prefix="/match", tags=["Job Matching Engine"])

@router.post("/calculate/{job_id}", response_model=MatchScoreBreakdown)
def calculate_job_match(
    job_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = JobSearchAgent.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    return JobMatchingAgent.calculate_match(user, job)

@router.get("/recommendations")
def get_recommendations(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    jobs = db.query(Job).all()
    scored_jobs = []

    for job in jobs:
        match_breakdown = JobMatchingAgent.calculate_match(user, job)
        scored_jobs.append({
            "job": {
                "job_id": job.job_id,
                "company": job.company,
                "title": job.title,
                "description": job.description,
                "skills_required": job.get_skills_list(),
                "education_required": job.education_required,
                "experience_required": job.experience_required,
                "location": job.location,
                "salary_or_stipend": job.salary_or_stipend,
                "deadline": job.deadline,
                "source": job.source,
                "job_type": job.job_type,
                "is_remote": job.is_remote,
                "company_logo": job.company_logo
            },
            "match_score": match_breakdown.overall_match_score,
            "match_breakdown": match_breakdown.model_dump()
        })

    # Sort by overall match score descending
    scored_jobs.sort(key=lambda x: x["match_score"], reverse=True)

    best_matches = [j for j in scored_jobs if j["match_score"] >= 80.0]
    good_matches = [j for j in scored_jobs if 60.0 <= j["match_score"] < 80.0]
    potential_matches = [j for j in scored_jobs if j["match_score"] < 60.0]

    return {
        "total_evaluated": len(scored_jobs),
        "best_matches": best_matches,
        "good_matches": good_matches,
        "potential_matches": potential_matches,
        "top_recommended": scored_jobs[:6]
    }
