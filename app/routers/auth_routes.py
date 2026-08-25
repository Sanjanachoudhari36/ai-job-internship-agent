from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserLogin, Token, UserOut
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    user = User(
        name=payload.name,
        email=payload.email.lower(),
        password_hash=get_password_hash(payload.password),
        education="Bachelor's in Computer Science",
        skills='["Python", "JavaScript", "SQL", "Git"]',
        preferred_roles='["Software Engineer", "Full Stack Developer", "AI Engineer"]',
        preferred_locations='["Remote"]'
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.email, "user_id": user.user_id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "user_id": user.user_id,
            "name": user.name,
            "email": user.email,
            "education": user.education,
            "skills": user.get_skills_list()
        }
    }

@router.post("/login", response_model=Token)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    token = create_access_token({"sub": user.email, "user_id": user.user_id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "user_id": user.user_id,
            "name": user.name,
            "email": user.email,
            "education": user.education,
            "skills": user.get_skills_list()
        }
    }

@router.get("/me", response_model=UserOut)
def get_current_user_profile(user: User = Depends(get_current_user)):
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
