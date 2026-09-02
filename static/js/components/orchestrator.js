/**
 * Multi-Agent Pipeline Visualizer Component - Real-Time Orchestration Telemetry
 */
const OrchestratorView = {
  jobsList: [],

  async render(container) {
    container.innerHTML = `
      <div style="display:flex; flex-direction:column; gap:24px;">
        <!-- Top Agent Architecture Overview Bar -->
        <div class="glass-card" style="background: linear-gradient(135deg, rgba(15,23,42,0.8), rgba(30,41,59,0.7));">
          <div class="card-header" style="margin-bottom:14px;">
            <h3 class="card-title"><i class="fa-solid fa-network-wired" style="color:#818cf8;"></i> 7-Agent Coordinated Architecture (Spec Section 5)</h3>
            <span class="badge badge-score high">Multi-Agent State Machine Active</span>
          </div>

          <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap:12px; text-align:center;">
            <div style="background:rgba(0,0,0,0.3); border:1px solid var(--border-glass); border-radius:var(--radius-sm); padding:10px;">
              <div style="font-size:1.4rem;">🤖</div>
              <div style="font-size:0.75rem; font-weight:700; color:#818cf8; margin-top:4px;">1. Orchestrator</div>
              <div style="font-size:0.68rem; color:var(--text-muted);">Workflow Controller</div>
            </div>
            <div style="background:rgba(0,0,0,0.3); border:1px solid var(--border-glass); border-radius:var(--radius-sm); padding:10px;">
              <div style="font-size:1.4rem;">🔍</div>
              <div style="font-size:0.75rem; font-weight:700; color:#22d3ee; margin-top:4px;">2. Job Search</div>
              <div style="font-size:0.68rem; color:var(--text-muted);">Discovery & Deduplication</div>
            </div>
            <div style="background:rgba(0,0,0,0.3); border:1px solid var(--border-glass); border-radius:var(--radius-sm); padding:10px;">
              <div style="font-size:1.4rem;">🎯</div>
              <div style="font-size:0.75rem; font-weight:700; color:#34d399; margin-top:4px;">3. Job Matcher</div>
              <div style="font-size:0.68rem; color:var(--text-muted);">6-Factor Scorer</div>
            </div>
            <div style="background:rgba(0,0,0,0.3); border:1px solid var(--border-glass); border-radius:var(--radius-sm); padding:10px;">
              <div style="font-size:1.4rem;">📄</div>
              <div style="font-size:0.75rem; font-weight:700; color:#a78bfa; margin-top:4px;">4. Resume Agent</div>
              <div style="font-size:0.68rem; color:var(--text-muted);">ATS Optimizer</div>
            </div>
            <div style="background:rgba(0,0,0,0.3); border:1px solid var(--border-glass); border-radius:var(--radius-sm); padding:10px;">
              <div style="font-size:1.4rem;">✉️</div>
              <div style="font-size:0.75rem; font-weight:700; color:#fbbf24; margin-top:4px;">5. Cover Letter</div>
              <div style="font-size:0.68rem; color:var(--text-muted);">Personalized Synthesis</div>
            </div>
            <div style="background:rgba(0,0,0,0.3); border:1px solid var(--border-glass); border-radius:var(--radius-sm); padding:10px;">
              <div style="font-size:1.4rem;">📊</div>
              <div style="font-size:0.75rem; font-weight:700; color:#38bdf8; margin-top:4px;">6. Tracker Agent</div>
              <div style="font-size:0.68rem; color:var(--text-muted);">Kanban & Deadlines</div>
            </div>
            <div style="background:rgba(0,0,0,0.3); border:1px solid var(--border-glass); border-radius:var(--radius-sm); padding:10px;">
              <div style="font-size:1.4rem;">🎤</div>
              <div style="font-size:0.75rem; font-weight:700; color:#f43f5e; margin-top:4px;">7. Interview Prep</div>
              <div style="font-size:0.68rem; color:var(--text-muted);">Mock Question Generator</div>
            </div>
          </div>
        </div>

        <!-- Orchestrator Control & Terminal -->
        <div class="orchestrator-layout" style="display:grid; grid-template-columns: 1fr 2fr; gap:24px;">
          <!-- Controls -->
          <div class="glass-card orchestrator-column">
            <div class="card-header">
              <h3 class="card-title" style="font-size:1rem;"><i class="fa-solid fa-sliders" style="color:#06b6d4;"></i> Launch Parameters</h3>
            </div>

            <div class="form-group">
              <label class="form-label">Target Opportunity:</label>
              <select id="orchestrator-job-select" class="input-field">
                <!-- Populated dynamically -->
              </select>
            </div>

            <div style="display:flex; flex-direction:column; gap:10px; margin-bottom:20px;">
              <label style="display:flex; align-items:center; gap:8px; font-size:0.85rem; cursor:pointer;">
                <input type="checkbox" id="orch-chk-resume" checked style="accent-color:var(--primary);">
                <span>Execute Resume ATS Tailoring</span>
              </label>
              <label style="display:flex; align-items:center; gap:8px; font-size:0.85rem; cursor:pointer;">
                <input type="checkbox" id="orch-chk-cl" checked style="accent-color:var(--primary);">
                <span>Synthesize Custom Cover Letter</span>
              </label>
              <label style="display:flex; align-items:center; gap:8px; font-size:0.85rem; cursor:pointer;">
                <input type="checkbox" id="orch-chk-interview" checked style="accent-color:var(--primary);">
                <span>Generate Mock Interview Bundle</span>
              </label>
            </div>

            <button class="btn btn-primary" id="btn-run-orchestrator" style="width:100%;">
              <i class="fa-solid fa-play"></i> Run End-to-End Orchestrator
            </button>
          </div>

          <!-- Live Terminal Output -->
          <div class="glass-card orchestrator-column orchestrator-terminal-panel" style="display:flex; flex-direction:column;">
            <div class="card-header">
              <h3 class="card-title" style="font-size:1rem;"><i class="fa-solid fa-terminal" style="color:#818cf8;"></i> Live Agent Telemetry Terminal</h3>
              <span id="orchestrator-status-badge" class="badge" style="background:rgba(255,255,255,0.05); color:var(--text-muted);">Idle</span>
            </div>

            <div class="agent-terminal" id="agent-terminal-logs">
              <div class="agent-log-line" style="color:var(--text-muted);">
                <span>[00:00:00]</span> <span>Waiting for workflow trigger... Select an opportunity and click 'Run End-to-End Orchestrator'.</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Generated Application Bundle Results Container -->
        <div id="orchestrator-results-container"></div>
      </div>
    `;

    await this.init(container);
  },

  async init(container) {
    try {
      this.jobsList = await API.getJobs();
      const select = container.querySelector('#orchestrator-job-select');
      this.jobsList.forEach(job => {
        const opt = document.createElement('option');
        opt.value = job.job_id;
        opt.textContent = `${job.title} (${job.company}) - ${job.match_score ? job.match_score + '% Match' : ''}`;
        select.appendChild(opt);
      });
    } catch (e) {
      console.warn('Failed to load jobs for orchestrator:', e);
    }

    container.querySelector('#btn-run-orchestrator').addEventListener('click', async () => {
      await this.runPipeline(container);
    });
  },

  async runPipeline(container, targetJobId = null) {
    const jobSelect = container.querySelector('#orchestrator-job-select');
    if (targetJobId && jobSelect) {
      jobSelect.value = String(targetJobId);
    }
    let jobId = targetJobId || (jobSelect ? parseInt(jobSelect.value) : null);

    // If still no jobId, fetch jobs if list is empty or select first
    if (!jobId || isNaN(jobId)) {
      if (!this.jobsList || this.jobsList.length === 0) {
        this.jobsList = await API.getJobs();
      }
      if (this.jobsList && this.jobsList.length > 0) {
        jobId = this.jobsList[0].job_id;
        if (jobSelect) jobSelect.value = String(jobId);
      }
    }

    if (!jobId) {
      App.showToast('Please select a target opportunity to orchestrate.', 'error');
      return;
    }

    const resumeCheck = container.querySelector('#orch-chk-resume')?.checked ?? true;
    const clCheck = container.querySelector('#orch-chk-cl')?.checked ?? true;
    const interviewCheck = container.querySelector('#orch-chk-interview')?.checked ?? true;

    const terminal = container.querySelector('#agent-terminal-logs');
    const statusBadge = container.querySelector('#orchestrator-status-badge');
    const resultsBox = container.querySelector('#orchestrator-results-container');

    statusBadge.style.background = 'rgba(99,102,241,0.2)';
    statusBadge.style.color = '#818cf8';
    statusBadge.textContent = 'Orchestrating 7 Agents...';
    terminal.innerHTML = '';
    resultsBox.innerHTML = '';

    try {
      const res = await API.runOrchestrator({
        job_id: jobId,
        include_resume_tailoring: resumeCheck,
        include_cover_letter: clCheck,
        include_interview_prep: interviewCheck
      });

      // Stream logs visually
      for (const step of res.steps) {
        await new Promise(r => setTimeout(r, 120)); // Subtle animation pacing
        const logLine = document.createElement('div');
        logLine.className = 'agent-log-line';
        logLine.innerHTML = `
          <span class="agent-badge-icon">${step.icon}</span>
          <span class="agent-time">[${step.timestamp}]</span>
          <span class="agent-name-tag">${step.agent_name}:</span>
          <span class="agent-log-msg">${step.message}</span>
        `;
        terminal.appendChild(logLine);
        terminal.scrollTop = terminal.scrollHeight;
      }

      statusBadge.style.background = 'rgba(16,185,129,0.2)';
      statusBadge.style.color = '#34d399';
      statusBadge.textContent = 'Completed (Ready for Human Approval)';
      App.showToast('Multi-Agent Execution Pipeline Completed!', 'success');

      this.renderBundleResults(resultsBox, res.results);
    } catch (err) {
      statusBadge.style.background = 'rgba(244,63,94,0.2)';
      statusBadge.style.color = '#f43f5e';
      statusBadge.textContent = 'Failed';
      terminal.innerHTML += `<div class="agent-log-line" style="color:#f43f5e;">Error: ${err.message}</div>`;
      App.showToast(err.message, 'error');
    }
  },

  renderBundleResults(container, results) {
    container.innerHTML = `
      <div class="glass-card" style="border:1px solid rgba(16, 185, 129, 0.4); animation: fadeIn 0.4s ease-in-out;">
        <div class="card-header">
          <h3 class="card-title"><i class="fa-solid fa-box-archive" style="color:#34d399;"></i> Generated Application Optimization Bundle</h3>
          <span class="badge badge-score high">Human-in-the-Loop Safe</span>
        </div>

        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:18px;">
          <!-- 1. Match Summary -->
          ${results.match_analysis ? `
            <div style="background:rgba(15,23,42,0.6); padding:16px; border-radius:var(--radius-md); border:1px solid var(--border-glass);">
              <h4 style="font-size:0.9rem; font-weight:700; color:#818cf8; margin-bottom:8px;">
                🎯 6-Factor Compatibility: ${results.match_analysis.overall_match_score}%
              </h4>
              <p style="font-size:0.8rem; color:var(--text-secondary); margin-bottom:8px;">
                ${results.match_analysis.fit_summary}
              </p>
              <div style="font-size:0.75rem; color:var(--text-muted);">
                Matched Skills: ${results.match_analysis.matched_skills?.join(', ') || 'None'}
              </div>
            </div>
          ` : ''}

          <!-- 2. Tailored Resume -->
          ${results.resume_analysis ? `
            <div style="background:rgba(15,23,42,0.6); padding:16px; border-radius:var(--radius-md); border:1px solid var(--border-glass);">
              <h4 style="font-size:0.9rem; font-weight:700; color:#06b6d4; margin-bottom:8px;">
                📄 Tailored ATS Resume Draft (${results.resume_analysis.ats_score}/100)
              </h4>
              <p style="font-size:0.8rem; color:var(--text-secondary); margin-bottom:10px;">
                ATS keywords synchronized and impact bullet points generated.
              </p>
              <button class="btn btn-secondary btn-sm" onclick="App.navigate('resume')">
                Open in Resume Studio →
              </button>
            </div>
          ` : ''}

          <!-- 3. Cover Letter -->
          ${results.cover_letter ? `
            <div style="background:rgba(15,23,42,0.6); padding:16px; border-radius:var(--radius-md); border:1px solid var(--border-glass);">
              <h4 style="font-size:0.9rem; font-weight:700; color:#fbbf24; margin-bottom:8px;">
                ✉️ Tailored Cover Letter
              </h4>
              <p style="font-size:0.8rem; color:var(--text-secondary); margin-bottom:10px;">
                Personalized cover letter synthesized for ${results.cover_letter.company_name}.
              </p>
              <button class="btn btn-secondary btn-sm" onclick="App.navigate('cover-letter')">
                Open in Cover Letter Editor →
              </button>
            </div>
          ` : ''}

          <!-- 4. Interview Prep -->
          ${results.interview_questions ? `
            <div style="background:rgba(15,23,42,0.6); padding:16px; border-radius:var(--radius-md); border:1px solid var(--border-glass);">
              <h4 style="font-size:0.9rem; font-weight:700; color:#f43f5e; margin-bottom:8px;">
                🎤 Mock Interview Question Bank (${results.interview_questions.length} Questions)
              </h4>
              <p style="font-size:0.8rem; color:var(--text-secondary); margin-bottom:10px;">
                Technical, behavioral and company culture assessment rubrics ready.
              </p>
              <button class="btn btn-secondary btn-sm" onclick="App.navigate('interview')">
                Start Mock Practice →
              </button>
            </div>
          ` : ''}
        </div>
      </div>
    `;
  }
};
