import json
import re
from typing import Dict, Any, List, Tuple
from app.models import User, Job
from app.schemas import MatchScoreBreakdown

class JobMatchingAgent:
    """
    Job Matching Agent:
    Implements the 6-factor weighted scoring model defined in Section 8 of the spec:
      - Skill Match: 40%
      - Education Match: 15%
      - Experience Match: 15%
      - Project Match: 15%
      - Location Match: 5%
      - Other Criteria: 10%
    """

    @staticmethod
    def calculate_match(user: User, job: Job) -> MatchScoreBreakdown:
        user_skills = [s.strip().lower() for s in user.get_skills_list()]
        job_skills = [s.strip().lower() for s in job.get_skills_list()]
        
        # 1. Skill Match (Weight: 40%)
        matched_skills_orig = []
        missing_skills_orig = []
        raw_job_skills_orig = job.get_skills_list()
        
        if not raw_job_skills_orig:
            skill_score = 80.0
        else:
            matched_count = 0
            for orig_skill in raw_job_skills_orig:
                skill_clean = orig_skill.strip().lower()
                # Check direct or substring match with user skills, resume, or projects
                is_matched = False
                for u_skill in user_skills:
                    if skill_clean == u_skill or skill_clean in u_skill or u_skill in skill_clean:
                        is_matched = True
                        break
                
                # Check resume text if not directly in skills list
                if not is_matched and user.resume_text:
                    if re.search(r'\b' + re.escape(skill_clean) + r'\b', user.resume_text.lower()):
                        is_matched = True

                if is_matched:
                    matched_count += 1
                    matched_skills_orig.append(orig_skill)
                else:
                    missing_skills_orig.append(orig_skill)

            skill_score = (matched_count / len(raw_job_skills_orig)) * 100.0 if raw_job_skills_orig else 100.0

        # 2. Education Match (Weight: 15%)
        education_score = 70.0  # Base passing score
        edu_status = "Satisfied"
        user_edu = (user.education or "").lower()
        job_edu = (job.education_required or "").lower()

        if any(term in user_edu for term in ["b.tech", "btech", "bachelor", "b.e", "b.s", "computer", "cs", "it", "data", "engineering", "m.tech", "master"]):
            education_score = 95.0
            edu_status = "Satisfied (Strong STEM / CS Background)"
        elif not user_edu:
            education_score = 50.0
            edu_status = "Profile education details incomplete"
        else:
            education_score = 80.0
            edu_status = "Eligible"

        # 3. Experience Match (Weight: 15%)
        exp_score = 75.0
        exp_status = "Satisfied"
        user_exp = (user.experience or "").lower()
        job_exp = (job.experience_required or "").lower()

        is_intern_job = "intern" in job.title.lower() or job.job_type == "internship" or "fresher" in job_exp or "0-" in job_exp or "0 to" in job_exp

        if is_intern_job:
            exp_score = 95.0
            exp_status = "Satisfied (Entry / Internship Level)"
        elif user_exp and len(user_exp) > 30:
            exp_score = 90.0
            exp_status = "Satisfied (Relevant prior project / internship experience)"
        else:
            exp_score = 70.0
            exp_status = "Acceptable (Entry level profile)"

        # 4. Project Match (Weight: 15%)
        project_score = 60.0
        user_projects = (user.projects or "").lower()
        
        if user_projects:
            # Check overlap between project keywords and job skills
            overlap_count = 0
            for skill in job_skills:
                if skill in user_projects:
                    overlap_count += 1
            
            if overlap_count >= 2:
                project_score = 95.0
            elif overlap_count == 1 or len(user_projects) > 50:
                project_score = 85.0
            else:
                project_score = 75.0
        elif user.resume_text and len(user.resume_text) > 100:
            project_score = 80.0
        else:
            project_score = 50.0

        # 5. Location Match (Weight: 5%)
        loc_score = 70.0
        user_locs = [l.lower() for l in user.get_preferred_locations_list()]
        job_loc = (job.location or "").lower()

        if job.is_remote or "remote" in job_loc:
            loc_score = 100.0
        elif any(uloc in job_loc or job_loc in uloc for uloc in user_locs):
            loc_score = 100.0
        elif not user_locs:
            loc_score = 85.0
        else:
            loc_score = 60.0

        # 6. Other Criteria / Role Alignment (Weight: 10%)
        other_score = 80.0
        user_roles = [r.lower() for r in user.get_preferred_roles_list()]
        job_title_lower = job.title.lower()

        if any(r in job_title_lower or job_title_lower in r for r in user_roles):
            other_score = 98.0
        elif not user_roles:
            other_score = 80.0
        else:
            other_score = 70.0

        # Weighted Total (Section 8 Formula)
        overall = (
            (skill_score * 0.40) +
            (education_score * 0.15) +
            (exp_score * 0.15) +
            (project_score * 0.15) +
            (loc_score * 0.05) +
            (other_score * 0.10)
        )
        overall = round(min(max(overall, 15.0), 99.0), 1)

        # Generate Actionable Recommendations
        recommendations = []
        if missing_skills_orig:
            recommendations.append(f"Consider learning or highlighting familiarity with: {', '.join(missing_skills_orig[:3])}.")
        if skill_score >= 80:
            recommendations.append("Strong technical alignment. Emphasize your key projects in the cover letter.")
        if project_score < 75:
            recommendations.append("Add detailed bullet points with measurable impact for your portfolio projects.")
        if loc_score == 100 and job.is_remote:
            recommendations.append("100% remote opportunity compatible with your location preferences.")

        fit_summary = f"{'High' if overall >= 80 else 'Moderate' if overall >= 65 else 'Potential'} Match ({overall}%). "
        if matched_skills_orig:
            fit_summary += f"Strong match in {', '.join(matched_skills_orig[:4])}. "
        if missing_skills_orig:
            fit_summary += f"Missing: {', '.join(missing_skills_orig[:3])}. "
        fit_summary += f"Experience: {exp_status}."

        return MatchScoreBreakdown(
            skill_score=round(skill_score, 1),
            education_score=round(education_score, 1),
            experience_score=round(exp_score, 1),
            project_score=round(project_score, 1),
            location_score=round(loc_score, 1),
            other_score=round(other_score, 1),
            overall_match_score=overall,
            matched_skills=matched_skills_orig,
            missing_skills=missing_skills_orig,
            experience_status=exp_status,
            education_status=edu_status,
            recommendations=recommendations,
            fit_summary=fit_summary
        )
