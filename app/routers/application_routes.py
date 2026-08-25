from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Application, Job, User
from app.schemas import ApplicationCreate, ApplicationUpdate, ApplicationOut
from app.auth import get_current_user
from app.agents.tracker_agent import ApplicationTrackingAgent
from app.agents.job_matching_agent import JobMatchingAgent
from app.agents.job_search_agent import JobSearchAgent

router = APIRouter(prefix="/applications", tags=["Application Tracker"])

@router.get("", response_model=List[ApplicationOut])
def list_applications(
    status: Optional[str] = Query(None, description="Filter by status"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    apps = ApplicationTrackingAgent.get_user_applications(db, user.user_id, status)
    
    # Format with job relationship
    results = []
    for app in apps:
        app_dict = {
            "application_id": app.application_id,
            "user_id": app.user_id,
            "job_id": app.job_id,
            "status": app.status,
            "applied_date": app.applied_date,
            "interview_date": app.interview_date,
            "notes": app.notes,
            "match_score": app.match_score,
            "tailored_resume": app.tailored_resume,
            "cover_letter": app.cover_letter,
            "created_at": app.created_at,
            "updated_at": app.updated_at,
            "job": {
                "job_id": app.job.job_id,
                "company": app.job.company,
                "title": app.job.title,
                "description": app.job.description,
                "skills_required": app.job.get_skills_list(),
                "education_required": app.job.education_required,
                "experience_required": app.job.experience_required,
                "location": app.job.location,
                "salary_or_stipend": app.job.salary_or_stipend,
                "deadline": app.job.deadline,
                "source": app.job.source,
                "job_type": app.job.job_type,
                "is_remote": app.job.is_remote,
                "company_logo": app.job.company_logo
            } if app.job else None
        }
        results.append(app_dict)
    return results

@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def create_application(
    payload: ApplicationCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = JobSearchAgent.get_job_by_id(db, payload.job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    existing = db.query(Application).filter(
        Application.user_id == user.user_id,
        Application.job_id == payload.job_id
    ).first()

    if existing:
        # Update status if already exists
        existing.status = payload.status or existing.status
        if payload.notes:
            existing.notes = payload.notes
        db.commit()
        db.refresh(existing)
        target_app = existing
    else:
        match_res = JobMatchingAgent.calculate_match(user, job)
        new_app = Application(
            user_id=user.user_id,
            job_id=payload.job_id,
            status=payload.status or "saved",
            notes=payload.notes or "",
            match_score=match_res.overall_match_score,
            tailored_resume=payload.tailored_resume or "",
            cover_letter=payload.cover_letter or ""
        )
        db.add(new_app)
        db.commit()
        db.refresh(new_app)
        target_app = new_app

    return {
        "application_id": target_app.application_id,
        "user_id": target_app.user_id,
        "job_id": target_app.job_id,
        "status": target_app.status,
        "applied_date": target_app.applied_date,
        "interview_date": target_app.interview_date,
        "notes": target_app.notes,
        "match_score": target_app.match_score,
        "tailored_resume": target_app.tailored_resume,
        "cover_letter": target_app.cover_letter,
        "created_at": target_app.created_at,
        "updated_at": target_app.updated_at,
        "job": {
            "job_id": target_app.job.job_id,
            "company": target_app.job.company,
            "title": target_app.job.title,
            "description": target_app.job.description,
            "skills_required": target_app.job.get_skills_list(),
            "education_required": target_app.job.education_required,
            "experience_required": target_app.job.experience_required,
            "location": target_app.job.location,
            "salary_or_stipend": target_app.job.salary_or_stipend,
            "deadline": target_app.job.deadline,
            "source": target_app.job.source,
            "job_type": target_app.job.job_type,
            "is_remote": target_app.job.is_remote,
            "company_logo": target_app.job.company_logo
        } if target_app.job else None
    }

@router.put("/{application_id}", response_model=ApplicationOut)
def update_application(
    application_id: int,
    payload: ApplicationUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(
        Application.application_id == application_id,
        Application.user_id == user.user_id
    ).first()

    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    if payload.status:
        app.status = payload.status.lower()
    if payload.notes is not None:
        app.notes = payload.notes
    if payload.applied_date is not None:
        app.applied_date = payload.applied_date
    if payload.interview_date is not None:
        app.interview_date = payload.interview_date
    if payload.tailored_resume is not None:
        app.tailored_resume = payload.tailored_resume
    if payload.cover_letter is not None:
        app.cover_letter = payload.cover_letter

    db.commit()
    db.refresh(app)

    return {
        "application_id": app.application_id,
        "user_id": app.user_id,
        "job_id": app.job_id,
        "status": app.status,
        "applied_date": app.applied_date,
        "interview_date": app.interview_date,
        "notes": app.notes,
        "match_score": app.match_score,
        "tailored_resume": app.tailored_resume,
        "cover_letter": app.cover_letter,
        "created_at": app.created_at,
        "updated_at": app.updated_at,
        "job": {
            "job_id": app.job.job_id,
            "company": app.job.company,
            "title": app.job.title,
            "description": app.job.description,
            "skills_required": app.job.get_skills_list(),
            "education_required": app.job.education_required,
            "experience_required": app.job.experience_required,
            "location": app.job.location,
            "salary_or_stipend": app.job.salary_or_stipend,
            "deadline": app.job.deadline,
            "source": app.job.source,
            "job_type": app.job.job_type,
            "is_remote": app.job.is_remote,
            "company_logo": app.job.company_logo
        } if app.job else None
    }

@router.delete("/{application_id}")
def delete_application(
    application_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(
        Application.application_id == application_id,
        Application.user_id == user.user_id
    ).first()

    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    db.delete(app)
    db.commit()
    return {"message": "Application removed from pipeline successfully"}
