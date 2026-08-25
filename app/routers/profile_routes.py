import os
import json
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models import User
from app.schemas import UserProfileUpdate, UserOut
from app.auth import get_current_user
from app.agents.resume_agent import ResumeAgent

router = APIRouter(prefix="/profile", tags=["User Profile"])

@router.get("", response_model=UserOut)
def get_profile(user: User = Depends(get_current_user)):
    return {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "education": user.education,
        "graduation_year": user.graduation_year,
        "skills": user.get_skills_list(),
        "experience": user.experience,
        "projects": user.projects,
        "preferred_locations": user.get_preferred_locations_list(),
        "preferred_roles": user.get_preferred_roles_list(),
        "resume_filename": user.resume_filename,
        "resume_text": user.resume_text,
        "profile_summary": user.profile_summary,
        "created_at": user.created_at
    }

@router.put("", response_model=UserOut)
def update_profile(
    payload: UserProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if payload.name is not None:
        user.name = payload.name
    if payload.education is not None:
        user.education = payload.education
    if payload.graduation_year is not None:
        user.graduation_year = payload.graduation_year
    if payload.skills is not None:
        user.skills = json.dumps(payload.skills)
    if payload.experience is not None:
        user.experience = payload.experience
    if payload.projects is not None:
        user.projects = payload.projects
    if payload.preferred_locations is not None:
        user.preferred_locations = json.dumps(payload.preferred_locations)
    if payload.preferred_roles is not None:
        user.preferred_roles = json.dumps(payload.preferred_roles)
    if payload.profile_summary is not None:
        user.profile_summary = payload.profile_summary

    db.commit()
    db.refresh(user)

    return {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "education": user.education,
        "graduation_year": user.graduation_year,
        "skills": user.get_skills_list(),
        "experience": user.experience,
        "projects": user.projects,
        "preferred_locations": user.get_preferred_locations_list(),
        "preferred_roles": user.get_preferred_roles_list(),
        "resume_filename": user.resume_filename,
        "resume_text": user.resume_text,
        "profile_summary": user.profile_summary,
        "created_at": user.created_at
    }

@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    filename = file.filename or "resume.pdf"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in [".pdf", ".docx", ".doc", ".txt", ".md"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload PDF, DOCX, or TXT."
        )

    user_upload_dir = os.path.join(settings.UPLOAD_DIR, str(user.user_id))
    os.makedirs(user_upload_dir, exist_ok=True)
    saved_path = os.path.join(user_upload_dir, filename)

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text and skills
    extracted_text = ResumeAgent.extract_text_from_file(saved_path)
    extracted_skills = ResumeAgent.extract_skills_heuristic(extracted_text)

    user.resume_filename = filename
    user.resume_text = extracted_text
    
    # Merge existing skills with extracted skills
    existing_skills = user.get_skills_list()
    merged_skills = list(dict.fromkeys(existing_skills + extracted_skills))
    user.skills = json.dumps(merged_skills)

    db.commit()
    db.refresh(user)

    return {
        "message": "Resume uploaded and parsed successfully.",
        "filename": filename,
        "extracted_skills": extracted_skills,
        "total_skills": merged_skills,
        "char_count": len(extracted_text)
    }
