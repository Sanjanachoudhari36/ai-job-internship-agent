import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Job, User
from app.schemas import JobCreate, JobOut
from app.auth import get_optional_user, get_current_user
from app.agents.job_search_agent import JobSearchAgent
from app.agents.job_matching_agent import JobMatchingAgent

router = APIRouter(prefix="/jobs", tags=["Jobs & Internships"])

@router.get("", response_model=List[JobOut])
def get_jobs(
    q: Optional[str] = Query(None, description="Search query"),
    job_type: Optional[str] = Query(None, description="internship / full-time / all"),
    location: Optional[str] = Query(None, description="Location filter"),
    is_remote: Optional[bool] = Query(None, description="Remote filter"),
    limit: int = Query(50, ge=1, le=100),
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    jobs = JobSearchAgent.search_jobs(
        db=db,
        query=q,
        job_type=job_type,
        location=location,
        is_remote=is_remote,
        limit=limit
    )

    results = []
    for job in jobs:
        job_dict = {
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
            "company_logo": job.company_logo,
            "posted_at": job.posted_at,
            "match_score": None,
            "match_breakdown": None
        }

        # If user is authenticated, compute the match score
        if user:
            match_res = JobMatchingAgent.calculate_match(user, job)
            job_dict["match_score"] = match_res.overall_match_score
            job_dict["match_breakdown"] = match_res.model_dump()

        results.append(job_dict)

    # If user is logged in, sort by match score descending
    if user:
        results.sort(key=lambda x: x["match_score"] or 0, reverse=True)

    return results

@router.get("/{job_id}", response_model=JobOut)
def get_job(
    job_id: int,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    job = JobSearchAgent.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    job_dict = {
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
        "company_logo": job.company_logo,
        "posted_at": job.posted_at,
        "match_score": None,
        "match_breakdown": None
    }

    if user:
        match_res = JobMatchingAgent.calculate_match(user, job)
        job_dict["match_score"] = match_res.overall_match_score
        job_dict["match_breakdown"] = match_res.model_dump()

    return job_dict

@router.post("", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    job = Job(
        company=payload.company,
        title=payload.title,
        description=payload.description,
        skills_required=json.dumps(payload.skills_required),
        education_required=payload.education_required,
        experience_required=payload.experience_required,
        location=payload.location,
        salary_or_stipend=payload.salary_or_stipend,
        deadline=payload.deadline,
        source=payload.source or "User Submitted",
        job_type=payload.job_type or "internship",
        is_remote=payload.is_remote or False,
        company_logo=payload.company_logo
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return {
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
        "company_logo": job.company_logo,
        "posted_at": job.posted_at
    }
