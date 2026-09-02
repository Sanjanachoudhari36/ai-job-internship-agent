/**
 * AI Resume Studio Component - Resume Parsing, ATS Keyword Scoring & Tailoring
 */
const ResumeView = {
  currentAnalysis: null,
  jobsList: [],

  async render(container) {
    container.innerHTML = `
      <div class="resume-layout" style="display:grid; grid-template-columns: 1fr 1fr; gap: 24px;">
        <!-- Left Column: Upload & Configuration -->
        <div class="resume-column" style="display:flex; flex-direction:column; gap:20px;">
          <!-- Upload Card -->
          <div class="glass-card">
            <div class="card-header">
              <h3 class="card-title"><i class="fa-solid fa-cloud-arrow-up" style="color:#6366f1;"></i> Resume Upload & Parser</h3>
            </div>
            
            <div id="resume-dropzone" style="border: 2px dashed rgba(99, 102, 241, 0.4); border-radius: var(--radius-lg); padding: 32px; text-align:center; background: rgba(15, 23, 42, 0.4); cursor:pointer; transition:var(--transition);" onmouseover="this.style.borderColor='#6366f1'; this.style.background='rgba(99, 102, 241, 0.05)';" onmouseout="this.style.borderColor='rgba(99, 102, 241, 0.4)'; this.style.background='rgba(15, 23, 42, 0.4)';">
              <i class="fa-solid fa-file-pdf fa-3x" style="color:#818cf8; margin-bottom:12px;"></i>
              <div style="font-weight:700; font-size:1rem; margin-bottom:4px;">Drag and drop your resume file here</div>
              <p style="font-size:0.8rem; color:var(--text-muted); margin-bottom:16px;">Supports PDF, DOCX, and TXT formats</p>
              <input type="file" id="resume-file-input" accept=".pdf,.docx,.doc,.txt,.md" style="display:none;">
              <button class="btn btn-secondary btn-sm" onclick="document.getElementById('resume-file-input').click()">
                <i class="fa-solid fa-folder-open"></i> Browse Files
              </button>
            </div>

            <div id="upload-status" style="margin-top:14px; font-size:0.85rem; color:var(--accent-emerald); display:none;">
              <i class="fa-solid fa-circle-check"></i> <span id="upload-status-text">Resume parsed successfully!</span>
            </div>
          </div>

          <!-- Target Job Selector for ATS Analysis -->
          <div class="glass-card">
            <div class="card-header">
              <h3 class="card-title"><i class="fa-solid fa-crosshairs" style="color:#06b6d4;"></i> Target Job Description</h3>
            </div>

            <div class="form-group">
              <label class="form-label">Select from Saved Opportunities:</label>
              <select id="resume-job-select" class="input-field">
                <option value="">-- Choose a target job --</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Or Paste Custom Job Description:</label>
              <textarea id="resume-custom-jd" class="input-field" rows="4" placeholder="Paste full job description or key requirements here..."></textarea>
            </div>

            <button class="btn btn-primary" id="btn-run-resume-analysis" style="width:100%;">
              <i class="fa-solid fa-wand-magic-sparkles"></i> Run ATS Scan & Resume Tailor
            </button>
          </div>
        </div>

        <!-- Right Column: ATS Report & Tailored Draft Preview -->
        <div id="resume-results-container" class="resume-results-column">
          <div class="glass-card" style="text-align:center; padding:60px 24px; min-height:400px; display:flex; flex-direction:column; align-items:center; justify-content:center;">
            <i class="fa-solid fa-file-waveform fa-3x" style="color:var(--text-muted); margin-bottom:16px;"></i>
            <h3 style="font-size:1.1rem;">ATS Analysis & Tailored Draft Ready</h3>
            <p style="font-size:0.85rem; color:var(--text-muted); max-width:350px; margin-top:8px;">
              Upload your resume or select a target opportunity on the left to generate ATS score metrics, missing keyword insights, and optimized bullet points.
            </p>
          </div>
        </div>
      </div>
    `;

    this.setupEventListeners(container);
    await this.loadJobs(container);
  },

  async setupEventListeners(container) {
    const fileInput = container.querySelector('#resume-file-input');
    fileInput.addEventListener('change', async (e) => {
      if (e.target.files.length > 0) {
        await this.handleFileUpload(e.target.files[0]);
      }
    });

    const dropzone = container.querySelector('#resume-dropzone');
    dropzone.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.style.borderColor = '#6366f1'; });
    dropzone.addEventListener('dragleave', (e) => { e.preventDefault(); dropzone.style.borderColor = 'rgba(99,102,241,0.4)'; });
    dropzone.addEventListener('drop', async (e) => {
      e.preventDefault();
      if (e.dataTransfer.files.length > 0) {
        await this.handleFileUpload(e.dataTransfer.files[0]);
      }
    });

    const analyzeBtn = container.querySelector('#btn-run-resume-analysis');
    analyzeBtn.addEventListener('click', async () => {
      await this.runAnalysis();
    });
  },

  async loadJobs(container) {
    try {
      this.jobsList = await API.getJobs();
      const select = container.querySelector('#resume-job-select');
      this.jobsList.forEach(job => {
        const opt = document.createElement('option');
        opt.value = job.job_id;
        opt.textContent = `${job.title} - ${job.company}`;
        select.appendChild(opt);
      });
    } catch (e) {
      console.warn('Failed to load jobs for resume selector:', e);
    }
  },

  async handleFileUpload(file) {
    const statusBox = document.getElementById('upload-status');
    const statusText = document.getElementById('upload-status-text');
    statusBox.style.display = 'block';
    statusText.textContent = `Uploading & parsing ${file.name}...`;

    try {
      const res = await API.uploadResume(file);
      statusText.textContent = `Parsed: ${file.name} (${res.extracted_skills.length} skills found)`;
      App.showToast(`Resume uploaded & parsed successfully!`, 'success');
    } catch (err) {
      statusText.textContent = `Upload error: ${err.message}`;
      statusBox.style.color = '#f43f5e';
      App.showToast(err.message, 'error');
    }
  },

  async runAnalysis() {
    const jobSelect = document.getElementById('resume-job-select');
    const customJd = document.getElementById('resume-custom-jd').value;
    const jobId = jobSelect.value ? parseInt(jobSelect.value) : null;

    const resultsContainer = document.getElementById('resume-results-container');
    resultsContainer.innerHTML = `
      <div class="glass-card" style="text-align:center; padding:60px 24px;">
        <i class="fa-solid fa-circle-notch fa-spin fa-3x" style="color:#6366f1; margin-bottom:16px;"></i>
        <h3>AI Resume Agent Analyzing ATS Compatibility...</h3>
        <p style="font-size:0.85rem; color:var(--text-muted); margin-top:8px;">Comparing keywords, calculating fit, and generating impact-driven bullet points...</p>
      </div>
    `;

    try {
      const analysis = await API.analyzeResume(jobId, customJd);
      this.currentAnalysis = analysis;
      this.renderAnalysisResults(resultsContainer);
    } catch (err) {
      resultsContainer.innerHTML = `
        <div class="glass-card" style="color:#f43f5e;">
          <i class="fa-solid fa-triangle-exclamation"></i> Error running resume analysis: ${err.message}
        </div>
      `;
    }
  },

  renderAnalysisResults(container) {
    const a = this.currentAnalysis;
    if (!a) return;

    container.innerHTML = `
      <div style="display:flex; flex-direction:column; gap:20px;">
        <!-- ATS Score Card -->
        <div class="glass-card" style="background: linear-gradient(145deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9));">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-size:0.85rem; color:var(--text-muted); font-weight:600; text-transform:uppercase;">ATS Compatibility Score</div>
              <h2 style="font-size:2.2rem; font-weight:800; color:${a.ats_score >= 80 ? '#34d399' : '#fbbf24'}; margin:4px 0;">
                ${a.ats_score}<span style="font-size:1.1rem; color:var(--text-muted); font-weight:500;">/100</span>
              </h2>
              <div style="font-size:0.8rem; color:var(--text-secondary);">
                ${a.ats_score >= 80 ? '🔥 High ATS match rate for technical recruiter filters.' : '⚠️ Moderate match. Add missing keywords to pass auto-filters.'}
              </div>
            </div>
            <div style="width:80px; height:80px; border-radius:50%; border:6px solid ${a.ats_score >= 80 ? '#10b981' : '#f59e0b'}; display:flex; align-items:center; justify-content:center; font-size:1.4rem; font-weight:800;">
              ${a.ats_score}%
            </div>
          </div>
        </div>

        <!-- Missing Keywords & Skill Gap -->
        <div class="glass-card">
          <h4 style="font-size:0.9rem; font-weight:700; text-transform:uppercase; color:var(--text-muted); margin-bottom:10px;">
            Target Keywords & Skill Alignment
          </h4>
          <div style="display:flex; flex-direction:column; gap:12px;">
            <div>
              <div style="font-size:0.8rem; font-weight:600; margin-bottom:6px;">Extracted Skills Found in Resume:</div>
              <div style="display:flex; flex-wrap:wrap; gap:6px;">
                ${a.extracted_skills.map(s => `<span class="tag match"><i class="fa-solid fa-check"></i> ${s}</span>`).join('')}
              </div>
            </div>

            ${a.missing_keywords && a.missing_keywords.length > 0 ? `
              <div>
                <div style="font-size:0.8rem; font-weight:600; margin-bottom:6px; color:#fda4af;">Recommended Keywords to Include:</div>
                <div style="display:flex; flex-wrap:wrap; gap:6px;">
                  ${a.missing_keywords.map(s => `<span class="tag missing"><i class="fa-solid fa-plus"></i> ${s}</span>`).join('')}
                </div>
              </div>
            ` : ''}
          </div>
        </div>

        <!-- Bullet Point Optimizer -->
        <div class="glass-card">
          <h4 style="font-size:0.9rem; font-weight:700; text-transform:uppercase; color:#818cf8; margin-bottom:12px;">
            <i class="fa-solid fa-wand-magic-sparkles"></i> AI Bullet Point Enhancer
          </h4>
          <div style="display:flex; flex-direction:column; gap:12px;">
            ${(a.bullet_suggestions || []).map(b => `
              <div style="background:rgba(15,23,42,0.6); padding:12px 14px; border-radius:var(--radius-md); border:1px solid var(--border-glass);">
                <div style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; font-weight:700; margin-bottom:4px;">Original:</div>
                <div style="font-size:0.82rem; color:var(--text-secondary); margin-bottom:8px;">${b.original}</div>
                <div style="font-size:0.75rem; color:#34d399; text-transform:uppercase; font-weight:700; margin-bottom:4px;">Tailored with Measurable Impact:</div>
                <div style="font-size:0.85rem; color:#ffffff; font-weight:500;">${b.tailored_with_impact}</div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Tailored Resume Draft Preview -->
        <div class="glass-card">
          <div class="card-header">
            <h4 class="card-title" style="font-size:0.95rem;"><i class="fa-solid fa-file-pen" style="color:#06b6d4;"></i> Tailored Resume Draft</h4>
            <button class="btn btn-secondary btn-sm" onclick="ResumeView.copyDraft()">
              <i class="fa-regular fa-copy"></i> Copy Markdown
            </button>
          </div>
          <textarea id="tailored-resume-textarea" class="input-field" style="height:250px; font-family:'JetBrains Mono', monospace; font-size:0.82rem;" readonly>${a.tailored_resume_preview}</textarea>
        </div>
      </div>
    `;
  },

  copyDraft() {
    const text = document.getElementById('tailored-resume-textarea');
    if (text) {
      navigator.clipboard.writeText(text.value);
      App.showToast('Tailored resume draft copied to clipboard!', 'success');
    }
  }
};
