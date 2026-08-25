import datetime
from typing import Optional, List
from app.agents.ai_provider import AIProvider
from app.models import User, Job
from app.schemas import CoverLetterResponse

class CoverLetterAgent:
    """
    Cover Letter Agent:
    Generates tailored, highly personalized cover letters based on:
    User Profile + Resume + Job Description
    """

    @staticmethod
    async def generate_cover_letter(
        user: User,
        job: Optional[Job] = None,
        company_name: Optional[str] = None,
        job_title: Optional[str] = None,
        job_description: Optional[str] = None,
        tone: str = "Professional and Enthusiastic",
        key_highlights: Optional[str] = None
    ) -> CoverLetterResponse:
        comp = company_name or (job.company if job else "Hiring Team")
        role = job_title or (job.title if job else "Software Engineer")
        jd = job_description or (job.description if job else "")
        skills = user.get_skills_list()
        user_name = user.name or "Alex Morgan"
        user_edu = user.education or "Computer Science"
        today_str = datetime.date.today().strftime("%B %d, %Y")

        highlights_used = [
            f"Academic foundation in {user_edu}",
            f"Core technical proficiency in {', '.join(skills[:3]) if skills else 'Software Engineering'}",
            f"Hands-on project experience in full-stack and AI development"
        ]

        prompt = f"""
Write a compelling, high-converting cover letter for:
Candidate: {user_name}
Target Company: {comp}
Target Role: {role}
Tone: {tone}
Key Highlights / Candidate Experience:
- Education: {user_edu} (Graduation: {user.graduation_year or '2026'})
- Skills: {', '.join(skills)}
- Experience & Projects: {user.experience or user.projects or 'Full-stack software engineering projects'}
- Extra Notes: {key_highlights or 'Passionate about building scalable solutions.'}

Job Description:
{jd[:1500]}

Format requirements:
- Include formal header with date {today_str}
- 3 to 4 clear, impactful paragraphs
- Connect candidate's specific background to the company's mission and role requirements
- Do not use generic placeholders like [Insert here]; use the actual provided information.
"""

        ai_response = await AIProvider.generate_text(
            prompt=prompt,
            system_prompt=f"You are a top executive recruiter and career strategist. Write a {tone} cover letter."
        )

        if ai_response and len(ai_response.strip()) > 200:
            cover_letter_text = ai_response.strip()
        else:
            # Fallback high quality template
            cover_letter_text = f"""{today_str}

Hiring Manager
{comp}

Dear Hiring Team at {comp},

I am writing to express my strong enthusiasm for the {role} position at {comp}. As a {user_edu} student with a deep passion for building scalable software and intelligent applications, I have developed solid expertise in {', '.join(skills[:3]) if skills else 'Python, Web Development, and Cloud Architectures'}. Having closely followed {comp}'s recent innovations, I am excited about the opportunity to contribute to your engineering initiatives.

Throughout my academic journey and practical project work, I have consistently focused on building reliable, high-performance systems. For instance, I architected full-stack applications with FastAPI and modern web components, streamlining data processing workflows and optimizing backend response times. My experience in {skills[0] if skills else 'Python'} and database management has equipped me with the technical dexterity required to deliver immediate value to your team.

What particularly draws me to {comp} is your commitment to high-quality engineering standards and collaborative culture. I am eager to apply my problem-solving skills, rapid adaptability, and dedication to code quality to help {comp} achieve its strategic goals.

Thank you for your time and consideration. I welcome the opportunity to discuss how my background, technical skill set, and enthusiasm align with the needs of the {role} role.

Sincerely,

{user_name}
{user.email}
"""

        return CoverLetterResponse(
            cover_letter=cover_letter_text,
            company_name=comp,
            job_title=role,
            highlights_used=highlights_used
        )
