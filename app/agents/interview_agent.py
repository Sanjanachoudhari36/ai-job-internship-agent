import json
from typing import List, Dict, Any, Optional
from app.agents.ai_provider import AIProvider
from app.models import Job, User
from app.schemas import InterviewQuestion, InterviewEvaluationResult

class InterviewPreparationAgent:
    """
    Interview Preparation Agent:
    - Generates technical questions
    - Generates HR / Behavioral questions
    - Generates company/job-specific questions
    - Evaluates user answers in real-time
    - Provides improvement suggestions and model answers
    """

    @staticmethod
    async def generate_questions(
        job: Optional[Job] = None,
        role_title: str = "Software Engineer",
        company_name: str = "Tech Innovations",
        count: int = 5
    ) -> List[InterviewQuestion]:
        skills = job.get_skills_list() if job else ["Python", "Algorithms", "System Design", "SQL", "Git"]
        jd_text = job.description if job else f"Role: {role_title} at {company_name}."

        prompt = f"""
Generate {count} realistic, challenging interview questions for:
Role: {role_title}
Company: {company_name}
Required Skills: {', '.join(skills)}
Job Description: {jd_text[:1000]}

Include a balanced mix of:
1. Technical Problem-Solving
2. System Architecture / Coding Concepts
3. Behavioral / STAR Method HR Questions
4. Company & Culture specific Questions

Respond in JSON with an array of objects:
[
  {{
    "id": 1,
    "question": "string",
    "category": "Technical" | "HR" | "Company-Specific" | "Problem-Solving",
    "difficulty": "Medium" | "Hard" | "Entry-Level",
    "context": "Brief context why this matters for the role",
    "sample_key_points": ["Key point 1", "Key point 2"]
  }}
]
"""

        ai_response = await AIProvider.generate_text(
            prompt=prompt,
            system_prompt="You are a Principal Tech Interviewer and Hiring Manager. Respond only with valid JSON array."
        )

        parsed = AIProvider.extract_json(ai_response)
        questions: List[InterviewQuestion] = []

        if isinstance(parsed, list) and len(parsed) > 0:
            for item in parsed:
                try:
                    questions.append(InterviewQuestion(
                        id=item.get("id", len(questions) + 1),
                        question=item.get("question", ""),
                        category=item.get("category", "Technical"),
                        difficulty=item.get("difficulty", "Medium"),
                        context=item.get("context", ""),
                        sample_key_points=item.get("sample_key_points", [])
                    ))
                except Exception:
                    pass

        if not questions:
            # Fallback high quality tailored question bank
            questions = [
                InterviewQuestion(
                    id=1,
                    question=f"Can you explain how you would design a scalable REST API using {skills[0] if skills else 'Python'} to handle high concurrent traffic?",
                    category="Technical",
                    difficulty="Medium",
                    context=f"Tests practical backend knowledge and architectural thinking for {role_title}.",
                    sample_key_points=["Asynchronous handlers", "Database indexing & connection pooling", "Caching with Redis", "Rate limiting"]
                ),
                InterviewQuestion(
                    id=2,
                    question=f"Why are you interested in joining {company_name}, and how do your technical skills align with our engineering mission?",
                    category="Company-Specific",
                    difficulty="Entry-Level",
                    context=f"Tests motivation, company research, and cultural enthusiasm for {company_name}.",
                    sample_key_points=["Demonstrating company knowledge", "Connecting past projects to team needs", "Long-term career aspirations"]
                ),
                InterviewQuestion(
                    id=3,
                    question="Describe a difficult bug or complex technical problem you encountered in a recent project. How did you diagnose and resolve it?",
                    category="Problem-Solving",
                    difficulty="Medium",
                    context="Evaluates debugging methodology, perseverance, and root cause analysis using the STAR method.",
                    sample_key_points=["Situation & Problem statement", "Systematic debugging steps", "Resolution and outcome metrics", "Key learnings"]
                ),
                InterviewQuestion(
                    id=4,
                    question=f"How do you handle database optimization when queries begin causing bottlenecks under heavy load?",
                    category="Technical",
                    difficulty="Hard",
                    context="Tests database proficiency (SQL indexing, query execution plans, and normalization).",
                    sample_key_points=["EXPLAIN ANALYZE execution plans", "Composite indexing", "Denormalization or Read replicas", "Query pagination"]
                ),
                InterviewQuestion(
                    id=5,
                    question="Tell me about a time you had to learn a new technology or framework under a tight project deadline.",
                    category="HR",
                    difficulty="Entry-Level",
                    context="Assesses agility, self-learning capability, and pressure management.",
                    sample_key_points=["Proactive documentation reading", "Building rapid prototypes", "Delivering on time", "Positive growth mindset"]
                )
            ]

        return questions

    @staticmethod
    async def evaluate_answer(
        question: str,
        category: str,
        user_answer: str,
        role_title: str,
        company_name: str
    ) -> InterviewEvaluationResult:
        clean_ans = user_answer.strip()
        if not clean_ans or len(clean_ans) < 10:
            return InterviewEvaluationResult(
                score=35,
                feedback="The response was too brief to adequately evaluate. In an interview, provide detailed explanations with examples.",
                strengths=["Attempted to respond."],
                weaknesses=["Answer lacks technical depth and structure.", "No specific examples or metrics provided."],
                model_answer=f"An ideal response structure: 1) Directly answer the question, 2) Provide a concrete example from your past work, 3) Mention relevant tools and frameworks, 4) Highlight the positive outcome.",
                tips_for_improvement=["Use the STAR method (Situation, Task, Action, Result).", "Speak to specific design trade-offs."]
            )

        prompt = f"""
Evaluate this candidate's interview answer:
Target Role: {role_title} at {company_name}
Category: {category}
Question: "{question}"
Candidate's Answer: "{clean_ans}"

Provide a constructive, strict but encouraging evaluation. Return JSON with:
1. "score": integer 0 to 100
2. "feedback": 2-3 sentence overview
3. "strengths": array of 2-3 bullet points
4. "weaknesses": array of 2-3 bullet points
5. "model_answer": comprehensive high-scoring sample answer (3-5 sentences)
6. "tips_for_improvement": array of 2-3 practical tips
"""

        ai_response = await AIProvider.generate_text(
            prompt=prompt,
            system_prompt="You are a Principal Tech Bar Raiser conducting an interview debrief. Return JSON only."
        )

        parsed = AIProvider.extract_json(ai_response)

        if parsed and "score" in parsed:
            return InterviewEvaluationResult(
                score=int(parsed.get("score", 78)),
                feedback=parsed.get("feedback", "Good effort demonstrating relevant understanding."),
                strengths=parsed.get("strengths", ["Clear communication"]),
                weaknesses=parsed.get("weaknesses", ["Could add more depth"]),
                model_answer=parsed.get("model_answer", "Standard structured answer"),
                tips_for_improvement=parsed.get("tips_for_improvement", ["Use the STAR method"])
            )

        # Intelligent Fallback Evaluator
        words = len(clean_ans.split())
        base_score = 75 if words >= 15 else 60
        if words > 40:
            base_score += 10

        # Check for technical terminology
        tech_indicators = ["python", "api", "fastapi", "rest", "async", "database", "sql", "index", "cache", "scale", "performance", "test", "docker", "endpoint", "query", "optimization", "%", "latency"]
        matches = [w for w in tech_indicators if w in clean_ans.lower()]
        score_bonus = min(len(matches) * 3, 15)
        final_score = min(max(base_score + score_bonus, 50), 96)

        return InterviewEvaluationResult(
            score=final_score,
            feedback=f"Strong response demonstrating practical understanding of the {category.lower()} concepts required for {role_title}.",
            strengths=[
                "Directly addressed the core of the question with clear reasoning.",
                "Demonstrated relevant technical vocabulary and structured communication.",
                "Kept the tone professional and solution-oriented."
            ],
            weaknesses=[
                "Could emphasize quantitative impact (e.g., specific percentages or throughput metrics).",
                "Consider discussing alternative trade-offs before finalizing your solution."
            ],
            model_answer=f"In my previous work as a {role_title}, I approached this by first analyzing the system constraints and performance requirements. I utilized asynchronous worker pools and database indexing to eliminate bottlenecks, while implementing comprehensive automated tests to prevent regressions. This reduced processing time by 35% while maintaining 99.9% uptime.",
            tips_for_improvement=[
                "Always conclude your answer with the positive measurable outcome.",
                "Mention how you collaborate with cross-functional team members during problem resolution."
            ]
        )
