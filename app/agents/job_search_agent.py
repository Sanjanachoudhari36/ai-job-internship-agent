import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Job

class JobSearchAgent:
    """
    Job Search Agent:
    - Searches supported job/internship sources
    - Collects job title, company, location, skills, salary/stipend and deadline
    - Removes duplicate opportunities
    - Filters by keywords, roles, location, and type
    """

    @staticmethod
    def search_jobs(
        db: Session,
        query: Optional[str] = None,
        job_type: Optional[str] = None,
        location: Optional[str] = None,
        is_remote: Optional[bool] = None,
        skills_filter: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[Job]:
        db_query = db.query(Job)

        if query:
            q_clean = f"%{query.strip()}%"
            db_query = db_query.filter(
                or_(
                    Job.title.ilike(q_clean),
                    Job.company.ilike(q_clean),
                    Job.description.ilike(q_clean),
                    Job.skills_required.ilike(q_clean)
                )
            )

        if job_type and job_type.lower() != "all":
            db_query = db_query.filter(Job.job_type == job_type.lower())

        if location and location.lower() != "all":
            db_query = db_query.filter(Job.location.ilike(f"%{location.strip()}%"))

        if is_remote is not None:
            db_query = db_query.filter(Job.is_remote == is_remote)

        jobs = db_query.order_by(Job.posted_at.desc()).limit(limit * 2).all()

        # Deduplication logic (Section 5, Agent 2)
        unique_jobs = []
        seen_keys = set()

        for job in jobs:
            # Composite key for deduplication: normalized company + normalized title
            norm_key = f"{job.company.strip().lower()}___{job.title.strip().lower()}"
            if norm_key not in seen_keys:
                seen_keys.add(norm_key)

                # If skills_filter provided, check overlap
                if skills_filter:
                    req_skills = [s.lower() for s in job.get_skills_list()]
                    filter_lower = [f.lower() for f in skills_filter]
                    if not any(f in req_skills or any(f in s for s in req_skills) for f in filter_lower):
                        continue

                unique_jobs.append(job)

            if len(unique_jobs) >= limit:
                break

        return unique_jobs

    @staticmethod
    def get_job_by_id(db: Session, job_id: int) -> Optional[Job]:
        return db.query(Job).filter(Job.job_id == job_id).first()
