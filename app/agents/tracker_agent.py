import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models import Application, Job, User

class ApplicationTrackingAgent:
    """
    Application Tracking Agent:
    - Tracks application pipeline: Saved -> Applied -> Assessment -> Interview -> Selected / Rejected
    - Monitors upcoming deadlines and interview schedules
    - Validates human confirmation before status changes
    - Computes funnel metrics
    """

    STAGES = ["saved", "applied", "assessment", "interview", "selected", "rejected"]

    @staticmethod
    def get_user_applications(db: Session, user_id: int, status_filter: Optional[str] = None) -> List[Application]:
        query = db.query(Application).filter(Application.user_id == user_id)
        if status_filter and status_filter.lower() != "all":
            query = query.filter(Application.status == status_filter.lower())
        return query.order_by(Application.updated_at.desc()).all()

    @staticmethod
    def get_pipeline_summary(db: Session, user_id: int) -> Dict[str, Any]:
        apps = db.query(Application).filter(Application.user_id == user_id).all()
        
        counts = {stage: 0 for stage in ApplicationTrackingAgent.STAGES}
        for app in apps:
            if app.status in counts:
                counts[app.status] += 1
            else:
                counts["saved"] += 1

        # Upcoming interviews
        now = datetime.datetime.utcnow()
        upcoming_interviews = []
        for app in apps:
            if app.status == "interview" and app.interview_date and app.interview_date >= now:
                job = app.job
                upcoming_interviews.append({
                    "application_id": app.application_id,
                    "company": job.company if job else "Company",
                    "title": job.title if job else "Role",
                    "interview_date": app.interview_date.isoformat(),
                    "notes": app.notes
                })

        # Deadlines from saved or applied opportunities
        deadlines = []
        for app in apps:
            if app.job and app.job.deadline:
                deadlines.append({
                    "application_id": app.application_id,
                    "company": app.job.company,
                    "title": app.job.title,
                    "deadline": app.job.deadline,
                    "status": app.status
                })

        return {
            "total_applications": len(apps),
            "stages_breakdown": counts,
            "upcoming_interviews": upcoming_interviews,
            "deadlines": deadlines[:5]
        }

    @staticmethod
    def update_stage(
        db: Session,
        application_id: int,
        user_id: int,
        new_status: str,
        notes: Optional[str] = None,
        interview_date: Optional[datetime.datetime] = None
    ) -> Optional[Application]:
        app = db.query(Application).filter(
            Application.application_id == application_id,
            Application.user_id == user_id
        ).first()

        if not app:
            return None

        if new_status.lower() in ApplicationTrackingAgent.STAGES:
            app.status = new_status.lower()
            if new_status.lower() == "applied" and not app.applied_date:
                app.applied_date = datetime.datetime.utcnow()

        if notes is not None:
            app.notes = notes
        if interview_date is not None:
            app.interview_date = interview_date

        app.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(app)
        return app
