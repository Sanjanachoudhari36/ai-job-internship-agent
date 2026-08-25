import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Workflow, User, Job
from app.schemas import WorkflowCreate, WorkflowUpdate, WorkflowOut, WorkflowRunRequest, WorkflowRunResponse
from app.auth import get_current_user
from app.agents.workflow_engine import WorkflowEngine

router = APIRouter(prefix="/workflows", tags=["AI Workflow Builder"])

DEFAULT_WORKFLOW_TEMPLATES = [
    {
        "name": "Full Auto-Pilot Application Packager",
        "description": "End-to-end autonomous pipeline: searches opportunities, computes 6-factor match, optimizes ATS resume keywords, synthesizes custom cover letter, saves to Kanban and preps mock interview questions.",
        "trigger_type": "manual",
        "icon": "fa-wand-magic-sparkles",
        "nodes": [
            {"id": "node_1", "agent_type": "job_search", "label": "1. Job Scout Agent", "icon": "🔍", "config": {"job_type": "all", "remote_only": False}},
            {"id": "node_2", "agent_type": "matcher", "label": "2. 6-Factor Compatibility Scorer", "icon": "🎯", "config": {}},
            {"id": "node_3", "agent_type": "condition", "label": "3. Match Score Gate", "icon": "🔀", "config": {"min_match_score": 75.0, "halt_on_low_match": False}},
            {"id": "node_4", "agent_type": "resume_ats", "label": "4. Resume ATS Tailor", "icon": "📄", "config": {}},
            {"id": "node_5", "agent_type": "cover_letter", "label": "5. Smart Cover Letter Writer", "icon": "✉️", "config": {"tone": "Professional and Enthusiastic"}},
            {"id": "node_6", "agent_type": "tracker", "label": "6. Pipeline Stage Tracker", "icon": "📊", "config": {"target_stage": "saved"}},
            {"id": "node_7", "agent_type": "interview_prep", "label": "7. Mock Interview Prep Agent", "icon": "🎤", "config": {"question_count": 4}}
        ]
    },
    {
        "name": "Deep Tech ATS Resume & Gap Optimizer",
        "description": "Specialized workflow that scans candidate resume against job requirements, identifies missing critical keywords, and rewrites bullet points with measurable engineering impact metrics.",
        "trigger_type": "manual",
        "icon": "fa-file-lines",
        "nodes": [
            {"id": "node_1", "agent_type": "matcher", "label": "1. Skill Overlap Evaluator", "icon": "🎯", "config": {}},
            {"id": "node_2", "agent_type": "resume_ats", "label": "2. ATS Keyword Enhancer", "icon": "📄", "config": {}},
            {"id": "node_3", "agent_type": "notification", "label": "3. Readiness Alert Dispatcher", "icon": "🔔", "config": {}}
        ]
    },
    {
        "name": "Interview Sprint & Behavioral Simulator",
        "description": "Generates technical architecture, problem-solving and STAR method HR questions tailored specifically to the target company's culture and engineering stack.",
        "trigger_type": "manual",
        "icon": "fa-microphone-lines",
        "nodes": [
            {"id": "node_1", "agent_type": "matcher", "label": "1. Requirement Analysis", "icon": "🎯", "config": {}},
            {"id": "node_2", "agent_type": "interview_prep", "label": "2. High-Yield Question Generator", "icon": "🎤", "config": {"question_count": 5}},
            {"id": "node_3", "agent_type": "tracker", "label": "3. Schedule Tracker Alarm", "icon": "📊", "config": {"target_stage": "interview"}}
        ]
    }
]

@router.get("", response_model=List[WorkflowOut])
def get_workflows(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workflows = db.query(Workflow).filter(Workflow.user_id == user.user_id).all()
    
    # If user has no workflows yet, seed templates
    if not workflows:
        for tpl in DEFAULT_WORKFLOW_TEMPLATES:
            wf = Workflow(
                user_id=user.user_id,
                name=tpl["name"],
                description=tpl["description"],
                trigger_type=tpl["trigger_type"],
                icon=tpl["icon"],
                nodes=json.dumps(tpl["nodes"]),
                is_active=True
            )
            db.add(wf)
        db.commit()
        workflows = db.query(Workflow).filter(Workflow.user_id == user.user_id).all()

    results = []
    for w in workflows:
        results.append({
            "workflow_id": w.workflow_id,
            "user_id": w.user_id,
            "name": w.name,
            "description": w.description,
            "trigger_type": w.trigger_type,
            "nodes": w.get_nodes_list(),
            "icon": w.icon,
            "is_active": w.is_active,
            "created_at": w.created_at,
            "updated_at": w.updated_at
        })
    return results

@router.post("", response_model=WorkflowOut, status_code=status.HTTP_201_CREATED)
def create_workflow(
    payload: WorkflowCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wf = Workflow(
        user_id=user.user_id,
        name=payload.name,
        description=payload.description or "",
        trigger_type=payload.trigger_type or "manual",
        icon=payload.icon or "fa-diagram-project",
        nodes=json.dumps(payload.nodes),
        is_active=payload.is_active if payload.is_active is not None else True
    )
    db.add(wf)
    db.commit()
    db.refresh(wf)

    return {
        "workflow_id": wf.workflow_id,
        "user_id": wf.user_id,
        "name": wf.name,
        "description": wf.description,
        "trigger_type": wf.trigger_type,
        "nodes": wf.get_nodes_list(),
        "icon": wf.icon,
        "is_active": wf.is_active,
        "created_at": wf.created_at,
        "updated_at": wf.updated_at
    }

@router.get("/{workflow_id}", response_model=WorkflowOut)
def get_workflow_by_id(
    workflow_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wf = db.query(Workflow).filter(
        Workflow.workflow_id == workflow_id,
        Workflow.user_id == user.user_id
    ).first()

    if not wf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

    return {
        "workflow_id": wf.workflow_id,
        "user_id": wf.user_id,
        "name": wf.name,
        "description": wf.description,
        "trigger_type": wf.trigger_type,
        "nodes": wf.get_nodes_list(),
        "icon": wf.icon,
        "is_active": wf.is_active,
        "created_at": wf.created_at,
        "updated_at": wf.updated_at
    }

@router.put("/{workflow_id}", response_model=WorkflowOut)
def update_workflow(
    workflow_id: int,
    payload: WorkflowUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wf = db.query(Workflow).filter(
        Workflow.workflow_id == workflow_id,
        Workflow.user_id == user.user_id
    ).first()

    if not wf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

    if payload.name is not None: wf.name = payload.name
    if payload.description is not None: wf.description = payload.description
    if payload.trigger_type is not None: wf.trigger_type = payload.trigger_type
    if payload.icon is not None: wf.icon = payload.icon
    if payload.is_active is not None: wf.is_active = payload.is_active
    if payload.nodes is not None: wf.nodes = json.dumps(payload.nodes)

    db.commit()
    db.refresh(wf)

    return {
        "workflow_id": wf.workflow_id,
        "user_id": wf.user_id,
        "name": wf.name,
        "description": wf.description,
        "trigger_type": wf.trigger_type,
        "nodes": wf.get_nodes_list(),
        "icon": wf.icon,
        "is_active": wf.is_active,
        "created_at": wf.created_at,
        "updated_at": wf.updated_at
    }

@router.delete("/{workflow_id}")
def delete_workflow(
    workflow_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wf = db.query(Workflow).filter(
        Workflow.workflow_id == workflow_id,
        Workflow.user_id == user.user_id
    ).first()

    if not wf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

    db.delete(wf)
    db.commit()
    return {"message": f"Workflow '{wf.name}' deleted successfully."}

@router.post("/{workflow_id}/run", response_model=WorkflowRunResponse)
async def run_workflow(
    workflow_id: int,
    payload: Optional[WorkflowRunRequest] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wf = db.query(Workflow).filter(
        Workflow.workflow_id == workflow_id,
        Workflow.user_id == user.user_id
    ).first()

    if not wf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

    job_id = payload.job_id if payload else None
    overrides = payload.override_params if payload else None

    return await WorkflowEngine.execute_workflow(
        db=db,
        workflow=wf,
        user=user,
        target_job_id=job_id,
        override_params=overrides
    )
