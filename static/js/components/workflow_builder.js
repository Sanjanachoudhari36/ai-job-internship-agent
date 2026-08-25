/**
 * AI Workflow Builder Component - Create, Customize & Execute Autonomous Agent Pipelines
 */
const WorkflowBuilderView = {
  workflows: [],
  currentWorkflow: null,
  isEditing: false,
  availableAgents: [
    { type: 'job_search', name: 'Job Scout Agent', icon: '🔍', color: '#22d3ee', description: 'Discovers & deduplicates opportunities from target criteria' },
    { type: 'matcher', name: '6-Factor Compatibility Scorer', icon: '🎯', color: '#34d399', description: 'Calculates weighted candidate-job fit score (0-100%)' },
    { type: 'condition', name: 'Conditional Decision Gate', icon: '🔀', color: '#fbbf24', description: 'Branch logic: If Match >= X% continue, else skill gap roadmap' },
    { type: 'resume_ats', name: 'Resume ATS Optimizer', icon: '📄', color: '#818cf8', description: 'ATS keyword injection & impact-driven bullet tailoring' },
    { type: 'cover_letter', name: 'Cover Letter Synthesizer', icon: '✉️', color: '#e879f9', description: 'Personalized cover letter generation with customizable tone' },
    { type: 'tracker', name: 'Kanban Pipeline Tracker', icon: '📊', color: '#38bdf8', description: 'Auto-saves or transitions application to target stage' },
    { type: 'interview_prep', name: 'Interview Question Generator', icon: '🎤', color: '#f43f5e', description: 'Tailored technical & behavioral mock question bank' },
    { type: 'notification', name: 'Alert Dispatcher', icon: '🔔', color: '#a3e635', description: 'Dispatches readiness alerts and milestone notifications' }
  ],

  async render(container) {
    container.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:24px; flex-wrap:wrap; gap:16px;">
        <div>
          <h3 style="font-size:1.15rem; font-weight:700; color:#ffffff; display:flex; align-items:center; gap:8px;">
            <i class="fa-solid fa-wand-magic-sparkles" style="color:#d946ef;"></i> AI Workflow Builder
          </h3>
          <p style="font-size:0.82rem; color:var(--text-muted);">
            Design, customize, and orchestrate automated multi-agent career pipelines with visual drag-and-drop nodes.
          </p>
        </div>

        <div style="display:flex; gap:10px;">
          <button class="btn btn-secondary btn-sm" id="btn-refresh-workflows">
            <i class="fa-solid fa-arrows-rotate"></i> Refresh
          </button>
          <button class="btn btn-primary btn-sm" id="btn-create-new-workflow">
            <i class="fa-solid fa-plus"></i> Create Workflow
          </button>
        </div>
      </div>

      <!-- Main Grid: Workflow Library + Visual Flow Canvas -->
      <div style="display:grid; grid-template-columns: 1fr 2fr; gap:24px;">
        <!-- Left Column: Workflow Library & Preset Templates -->
        <div style="display:flex; flex-direction:column; gap:20px;">
          <div class="glass-card">
            <div class="card-header">
              <h4 class="card-title" style="font-size:0.95rem;"><i class="fa-solid fa-layer-group" style="color:#818cf8;"></i> My Agent Workflows</h4>
              <span id="workflow-count-badge" class="badge badge-score">0 Active</span>
            </div>

            <div id="workflow-list-container" style="display:flex; flex-direction:column; gap:10px; max-height:550px; overflow-y:auto;">
              <div style="display:flex; justify-content:center; padding:30px;">
                <i class="fa-solid fa-circle-notch fa-spin" style="color:#6366f1;"></i>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Visual Canvas & Execution Runner -->
        <div id="workflow-canvas-container">
          <div class="glass-card" style="text-align:center; padding:60px 24px; min-height:500px; display:flex; flex-direction:column; align-items:center; justify-content:center;">
            <i class="fa-solid fa-diagram-project fa-3x" style="color:var(--text-muted); margin-bottom:16px;"></i>
            <h3 style="font-size:1.15rem;">Select or Create an Agent Workflow</h3>
            <p style="font-size:0.85rem; color:var(--text-muted); max-width:400px; margin-top:8px;">
              Choose an existing workflow from the library on the left or click 'Create Workflow' to design a custom multi-agent pipeline.
            </p>
          </div>
        </div>
      </div>
    `;

    this.setupEvents(container);
    await this.loadWorkflows();
  },

  setupEvents(container) {
    container.querySelector('#btn-refresh-workflows').addEventListener('click', () => {
      this.loadWorkflows();
    });

    container.querySelector('#btn-create-new-workflow').addEventListener('click', () => {
      this.openWorkflowCreator();
    });
  },

  async loadWorkflows() {
    const listContainer = document.getElementById('workflow-list-container');
    if (!listContainer) return;

    try {
      this.workflows = await API.getWorkflows();
      const countBadge = document.getElementById('workflow-count-badge');
      if (countBadge) countBadge.textContent = `${this.workflows.length} Active`;

      if (this.workflows.length === 0) {
        listContainer.innerHTML = `
          <div style="text-align:center; padding:20px; color:var(--text-muted); font-size:0.85rem;">
            No workflows yet. Click 'Create Workflow' above.
          </div>
        `;
        return;
      }

      listContainer.innerHTML = this.workflows.map(wf => {
        const isSelected = this.currentWorkflow && this.currentWorkflow.workflow_id === wf.workflow_id;
        const nodeCount = (wf.nodes || []).length;

        return `
          <div style="background:${isSelected ? 'rgba(99,102,241,0.18)' : 'rgba(30,41,59,0.6)'}; border:1px solid ${isSelected ? 'rgba(99,102,241,0.5)' : 'var(--border-glass)'}; border-radius:var(--radius-md); padding:14px; cursor:pointer; transition:var(--transition);" onclick="WorkflowBuilderView.selectWorkflow(${wf.workflow_id})">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:6px;">
              <div style="font-weight:700; font-size:0.92rem; color:#ffffff; display:flex; align-items:center; gap:8px;">
                <i class="fa-solid ${wf.icon || 'fa-diagram-project'}" style="color:#818cf8;"></i>
                <span>${wf.name}</span>
              </div>
              <span class="badge" style="background:rgba(255,255,255,0.06); font-size:0.7rem;">${nodeCount} Nodes</span>
            </div>

            <p style="font-size:0.78rem; color:var(--text-muted); line-height:1.4; margin-bottom:10px; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;">
              ${wf.description || 'Custom multi-agent automated workflow.'}
            </p>

            <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--border-glass); padding-top:8px;">
              <span style="font-size:0.72rem; color:var(--accent-emerald);">
                <i class="fa-solid fa-bolt"></i> Trigger: ${wf.trigger_type || 'manual'}
              </span>
              <div style="display:flex; gap:6px;">
                <button class="btn btn-primary btn-sm" style="padding:3px 8px; font-size:0.75rem;" onclick="event.stopPropagation(); WorkflowBuilderView.quickRunWorkflow(${wf.workflow_id})">
                  <i class="fa-solid fa-play"></i> Run
                </button>
                <button class="btn-icon" style="padding:4px; font-size:0.75rem; color:#f43f5e;" onclick="event.stopPropagation(); WorkflowBuilderView.deleteWorkflowItem(${wf.workflow_id})" title="Delete Workflow">
                  <i class="fa-solid fa-trash-can"></i>
                </button>
              </div>
            </div>
          </div>
        `;
      }).join('');

      // Auto-select first if none selected
      if (!this.currentWorkflow && this.workflows.length > 0) {
        this.selectWorkflow(this.workflows[0].workflow_id);
      }
    } catch (err) {
      listContainer.innerHTML = `<div style="color:#f43f5e; font-size:0.85rem; padding:10px;">Error loading workflows: ${err.message}</div>`;
    }
  },

  selectWorkflow(workflowId) {
    this.currentWorkflow = this.workflows.find(w => w.workflow_id === workflowId);
    if (!this.currentWorkflow) return;

    this.renderCanvas();
    this.loadWorkflows(); // Refresh active styling
  },

  renderCanvas() {
    const canvas = document.getElementById('workflow-canvas-container');
    const wf = this.currentWorkflow;
    if (!canvas || !wf) return;

    const nodes = wf.nodes || [];

    canvas.innerHTML = `
      <div style="display:flex; flex-direction:column; gap:20px;">
        <!-- Canvas Header & Actions -->
        <div class="glass-card">
          <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:16px;">
            <div>
              <div style="display:flex; align-items:center; gap:10px;">
                <h3 style="font-size:1.25rem; font-weight:800; color:#ffffff;">${wf.name}</h3>
                <span class="badge badge-score high">Active Workflow</span>
              </div>
              <p style="font-size:0.84rem; color:var(--text-secondary); margin-top:4px;">
                ${wf.description}
              </p>
            </div>

            <div style="display:flex; gap:10px;">
              <button class="btn btn-secondary btn-sm" onclick="WorkflowBuilderView.openAddNodeModal()">
                <i class="fa-solid fa-plus"></i> Add Agent Node
              </button>
              <button class="btn btn-secondary btn-sm" onclick="WorkflowBuilderView.editWorkflowMeta()">
                <i class="fa-solid fa-gear"></i> Settings
              </button>
              <button class="btn btn-primary btn-sm" id="btn-execute-canvas-workflow">
                <i class="fa-solid fa-play"></i> Execute Pipeline
              </button>
            </div>
          </div>
        </div>

        <!-- Visual Node Pipeline Sequence -->
        <div class="glass-card" style="position:relative;">
          <div class="card-header" style="margin-bottom:16px;">
            <h4 class="card-title" style="font-size:0.95rem;">
              <i class="fa-solid fa-bezier-curve" style="color:#06b6d4;"></i> Visual Agent Pipeline Graph (${nodes.length} Stages)
            </h4>
          </div>

          <div id="nodes-flow-container" style="display:flex; flex-direction:column; gap:14px; position:relative;">
            ${nodes.map((node, idx) => `
              <div class="workflow-node-card" style="background:rgba(15,23,42,0.8); border:1px solid var(--border-glass); border-radius:var(--radius-md); padding:16px; display:flex; align-items:center; justify-content:space-between; transition:var(--transition); position:relative;" onmouseover="this.style.borderColor='rgba(99,102,241,0.5)'" onmouseout="this.style.borderColor='var(--border-glass)'">
                <div style="display:flex; align-items:center; gap:14px;">
                  <div style="width:42px; height:42px; border-radius:var(--radius-md); background:rgba(99,102,241,0.15); display:flex; align-items:center; justify-content:center; font-size:1.3rem;">
                    ${node.icon || '🤖'}
                  </div>
                  <div>
                    <div style="font-weight:700; font-size:0.92rem; color:#ffffff;">${node.label || `Step ${idx+1}`}</div>
                    <div style="font-size:0.78rem; color:var(--text-muted);">
                      Agent Type: <strong style="color:#818cf8;">${node.agent_type}</strong>
                      ${node.config && Object.keys(node.config).length > 0 ? ` • Config: ${JSON.stringify(node.config)}` : ''}
                    </div>
                  </div>
                </div>

                <div style="display:flex; align-items:center; gap:8px;">
                  ${idx > 0 ? `<button class="btn-icon" onclick="WorkflowBuilderView.moveNode(${idx}, -1)" title="Move Up"><i class="fa-solid fa-arrow-up"></i></button>` : ''}
                  ${idx < nodes.length - 1 ? `<button class="btn-icon" onclick="WorkflowBuilderView.moveNode(${idx}, 1)" title="Move Down"><i class="fa-solid fa-arrow-down"></i></button>` : ''}
                  <button class="btn-icon" style="color:#f43f5e;" onclick="WorkflowBuilderView.removeNode(${idx})" title="Remove Node"><i class="fa-solid fa-trash"></i></button>
                </div>
              </div>

              ${idx < nodes.length - 1 ? `
                <div style="display:flex; justify-content:center; align-items:center; height:18px;">
                  <i class="fa-solid fa-arrow-down" style="color:rgba(99,102,241,0.6); font-size:0.85rem;"></i>
                </div>
              ` : ''}
            `).join('')}
          </div>
        </div>

        <!-- Live Execution Output Area -->
        <div id="workflow-run-results-box"></div>
      </div>
    `;

    document.getElementById('btn-execute-canvas-workflow').addEventListener('click', () => {
      this.executeActiveWorkflow();
    });
  },

  openWorkflowCreator() {
    const content = `
      <div style="display:flex; flex-direction:column; gap:16px;">
        <div class="form-group">
          <label class="form-label">Workflow Name:</label>
          <input type="text" id="new-wf-name" class="input-field" placeholder="e.g., Autonomous Tech Scout & ATS Applier">
        </div>
        <div class="form-group">
          <label class="form-label">Description / Purpose:</label>
          <textarea id="new-wf-desc" class="input-field" rows="2" placeholder="Briefly describe what this agent workflow automates..."></textarea>
        </div>
        <div class="form-group">
          <label class="form-label">Trigger Type:</label>
          <select id="new-wf-trigger" class="input-field">
            <option value="manual">Manual 1-Click Trigger</option>
            <option value="on_new_job">On New Matching Job Discovered</option>
            <option value="on_save_job">On Opportunity Saved to Pipeline</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Start with Template:</label>
          <select id="new-wf-template" class="input-field">
            <option value="empty">Empty Canvas (Build from Scratch)</option>
            <option value="full">Full 7-Agent Autonomous Pipeline</option>
            <option value="ats">ATS Resume & Gap Enhancer</option>
            <option value="interview">Targeted Mock Interview Sprint</option>
          </select>
        </div>
      </div>
    `;

    App.showModal('Create Custom AI Agent Workflow', content, async () => {
      const name = document.getElementById('new-wf-name').value.trim();
      const desc = document.getElementById('new-wf-desc').value.trim();
      const trigger = document.getElementById('new-wf-trigger').value;
      const template = document.getElementById('new-wf-template').value;

      if (!name) {
        App.showToast('Please provide a workflow name', 'error');
        return;
      }

      let initialNodes = [];
      if (template === 'full') {
        initialNodes = [
          { id: 'node_1', agent_type: 'job_search', label: '1. Job Scout Agent', icon: '🔍', config: {} },
          { id: 'node_2', agent_type: 'matcher', label: '2. 6-Factor Compatibility Scorer', icon: '🎯', config: {} },
          { id: 'node_3', agent_type: 'condition', label: '3. Match Score Gate', icon: '🔀', config: { min_match_score: 75 } },
          { id: 'node_4', agent_type: 'resume_ats', label: '4. Resume ATS Tailor', icon: '📄', config: {} },
          { id: 'node_5', agent_type: 'cover_letter', label: '5. Cover Letter Writer', icon: '✉️', config: { tone: 'Professional and Enthusiastic' } },
          { id: 'node_6', agent_type: 'tracker', label: '6. Pipeline Stage Tracker', icon: '📊', config: { target_stage: 'saved' } },
          { id: 'node_7', agent_type: 'interview_prep', label: '7. Mock Interview Prep Agent', icon: '🎤', config: { question_count: 4 } }
        ];
      } else if (template === 'ats') {
        initialNodes = [
          { id: 'node_1', agent_type: 'matcher', label: '1. Skill Overlap Evaluator', icon: '🎯', config: {} },
          { id: 'node_2', agent_type: 'resume_ats', label: '2. ATS Keyword Enhancer', icon: '📄', config: {} }
        ];
      } else if (template === 'interview') {
        initialNodes = [
          { id: 'node_1', agent_type: 'matcher', label: '1. Job Requirements Scorer', icon: '🎯', config: {} },
          { id: 'node_2', agent_type: 'interview_prep', label: '2. Question Generator', icon: '🎤', config: { question_count: 5 } }
        ];
      }

      try {
        const created = await API.createWorkflow({
          name: name,
          description: desc,
          trigger_type: trigger,
          nodes: initialNodes,
          icon: 'fa-wand-magic-sparkles'
        });

        App.showToast(`Workflow '${created.name}' created!`, 'success');
        await WorkflowBuilderView.loadWorkflows();
        WorkflowBuilderView.selectWorkflow(created.workflow_id);
      } catch (err) {
        App.showToast(err.message, 'error');
      }
    }, 'Create Workflow');
  },

  openAddNodeModal() {
    const content = `
      <div style="display:flex; flex-direction:column; gap:16px;">
        <label class="form-label">Select Agent Type to Add:</label>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
          ${this.availableAgents.map(ag => `
            <div class="agent-select-card" data-type="${ag.type}" data-name="${ag.name}" data-icon="${ag.icon}" style="background:rgba(15,23,42,0.7); border:1px solid var(--border-glass); border-radius:var(--radius-md); padding:12px; cursor:pointer; transition:var(--transition);" onclick="document.querySelectorAll('.agent-select-card').forEach(c => c.style.borderColor='var(--border-glass)'); this.style.borderColor='#6366f1'; document.getElementById('selected-agent-type-input').value='${ag.type}';">
              <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                <span style="font-size:1.2rem;">${ag.icon}</span>
                <strong style="font-size:0.85rem; color:#ffffff;">${ag.name}</strong>
              </div>
              <p style="font-size:0.75rem; color:var(--text-muted); margin:0;">${ag.description}</p>
            </div>
          `).join('')}
        </div>
        <input type="hidden" id="selected-agent-type-input" value="job_search">

        <div class="form-group">
          <label class="form-label">Step Label:</label>
          <input type="text" id="node-custom-label" class="input-field" placeholder="e.g., Step: Optimize Resume ATS">
        </div>
      </div>
    `;

    App.showModal('Add Agent Node to Workflow', content, async () => {
      const type = document.getElementById('selected-agent-type-input').value;
      const customLabel = document.getElementById('node-custom-label').value.trim();
      const agentInfo = this.availableAgents.find(a => a.type === type);

      const newNode = {
        id: `node_${Date.now()}`,
        agent_type: type,
        label: customLabel || agentInfo.name,
        icon: agentInfo.icon,
        config: {}
      };

      this.currentWorkflow.nodes = this.currentWorkflow.nodes || [];
      this.currentWorkflow.nodes.push(newNode);

      try {
        await API.updateWorkflow(this.currentWorkflow.workflow_id, {
          nodes: this.currentWorkflow.nodes
        });
        App.showToast('Agent node added to workflow!', 'success');
        this.renderCanvas();
      } catch (err) {
        App.showToast(err.message, 'error');
      }
    }, 'Add Node');
  },

  async moveNode(index, direction) {
    const nodes = this.currentWorkflow.nodes;
    const targetIdx = index + direction;
    if (targetIdx < 0 || targetIdx >= nodes.length) return;

    const temp = nodes[index];
    nodes[index] = nodes[targetIdx];
    nodes[targetIdx] = temp;

    try {
      await API.updateWorkflow(this.currentWorkflow.workflow_id, { nodes: nodes });
      this.renderCanvas();
    } catch (err) {
      App.showToast(err.message, 'error');
    }
  },

  async removeNode(index) {
    this.currentWorkflow.nodes.splice(index, 1);
    try {
      await API.updateWorkflow(this.currentWorkflow.workflow_id, {
        nodes: this.currentWorkflow.nodes
      });
      App.showToast('Node removed', 'info');
      this.renderCanvas();
    } catch (err) {
      App.showToast(err.message, 'error');
    }
  },

  async executeActiveWorkflow() {
    if (!this.currentWorkflow) return;
    const resultsBox = document.getElementById('workflow-run-results-box');
    resultsBox.innerHTML = `
      <div class="glass-card" style="text-align:center; padding:40px;">
        <i class="fa-solid fa-circle-notch fa-spin fa-2x" style="color:#d946ef; margin-bottom:12px;"></i>
        <div>Executing custom workflow: '${this.currentWorkflow.name}'...</div>
      </div>
    `;

    try {
      const res = await API.runWorkflow(this.currentWorkflow.workflow_id);
      App.showToast(`Workflow '${res.workflow_name}' completed!`, 'success');
      if (window.confetti) confetti();

      resultsBox.innerHTML = `
        <div class="glass-card" style="border: 1px solid rgba(16, 185, 129, 0.4); animation: fadeIn 0.4s ease-in-out;">
          <div class="card-header">
            <h4 class="card-title" style="font-size:1rem;">
              <i class="fa-solid fa-circle-check" style="color:#10b981;"></i> Workflow Execution Telemetry (${res.steps_executed.length} Steps)
            </h4>
            <span class="badge badge-score high">Completed</span>
          </div>

          <div style="display:flex; flex-direction:column; gap:8px; margin-bottom:16px;">
            ${res.steps_executed.map(step => `
              <div style="background:rgba(15,23,42,0.6); padding:10px 14px; border-radius:var(--radius-sm); border:1px solid var(--border-glass); display:flex; align-items:center; gap:10px;">
                <span style="font-size:1.1rem;">${step.icon}</span>
                <div style="font-size:0.75rem; color:var(--text-muted);">[${step.timestamp}]</div>
                <strong style="font-size:0.85rem; color:#818cf8;">${step.agent_name}:</strong>
                <span style="font-size:0.85rem; color:var(--text-primary);">${step.message}</span>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    } catch (err) {
      resultsBox.innerHTML = `<div class="glass-card" style="color:#f43f5e;">Execution Error: ${err.message}</div>`;
    }
  },

  async quickRunWorkflow(workflowId) {
    try {
      App.showToast('Starting custom agent workflow...', 'info');
      const res = await API.runWorkflow(workflowId);
      App.showToast(`Workflow '${res.workflow_name}' completed successfully!`, 'success');
      if (window.confetti) confetti();
    } catch (err) {
      App.showToast(err.message, 'error');
    }
  },

  async deleteWorkflowItem(workflowId) {
    if (confirm('Delete this workflow?')) {
      try {
        await API.deleteWorkflow(workflowId);
        App.showToast('Workflow deleted', 'info');
        this.currentWorkflow = null;
        await this.loadWorkflows();
      } catch (err) {
        App.showToast(err.message, 'error');
      }
    }
  }
};
