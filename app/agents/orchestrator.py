import uuid
import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models import User, Job, Application
from app.agents.job_search_agent import JobSearchAgent
from app.agents.job_matching_agent import JobMatchingAgent
from app.agents.resume_agent import ResumeAgent
from app.agents.cover_letter_agent import CoverLetterAgent
from app.agents.tracker_agent import ApplicationTrackingAgent
from app.agents.interview_agent import InterviewPreparationAgent
from app.schemas import OrchestratorRunResponse, AgentStepLog

class OrchestratorAgent:
    """
    Orchestrator Agent:
    The central coordinator that manages and synchronizes the multi-agent workflow:
    1. AI Profile & Discovery -> 2. Job Search Agent -> 3. Job Matching Agent ->
    4. Resume Agent (ATS & Tailoring) -> 5. Cover Letter Agent ->
    6. Application Tracker (Saved/Applied) -> 7. Interview Preparation Agent
    """

    @staticmethod
    async def run_full_pipeline(
        db: Session,
        user: User,
        job_id: int,
        include_cover_letter: bool = True,
        include_resume_tailoring: bool = True,
        include_interview_prep: bool = True
    ) -> OrchestratorRunResponse:
        session_id = str(uuid.uuid4())
        steps: List[AgentStepLog] = []
        results: Dict[str, Any] = {}

        def add_step(agent_name: str, icon: str, status: str, message: str, data: Dict[str, Any] = None):
            steps.append(AgentStepLog(
                agent_name=agent_name,
                icon=icon,
                status=status,
                message=message,
                timestamp=datetime.datetime.utcnow().strftime("%H:%M:%S"),
                data=data or {}
            ))

        # 1. Orchestrator Initialization
        add_step("Orchestrator Agent", "🤖", "running", f"Initiating career optimization pipeline for {user.name}...")

        job = JobSearchAgent.get_job_by_id(db, job_id)
        if not job:
            add_step("Orchestrator Agent", "❌", "error", f"Job ID {job_id} not found in database.")
            return OrchestratorRunResponse(
                session_id=session_id,
                overall_status="failed",
                steps=steps,
                results={"error": "Job not found"}
            )

        # 2. Job Search & Extraction Step
        add_step("Job Search Agent", "🔍", "completed", f"Analyzed opportunity: '{job.title}' at {job.company}.", {
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "deadline": job.deadline,
            "skills": job.get_skills_list()
        })

        # 3. Job Matching Agent Step
        match_breakdown = JobMatchingAgent.calculate_match(user, job)
        results["match_analysis"] = match_breakdown.model_dump()
        add_step("Job Matching Agent", "🎯", "completed", f"Computed Compatibility Score: {match_breakdown.overall_match_score}%.", {
            "score": match_breakdown.overall_match_score,
            "matched_skills": match_breakdown.matched_skills,
            "missing_skills": match_breakdown.missing_skills,
            "fit_summary": match_breakdown.fit_summary
        })

        # Branching logic based on Match Score (Section 6)
        if match_breakdown.overall_match_score < 40.0:
            add_step("Skill Gap Advisor", "💡", "completed", "Low Match detected. Generated targeted skill acquisition roadmap.", {
                "recommended_skills_to_learn": match_breakdown.missing_skills
            })

        # 4. Resume Agent Step (ATS & Tailoring)
        tailored_resume_text = ""
        if include_resume_tailoring:
            add_step("Resume Agent", "📄", "running", "Evaluating ATS compatibility and optimizing resume bullet points...")
            resume_analysis = await ResumeAgent.analyze_and_tailor(user, job)
            results["resume_analysis"] = resume_analysis.model_dump()
            tailored_resume_text = resume_analysis.tailored_resume_preview
            add_step("Resume Agent", "📄", "completed", f"ATS Compatibility calculated at {resume_analysis.ats_score}/100. Tailored draft prepared.", {
                "ats_score": resume_analysis.ats_score,
                "missing_keywords": resume_analysis.missing_keywords,
                "improvements_count": len(resume_analysis.improvements)
            })

        # 5. Cover Letter Agent Step
        cover_letter_text = ""
        if include_cover_letter:
            add_step("Cover Letter Agent", "✉️", "running", "Synthesizing candidate background with company requirements...")
            cl_response = await CoverLetterAgent.generate_cover_letter(user, job)
            results["cover_letter"] = cl_response.model_dump()
            cover_letter_text = cl_response.cover_letter
            add_step("Cover Letter Agent", "✉️", "completed", f"Personalized cover letter synthesized for {job.company}.", {
                "length": len(cover_letter_text),
                "highlights": cl_response.highlights_used
            })

        # 6. Application Tracking Agent Step
        existing_app = db.query(Application).filter(
            Application.user_id == user.user_id,
            Application.job_id == job.job_id
        ).first()

        if not existing_app:
            new_app = Application(
                user_id=user.user_id,
                job_id=job.job_id,
                status="saved",
                match_score=match_breakdown.overall_match_score,
                tailored_resume=tailored_resume_text,
                cover_letter=cover_letter_text,
                notes=f"Processed via Orchestrator. Match Score: {match_breakdown.overall_match_score}%."
            )
            db.add(new_app)
            db.commit()
            db.refresh(new_app)
            app_id = new_app.application_id
            add_step("Application Tracking Agent", "📊", "completed", "Opportunity auto-saved in Application Kanban pipeline.", {
                "application_id": app_id,
                "status": "saved"
            })
        else:
            if tailored_resume_text:
                existing_app.tailored_resume = tailored_resume_text
            if cover_letter_text:
                existing_app.cover_letter = cover_letter_text
            existing_app.match_score = match_breakdown.overall_match_score
            db.commit()
            add_step("Application Tracking Agent", "📊", "completed", f"Updated existing application (Status: {existing_app.status}).", {
                "application_id": existing_app.application_id,
                "status": existing_app.status
            })

        # 7. Interview Preparation Agent Step
        if include_interview_prep:
            add_step("Interview Preparation Agent", "🎤", "running", "Generating technical, HR & company-specific interview question set...")
            questions = await InterviewPreparationAgent.generate_questions(job, job.title, job.company, count=4)
            results["interview_questions"] = [q.model_dump() for q in questions]
            add_step("Interview Preparation Agent", "🎤", "completed", f"Generated {len(questions)} mock interview questions with assessment rubrics.", {
                "question_count": len(questions),
                "categories": list(set(q.category for q in questions))
            })

        # Orchestrator Wrap-up
        add_step("Orchestrator Agent", "✅", "completed", "All 7 agent workflows executed successfully. Application bundle is ready for review.", {
            "summary": f"Bundle prepared for {job.title} at {job.company} (Match: {match_breakdown.overall_match_score}%)"
        })

        return OrchestratorRunResponse(
            session_id=session_id,
            overall_status="completed",
            steps=steps,
            results=results
        )
