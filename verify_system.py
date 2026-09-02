import asyncio
import json
import sys

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.database import engine, Base, IS_MONGODB, get_db
from app.models import User, Job, Application, Workflow
from app.seed_data import seed_database
from app.auth import get_password_hash, verify_password, create_access_token
from app.agents.job_search_agent import JobSearchAgent
from app.agents.job_matching_agent import JobMatchingAgent
from app.agents.resume_agent import ResumeAgent
from app.agents.cover_letter_agent import CoverLetterAgent
from app.agents.tracker_agent import ApplicationTrackingAgent
from app.agents.interview_agent import InterviewPreparationAgent
from app.agents.orchestrator import OrchestratorAgent
from app.agents.workflow_engine import WorkflowEngine
from app.routers.workflow_routes import DEFAULT_WORKFLOW_TEMPLATES

async def run_tests():
    print(f"=== 1. Testing Database ({'MongoDB Atlas' if IS_MONGODB else 'SQL'}) & Seeding ===")
    if not IS_MONGODB and engine:
        Base.metadata.create_all(bind=engine)
        
    db_gen = get_db()
    db = next(db_gen)
    seed_database(db)
    
    user = db.query(User).filter(User.email == "student@example.com").first()
    assert user is not None, "Demo candidate user should exist"
    print(f"  [+] Found demo candidate: {user.name} ({user.email})")

    jobs = db.query(Job).all()
    assert len(jobs) >= 5, "Database should have seeded initial opportunities"
    print(f"  [+] Found {len(jobs)} seeded opportunities.")

    print("\n=== 2. Testing Auth & Security ===")
    hashed = get_password_hash("testpass")
    assert verify_password("testpass", hashed), "Password verification failed"
    token = create_access_token({"sub": user.email, "user_id": user.user_id})
    assert len(token) > 20, "JWT token generation failed"
    print("  [+] Direct bcrypt password hashing & JWT generation verified.")

    print("\n=== 3. Testing 6-Factor Compatibility Scorer (Spec Sec 8) ===")
    target_job = jobs[0]
    match_res = JobMatchingAgent.calculate_match(user, target_job)
    print(f"  [+] Job: {target_job.title} at {target_job.company}")
    print(f"  [+] Overall Match Score: {match_res.overall_match_score}%")
    print(f"  [+] Skill Match (40%): {match_res.skill_score}%, Education (15%): {match_res.education_score}%")
    print(f"  [+] Matched Skills: {match_res.matched_skills}")
    assert match_res.overall_match_score >= 80.0, "Python Developer Intern should have high match for demo student"

    print("\n=== 4. Testing Resume Agent (ATS & Tailoring) ===")
    resume_res = await ResumeAgent.analyze_and_tailor(user, target_job)
    print(f"  [+] ATS Compatibility Score: {resume_res.ats_score}/100")
    print(f"  [+] Extracted Skills: {resume_res.extracted_skills[:4]}")
    print(f"  [+] Bullet Suggestion Sample: {resume_res.bullet_suggestions[0]['tailored_with_impact']}")
    assert resume_res.ats_score > 0, "ATS score should be computed"
    assert len(resume_res.bullet_suggestions) > 0, "Bullet suggestions should be generated"

    print("\n=== 5. Testing Cover Letter Agent ===")
    cl_res = await CoverLetterAgent.generate_cover_letter(user, target_job, tone="Professional and Enthusiastic")
    print(f"  [+] Cover letter synthesized for: {cl_res.company_name} ({cl_res.job_title})")
    print(f"  [+] Character length: {len(cl_res.cover_letter)}")
    assert len(cl_res.cover_letter) > 200, "Cover letter should have substantial length"

    print("\n=== 6. Testing Kanban Tracker Agent ===")
    summary = ApplicationTrackingAgent.get_pipeline_summary(db, user.user_id)
    print(f"  [+] Total applications tracked: {summary['total_applications']}")
    print(f"  [+] Stages breakdown: {summary['stages_breakdown']}")
    assert summary['total_applications'] > 0, "Seeded applications should be present"

    print("\n=== 7. Testing Interview Agent ===")
    questions = await InterviewPreparationAgent.generate_questions(target_job, count=3)
    print(f"  [+] Generated {len(questions)} interview questions.")
    print(f"  [+] Sample Question 1: {questions[0].question}")
    eval_res = await InterviewPreparationAgent.evaluate_answer(
        question=questions[0].question,
        category=questions[0].category,
        user_answer="I designed REST APIs using Python and FastAPI with asynchronous endpoints and database indexing, which improved performance by 35%.",
        role_title=target_job.title,
        company_name=target_job.company
    )
    print(f"  [+] Mock Answer Score: {eval_res.score}/100")
    print(f"  [+] Feedback: {eval_res.feedback}")
    assert eval_res.score >= 70, "Relevant technical answer should score >= 70"

    print("\n=== 8. Testing 7-Agent Multi-Agent Orchestrator Pipeline ===")
    orch_res = await OrchestratorAgent.run_full_pipeline(db, user, target_job.job_id)
    print(f"  [+] Orchestrator Status: {orch_res.overall_status}")
    print(f"  [+] Steps executed: {len(orch_res.steps)}")
    for step in orch_res.steps:
        print(f"      [{step.agent_name}]: {step.message}")
    assert orch_res.overall_status == "completed", "Orchestrator pipeline should complete successfully"
    assert len(orch_res.steps) >= 7, "All pipeline stages should be executed and logged"

    print("\n=== 9. Testing Dynamic AI Workflow Engine (7-Node Custom Pipeline) ===")
    test_template = DEFAULT_WORKFLOW_TEMPLATES[0]  # Full Auto-Pilot Application Packager
    custom_wf = Workflow(
        user_id=user.user_id,
        name=test_template["name"],
        description=test_template["description"],
        trigger_type=test_template["trigger_type"],
        icon=test_template["icon"],
        nodes=json.dumps(test_template["nodes"]),
        is_active=True
    )
    db.add(custom_wf)
    db.commit()
    db.refresh(custom_wf)

    wf_res = await WorkflowEngine.execute_workflow(
        db=db,
        workflow=custom_wf,
        user=user,
        target_job_id=target_job.job_id
    )
    print(f"  [+] Workflow Run Status: {wf_res.status}")
    print(f"  [+] Total Nodes Executed: {len(wf_res.steps_executed)}")
    for s in wf_res.steps_executed:
        print(f"      [{s.agent_name}]: {s.message}")
    assert wf_res.status == "completed", "Dynamic workflow should complete successfully"
    assert len(wf_res.steps_executed) >= 7, "All workflow nodes should execute"
    assert "artifacts" in wf_res.model_dump(), "Artifacts should be collected"

    try:
        db_gen.close()
    except Exception:
        pass
    print("\n🎉 ALL 9 AUTOMATED VERIFICATION SUITES (7 PIPELINE & AI WORKFLOW ENGINE) PASSED PERFECTLY! 🎉\n")

if __name__ == "__main__":
    asyncio.run(run_tests())
