import json
import datetime
from sqlalchemy.orm import Session
from app.models import User, Job, Application
from app.auth import get_password_hash

INITIAL_JOBS = [
    {
        "company": "Pythonic AI Labs",
        "title": "Python Developer Intern",
        "description": "Join our AI research team to build backend microservices, data processing pipelines, and integrate LLM APIs into production applications. You will collaborate with senior machine learning engineers to create scalable automated workflows.",
        "skills_required": ["Python", "FastAPI", "SQL", "HTML", "REST APIs", "Git"],
        "education_required": "Bachelor's in Computer Science, IT, or related STEM field",
        "experience_required": "0-1 years / Freshers eligible",
        "location": "Remote / Bengaluru",
        "salary_or_stipend": "$1,200 - $1,800 / month ($15K - $22K / yr)",
        "deadline": "28 Aug 2026",
        "source": "AI Campus Network",
        "job_type": "internship",
        "is_remote": True,
        "company_logo": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=100&auto=format&fit=crop&q=60"
    },
    {
        "company": "NextGen Cloud Systems",
        "title": "Software Engineer Intern",
        "description": "Looking for passionate computer science students to work on distributed cloud backends, database optimizations, and web interfaces. Hands-on experience with modern web stacks, containerization, and automated testing.",
        "skills_required": ["Python", "JavaScript", "SQL", "Docker", "Algorithms", "Git"],
        "education_required": "Bachelor's or Master's in Computer Science or Data Science",
        "experience_required": "Fresher or student in 3rd/4th year",
        "location": "San Francisco, CA / Hybrid",
        "salary_or_stipend": "$35 - $45 / hour",
        "deadline": "05 Sep 2026",
        "source": "TechCareers Global",
        "job_type": "internship",
        "is_remote": False,
        "company_logo": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=100&auto=format&fit=crop&q=60"
    },
    {
        "company": "ABC Technologies",
        "title": "Full Stack AI Engineer (Entry Level)",
        "description": "Build agentic AI web applications connecting LLMs, vector search, and interactive frontends. You will develop both FastAPI/Node backend endpoints and responsive client interfaces.",
        "skills_required": ["Python", "React", "JavaScript", "FastAPI", "PostgreSQL", "TailwindCSS"],
        "education_required": "B.S. / B.Tech in CS or Software Engineering",
        "experience_required": "0-2 years",
        "location": "New York, NY / Remote",
        "salary_or_stipend": "$85,000 - $105,000 / year",
        "deadline": "28 Aug 2026",
        "source": "Direct Partner",
        "job_type": "full-time",
        "is_remote": True,
        "company_logo": "https://images.unsplash.com/photo-1572021335469-31706a17aaef?w=100&auto=format&fit=crop&q=60"
    },
    {
        "company": "DataSphere Analytics",
        "title": "Data Science & ML Intern",
        "description": "Analyze large datasets, develop predictive models, fine-tune open source LLMs, and build automated reporting pipelines. Opportunity to deploy real-world AI pipelines.",
        "skills_required": ["Python", "Pandas", "PyTorch", "SQL", "Scikit-Learn", "Machine Learning"],
        "education_required": "B.S./M.S. in Data Science, CS, or Mathematics",
        "experience_required": "Academic projects or 0-1 years",
        "location": "Austin, TX / Remote",
        "salary_or_stipend": "$1,500 / month stipend",
        "deadline": "12 Sep 2026",
        "source": "DataCareers Portal",
        "job_type": "internship",
        "is_remote": True,
        "company_logo": "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=100&auto=format&fit=crop&q=60"
    },
    {
        "company": "Nexus Web Solutions",
        "title": "Frontend Developer Intern",
        "description": "Develop high performance, responsive user interfaces with HTML5, CSS3, JavaScript, and modern component frameworks. Collaborate with UI/UX designers to implement sleek designs.",
        "skills_required": ["JavaScript", "HTML", "CSS", "React", "UI/UX", "Responsive Design"],
        "education_required": "Any Degree / Self-Taught with strong portfolio",
        "experience_required": "Fresher / Portfolio required",
        "location": "Seattle, WA / Remote",
        "salary_or_stipend": "$1,000 - $1,400 / month",
        "deadline": "18 Sep 2026",
        "source": "FrontendJobs",
        "job_type": "internship",
        "is_remote": True,
        "company_logo": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=100&auto=format&fit=crop&q=60"
    },
    {
        "company": "CyberShield Defense",
        "title": "Junior DevOps & Cloud Engineer",
        "description": "Automate CI/CD workflows, manage containerized microservices in Kubernetes, and monitor application health with modern cloud tools.",
        "skills_required": ["Linux", "Docker", "Kubernetes", "Python", "CI/CD", "AWS"],
        "education_required": "B.Tech / B.E. in Information Technology or CS",
        "experience_required": "0-1 years experience",
        "location": "Boston, MA / Hybrid",
        "salary_or_stipend": "$80,000 - $95,000 / year",
        "deadline": "22 Sep 2026",
        "source": "CloudSec Network",
        "job_type": "full-time",
        "is_remote": False,
        "company_logo": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=100&auto=format&fit=crop&q=60"
    }
]

def seed_database(db: Session):
    # Check if jobs already exist
    job_count = db.query(Job).count()
    if job_count == 0:
        for job_info in INITIAL_JOBS:
            job = Job(
                company=job_info["company"],
                title=job_info["title"],
                description=job_info["description"],
                skills_required=json.dumps(job_info["skills_required"]),
                education_required=job_info["education_required"],
                experience_required=job_info["experience_required"],
                location=job_info["location"],
                salary_or_stipend=job_info["salary_or_stipend"],
                deadline=job_info["deadline"],
                source=job_info["source"],
                job_type=job_info["job_type"],
                is_remote=job_info["is_remote"],
                company_logo=job_info.get("company_logo")
            )
            db.add(job)
        db.commit()

    # Check if demo user exists
    demo_user = db.query(User).filter(User.email == "student@example.com").first()
    if not demo_user:
        demo_user = User(
            name="Alex Morgan",
            email="student@example.com",
            password_hash=get_password_hash("password123"),
            education="B.Tech in Computer Science & Engineering",
            graduation_year=2026,
            skills=json.dumps(["Python", "SQL", "HTML", "CSS", "JavaScript", "FastAPI", "Git", "REST APIs", "Machine Learning"]),
            experience="Software Engineering Intern at University Lab (6 months). Built automated data scraping and RESTful backend services using Python.",
            projects="AI Resume Analyzer: Built full-stack tool using Python and FastAPI.\nE-commerce Web App: Created responsive frontend with HTML/CSS/JS and SQLite backend.",
            preferred_locations=json.dumps(["Remote", "Bengaluru", "San Francisco, CA", "New York, NY"]),
            preferred_roles=json.dumps(["Python Developer", "Software Engineer Intern", "Full Stack Developer", "AI Engineer"]),
            profile_summary="Passionate Computer Science student graduating in 2026 with strong foundations in Python, Backend development, Web technologies, and AI Agent workflows. Quick learner with multiple full-stack projects.",
            resume_text="Alex Morgan\nEmail: student@example.com | GitHub: github.com/alexmorgan\n\nEDUCATION\nB.Tech Computer Science & Engineering (2022 - 2026)\nCGPA: 8.8/10\n\nTECHNICAL SKILLS\nLanguages: Python, JavaScript, SQL, HTML5, CSS3\nFrameworks & Libraries: FastAPI, Flask, Pydantic, SQLAlchemy\nTools & Platforms: Git, GitHub, Docker, Postman, Linux\n\nPROJECTS\n1. AI Job & Resume Analyzer: Developed a FastAPI application parsing resumes and matching job descriptions using NLP keyword extraction.\n2. Cloud Data Pipeline: Designed high throughput ETL pipelines with Python and SQLite.\n\nEXPERIENCE\nSoftware Engineering Intern - Campus Innovation Hub (2025)\n- Developed REST endpoints and reduced database query response times by 35%."
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)

        # Seed initial applications for the demo user matching the dashboard example
        jobs = db.query(Job).all()
        if jobs:
            # 1. Saved / High Match
            app1 = Application(
                user_id=demo_user.user_id,
                job_id=jobs[0].job_id,
                status="saved",
                match_score=94.0,
                notes="Targeting Python Developer Intern role. Resume tailored.",
                applied_date=None
            )
            # 2. Applied
            app2 = Application(
                user_id=demo_user.user_id,
                job_id=jobs[1].job_id,
                status="applied",
                match_score=88.0,
                notes="Applied via company career portal with tailored cover letter.",
                applied_date=datetime.datetime.utcnow() - datetime.timedelta(days=4)
            )
            # 3. Assessment
            if len(jobs) > 2:
                app3 = Application(
                    user_id=demo_user.user_id,
                    job_id=jobs[2].job_id,
                    status="assessment",
                    match_score=82.0,
                    notes="Coding assessment invitation received. Hackerrank test pending.",
                    applied_date=datetime.datetime.utcnow() - datetime.timedelta(days=7)
                )
                db.add(app3)
            # 4. Interview
            if len(jobs) > 3:
                app4 = Application(
                    user_id=demo_user.user_id,
                    job_id=jobs[3].job_id,
                    status="interview",
                    match_score=85.0,
                    notes="Technical Round 1 scheduled for this Friday.",
                    applied_date=datetime.datetime.utcnow() - datetime.timedelta(days=12),
                    interview_date=datetime.datetime.utcnow() + datetime.timedelta(days=3)
                )
                db.add(app4)
            
            db.add(app1)
            db.add(app2)
            db.commit()
