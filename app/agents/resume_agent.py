import os
import re
import json
from typing import Dict, Any, List, Optional
from pypdf import PdfReader
import docx
from app.agents.ai_provider import AIProvider
from app.models import User, Job
from app.schemas import ResumeAnalysisResponse

class ResumeAgent:
    """
    Resume Agent:
    - Parses PDF, DOCX, and TXT resumes
    - Extracts skills, education, and experience
    - Analyzes ATS compatibility score against a Job Description
    - Identifies missing keywords
    - Suggests actionable bullet point enhancements
    - Generates a tailored resume draft
    """

    @staticmethod
    def extract_text_from_file(file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        text = ""

        try:
            if ext == ".pdf":
                reader = PdfReader(file_path)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            elif ext in [".docx", ".doc"]:
                doc = docx.Document(file_path)
                for para in doc.paragraphs:
                    if para.text:
                        text += para.text + "\n"
            elif ext in [".txt", ".md"]:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
        except Exception as e:
            print(f"[ResumeAgent] Error extracting text from {file_path}: {e}")

        return text.strip()

    @staticmethod
    def extract_skills_heuristic(text: str) -> List[str]:
        common_tech_skills = [
            "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust", "Ruby", "PHP",
            "HTML", "HTML5", "CSS", "CSS3", "React", "Vue", "Angular", "Next.js", "Node.js", "Express",
            "FastAPI", "Django", "Flask", "Spring Boot", "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis",
            "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Linux", "Git", "GitHub", "CI/CD",
            "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "Pandas", "NumPy", "Scikit-Learn",
            "REST APIs", "GraphQL", "Microservices", "TailwindCSS", "Bootstrap", "Agile", "Scrum"
        ]
        found = []
        text_lower = text.lower()
        for skill in common_tech_skills:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found.append(skill)
        return found

    @staticmethod
    async def analyze_and_tailor(
        user: User,
        job: Optional[Job] = None,
        custom_jd: Optional[str] = None,
        target_role: Optional[str] = None
    ) -> ResumeAnalysisResponse:
        resume_text = user.resume_text or ""
        if not resume_text and user.experience:
            resume_text = f"{user.name}\n{user.education}\nSkills: {', '.join(user.get_skills_list())}\nExperience: {user.experience}\nProjects: {user.projects}"

        jd_text = custom_jd or (job.description if job else "")
        job_skills = job.get_skills_list() if job else []
        role_title = target_role or (job.title if job else "Software Engineer")
        company_name = job.company if job else "Target Company"

        extracted_skills = ResumeAgent.extract_skills_heuristic(resume_text)
        if not extracted_skills and user.get_skills_list():
            extracted_skills = user.get_skills_list()

        # Keyword overlap & ATS computation
        missing_keywords = []
        if job_skills:
            resume_lower = resume_text.lower()
            for s in job_skills:
                if s.lower() not in resume_lower and not any(s.lower() in es.lower() for es in extracted_skills):
                    missing_keywords.append(s)
        else:
            # Check default high impact tech keywords
            for s in ["FastAPI", "Docker", "Unit Testing", "CI/CD", "REST APIs", "Git"]:
                if s.lower() not in resume_text.lower():
                    missing_keywords.append(s)

        matched_count = len(job_skills) - len(missing_keywords) if job_skills else len(extracted_skills)
        total_count = max(len(job_skills), 1)
        base_ats = int((matched_count / total_count) * 45) + (45 if len(resume_text) > 250 else 25)
        ats_score = min(max(base_ats, 40), 96)

        # AI prompt for deep analysis and tailored bullet points
        prompt = f"""
Candidate Name: {user.name}
Target Role: {role_title} at {company_name}
Candidate Education: {user.education}
Candidate Skills: {', '.join(extracted_skills)}
Candidate Resume Content:
{resume_text[:2000]}

Target Job Description:
{jd_text[:1500]}

Analyze this resume against the JD. Return JSON with:
1. "strengths": array of 3 specific strengths
2. "improvements": array of 3 areas needing refinement
3. "bullet_suggestions": array of 3 objects with "original" and "tailored_with_impact"
4. "tailored_resume_preview": clean markdown resume tailored for this role
"""

        ai_response = await AIProvider.generate_text(
            prompt=prompt,
            system_prompt="You are an expert ATS (Applicant Tracking System) and Senior Technical Resume Coach. Respond in JSON format only."
        )
        parsed = AIProvider.extract_json(ai_response)

        if parsed and "strengths" in parsed:
            strengths = parsed.get("strengths", [])
            improvements = parsed.get("improvements", [])
            bullet_suggestions = parsed.get("bullet_suggestions", [])
            tailored_preview = parsed.get("tailored_resume_preview", "")
        else:
            # Fallback heuristic analysis
            strengths = [
                f"Solid educational foundation in {user.education or 'Computer Science / Engineering'}.",
                f"Demonstrated competency in key core skills: {', '.join(extracted_skills[:3]) if extracted_skills else 'Python and Software Development'}.",
                "Clear project-oriented experience with measurable technical outputs."
            ]
            improvements = [
                f"Integrate target role keywords: {', '.join(missing_keywords[:3]) if missing_keywords else 'REST APIs, Docker, and Testing'}.",
                "Quantify achievements using metrics (e.g., 'reduced latency by 30%', 'handled 10k requests').",
                "Ensure action verbs start every bullet point (e.g., 'Architected', 'Spearheaded', 'Optimized')."
            ]
            bullet_suggestions = [
                {
                    "original": "Worked on backend APIs with Python and database.",
                    "tailored_with_impact": f"Designed and deployed 10+ high-throughput RESTful endpoints using Python & FastAPI, improving API response times by 35%."
                },
                {
                    "original": "Created web applications for college and personal projects.",
                    "tailored_with_impact": f"Architected responsive full-stack applications with modern UI and relational databases, supporting 500+ active student users."
                },
                {
                    "original": "Helped team with testing and debugging code.",
                    "tailored_with_impact": f"Implemented automated test suites and CI/CD pipelines, reducing regression defects by 40%."
                }
            ]
            tailored_preview = f"""# {user.name}
**{role_title}** | {user.email} | Portfolio & GitHub

## PROFESSIONAL SUMMARY
Passionate and results-driven {role_title} candidate with proven hands-on experience developing scalable applications using {', '.join(extracted_skills[:4]) if extracted_skills else 'modern technologies'}. Proven ability to build robust features, optimize performance, and collaborate effectively.

## TECHNICAL SKILLS
- **Languages & Frameworks:** {', '.join(extracted_skills) if extracted_skills else 'Python, JavaScript, SQL, HTML, CSS, FastAPI'}
- **Relevant Core Competencies:** {', '.join(job_skills[:5]) if job_skills else 'REST APIs, Cloud Architecture, Git, Docker'}

## RELEVANT PROJECTS
**AI Job & Career Optimization Platform**
- Architected a multi-agent system utilizing FastAPI and intelligent workflow heuristics.
- Integrated automated ATS resume parsing and tailored generation, increasing application throughput by 70%.

**Full-Stack Application Development**
- Developed modular backend services with SQLAlchemy and SQLite/PostgreSQL.
- Implemented real-time interactive user dashboards with sub-100ms response latencies.

## EDUCATION
**{user.education or 'Bachelor of Technology in Computer Science'}** (Graduation: {user.graduation_year or '2026'})
"""

        return ResumeAnalysisResponse(
            ats_score=ats_score,
            extracted_skills=extracted_skills,
            missing_keywords=missing_keywords,
            strengths=strengths,
            improvements=improvements,
            bullet_suggestions=bullet_suggestions,
            tailored_resume_preview=tailored_preview
        )
