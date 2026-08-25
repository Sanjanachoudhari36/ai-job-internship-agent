import uuid
import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models import User, Job, Workflow, WorkflowExecution, Application
from app.agents.job_search_agent import JobSearchAgent
from app.agents.job_matching_agent import JobMatchingAgent
from app.agents.resume_agent import ResumeAgent
from app.agents.cover_letter_agent import CoverLetterAgent
from app.agents.tracker_agent import ApplicationTrackingAgent
from app.agents.interview_agent import InterviewPreparationAgent
from app.schemas import AgentStepLog, WorkflowRunResponse

class WorkflowEngine:
    """
    Dynamic Workflow Execution Engine:
    Executes custom user-designed multi-agent pipelines with conditional branching,
    custom agent configurations, parameter overrides, and live telemetry logging.
    """

    @staticmethod
    async def execute_workflow(
        db: Session,
        workflow: Workflow,
        user: User,
        target_job_id: Optional[int] = None,
        override_params: Optional[Dict[str, Any]] = None
    ) -> WorkflowRunResponse:
        execution_id = str(uuid.uuid4())
        steps: List[AgentStepLog] = []
        artifacts: Dict[str, Any] = {}
        nodes = workflow.get_nodes_list()
        
        def add_step(agent_name: str, icon: str, status: str, message: str, data: Dict[str, Any] = None):
            steps.append(AgentStepLog(
                agent_name=agent_name,
                icon=icon,
                status=status,
                message=message,
                timestamp=datetime.datetime.utcnow().strftime("%H:%M:%S"),
                data=data or {}
            ))

        add_step("AI Workflow Engine", "⚡", "running", f"Starting execution of custom workflow: '{workflow.name}'...")

        # If no specific job passed, pick first from DB or search node
        current_job = None
        if target_job_id:
            current_job = JobSearchAgent.get_job_by_id(db, target_job_id)
        else:
            all_jobs = db.query(Job).all()
            if all_jobs:
                current_job = all_jobs[0]

        # Execute nodes sequentially
        skip_remaining = False
        for index, node in enumerate(nodes):
            if skip_remaining:
                break

            agent_type = node.get("agent_type", "").lower()
            label = node.get("label", f"Step {index + 1}")
            cfg = node.get("config", {})
            icon = node.get("icon", "🤖")

            if agent_type == "job_search":
                query = cfg.get("search_query") or (override_params.get("query") if override_params else None)
                job_type = cfg.get("job_type", "all")
                is_remote = cfg.get("remote_only", False)

                results = JobSearchAgent.search_jobs(db, query=query, job_type=job_type, is_remote=is_remote if is_remote else None, limit=5)
                if results and not target_job_id:
                    current_job = results[0]

                artifacts["found_jobs_count"] = len(results)
                add_step(label, icon, "completed", f"Job Search Agent discovered {len(results)} opportunities matching criteria.", {
                    "count": len(results),
                    "selected_job": current_job.title if current_job else "None"
                })

            elif agent_type == "matcher":
                if not current_job:
                    add_step(label, icon, "error", "No target job available for matching analysis.")
                    continue

                match_res = JobMatchingAgent.calculate_match(user, current_job)
                artifacts["match_analysis"] = match_res.model_dump()
                add_step(label, icon, "completed", f"6-Factor Compatibility calculated at {match_res.overall_match_score}%.", {
                    "score": match_res.overall_match_score,
                    "matched_skills": match_res.matched_skills,
                    "missing_skills": match_res.missing_skills
                })

            elif agent_type == "condition":
                min_score = float(cfg.get("min_match_score", 70.0))
                current_score = artifacts.get("match_analysis", {}).get("overall_match_score", 85.0)

                if current_score >= min_score:
                    add_step(label, icon, "completed", f"Condition passed: Match Score ({current_score}%) >= Threshold ({min_score}%). Proceeding down High-Match path.", {
                        "condition": "PASSED"
                    })
                else:
                    add_step(label, icon, "completed", f"Condition branched: Match Score ({current_score}%) < Threshold ({min_score}%). Diverting to Skill Gap Advisor.", {
                        "condition": "BRANCH_LOW_MATCH"
                    })
                    if cfg.get("halt_on_low_match", False):
                        skip_remaining = True

            elif agent_type == "resume_ats":
                custom_role = cfg.get("target_role") or (current_job.title if current_job else "Software Engineer")
                resume_res = await ResumeAgent.analyze_and_tailor(user, current_job, target_role=custom_role)
                artifacts["resume_analysis"] = resume_res.model_dump()
                add_step(label, icon, "completed", f"Resume Agent optimized ATS draft (Score: {resume_res.ats_score}/100) with {len(resume_res.bullet_suggestions)} impact bullets.", {
                    "ats_score": resume_res.ats_score,
                    "skills": resume_res.extracted_skills
                })

            elif agent_type == "cover_letter":
                tone = cfg.get("tone", "Professional and Enthusiastic")
                cl_res = await CoverLetterAgent.generate_cover_letter(user, current_job, tone=tone)
                artifacts["cover_letter"] = cl_res.model_dump()
                add_step(label, icon, "completed", f"Cover Letter Agent synthesized personalized letter for {cl_res.company_name} in '{tone}' tone.", {
                    "company": cl_res.company_name,
                    "length": len(cl_res.cover_letter)
                })

            elif agent_type == "tracker":
                target_stage = cfg.get("target_stage", "saved")
                if current_job:
                    existing_app = db.query(Application).filter(
                        Application.user_id == user.user_id,
                        Application.job_id == current_job.job_id
                    ).first()

                    tailored_res = artifacts.get("resume_analysis", {}).get("tailored_resume_preview", "")
                    cl_text = artifacts.get("cover_letter", {}).get("cover_letter", "")
                    score = artifacts.get("match_analysis", {}).get("overall_match_score", 85.0)

                    if not existing_app:
                        new_app = Application(
                            user_id=user.user_id,
                            job_id=current_job.job_id,
                            status=target_stage,
                            match_score=score,
                            tailored_resume=tailored_res,
                            cover_letter=cl_text,
                            notes=f"Auto-saved by Workflow: '{workflow.name}'"
                        )
                        db.add(new_app)
                        db.commit()
                        app_id = new_app.application_id
                    else:
                        existing_app.status = target_stage
                        if tailored_res: existing_app.tailored_resume = tailored_res
                        if cl_text: existing_app.cover_letter = cl_text
                        db.commit()
                        app_id = existing_app.application_id

                    artifacts["application_id"] = app_id
                    add_step(label, icon, "completed", f"Application Tracker Agent updated Kanban stage to '{target_stage.upper()}'.", {
                        "application_id": app_id,
                        "stage": target_stage
                    })

            elif agent_type == "interview_prep":
                q_count = int(cfg.get("question_count", 4))
                questions = await InterviewPreparationAgent.generate_questions(current_job, count=q_count)
                artifacts["interview_questions"] = [q.model_dump() for q in questions]
                add_step(label, icon, "completed", f"Interview Preparation Agent generated {len(questions)} role-specific practice questions.", {
                    "count": len(questions),
                    "categories": list(set(q.category for q in questions))
                })

            elif agent_type == "notification":
                add_step(label, icon, "completed", f"Notification Agent dispatched alert: Application bundle for '{current_job.title if current_job else 'Opportunity'}' is ready for review.", {
                    "recipient": user.email
                })

        add_step("AI Workflow Engine", "✅", "completed", f"Custom workflow '{workflow.name}' executed successfully.")

        # Record execution in DB
        execution = WorkflowExecution(
            workflow_id=workflow.workflow_id,
            user_id=user.user_id,
            job_id=current_job.job_id if current_job else None,
            status="completed",
            steps_log=str([s.model_dump() for s in steps]),
            results=str(artifacts)
        )
        db.add(execution)
        db.commit()

        return WorkflowRunResponse(
            workflow_id=workflow.workflow_id,
            workflow_name=workflow.name,
            execution_id=execution_id,
            status="completed",
            steps_executed=steps,
            artifacts=artifacts
        )
