/**
 * Opportunities (Jobs & Internships) Component - Search, Discovery, & 6-Factor Compatibility
 */
const JobsView = {
  jobsData: [],
  selectedFilter: 'all',
  searchQuery: '',
  remoteOnly: false,

  async render(container) {
    container.innerHTML = `
      <!-- Filter Bar -->
      <div class="glass-card jobs-toolbar" style="margin-bottom: 24px; padding: 18px 24px;">
        <div class="jobs-toolbar-inner" style="display: flex; gap: 16px; align-items: center; flex-wrap: wrap;">
          <div class="jobs-search-group" style="flex: 1; min-width: 260px; position: relative;">
            <i class="fa-solid fa-magnifying-glass" style="position: absolute; left: 14px; top: 12px; color: var(--text-muted);"></i>
            <input type="text" id="jobs-search-input" class="input-field" placeholder="Search by role, company, or tech skills (e.g., Python, React)..." style="padding-left: 40px;" value="${this.searchQuery}">
          </div>

          <div class="jobs-filter-group" style="display: flex; gap: 8px;">
            <button class="btn ${this.selectedFilter === 'all' ? 'btn-primary' : 'btn-secondary'} btn-sm filter-btn" data-filter="all">All Roles</button>
            <button class="btn ${this.selectedFilter === 'internship' ? 'btn-primary' : 'btn-secondary'} btn-sm filter-btn" data-filter="internship">Internships</button>
            <button class="btn ${this.selectedFilter === 'full-time' ? 'btn-primary' : 'btn-secondary'} btn-sm filter-btn" data-filter="full-time">Full-Time</button>
          </div>

          <label class="jobs-actions" style="display: flex; align-items: center; gap: 8px; font-size: 0.85rem; color: var(--text-secondary); cursor: pointer;">
            <input type="checkbox" id="jobs-remote-toggle" ${this.remoteOnly ? 'checked' : ''} style="cursor: pointer; accent-color: var(--primary);">
            <span>Remote Only</span>
          </label>
        </div>
      </div>

      <!-- Opportunity List Container -->
      <div id="jobs-list-container">
        <div style="display:flex; justify-content:center; padding:40px;">
          <i class="fa-solid fa-circle-notch fa-spin fa-2x" style="color:#6366f1;"></i>
        </div>
      </div>
    `;

    // Event listeners for filters
    const searchInput = container.querySelector('#jobs-search-input');
    searchInput.addEventListener('input', (e) => {
      this.searchQuery = e.target.value;
      this.filterAndRenderJobs();
    });

    const filterBtns = container.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        filterBtns.forEach(b => { b.classList.remove('btn-primary'); b.classList.add('btn-secondary'); });
        btn.classList.remove('btn-secondary');
        btn.classList.add('btn-primary');
        this.selectedFilter = btn.dataset.filter;
        this.filterAndRenderJobs();
      });
    });

    const remoteToggle = container.querySelector('#jobs-remote-toggle');
    remoteToggle.addEventListener('change', (e) => {
      this.remoteOnly = e.target.checked;
      this.filterAndRenderJobs();
    });

    await this.fetchJobs();
  },

  async fetchJobs() {
    try {
      this.jobsData = await API.getJobs();
      this.filterAndRenderJobs();
    } catch (err) {
      document.getElementById('jobs-list-container').innerHTML = `
        <div class="glass-card" style="color:#f43f5e;">
          <i class="fa-solid fa-triangle-exclamation"></i> Error fetching opportunities: ${err.message}
        </div>
      `;
    }
  },

  filterAndRenderJobs() {
    const listContainer = document.getElementById('jobs-list-container');
    if (!listContainer) return;

    let filtered = [...this.jobsData];

    if (this.selectedFilter !== 'all') {
      filtered = filtered.filter(j => (j.job_type || '').toLowerCase() === this.selectedFilter);
    }

    if (this.remoteOnly) {
      filtered = filtered.filter(j => j.is_remote || (j.location || '').toLowerCase().includes('remote'));
    }

    if (this.searchQuery.trim()) {
      const q = this.searchQuery.toLowerCase();
      filtered = filtered.filter(j =>
        (j.title || '').toLowerCase().includes(q) ||
        (j.company || '').toLowerCase().includes(q) ||
        (j.description || '').toLowerCase().includes(q) ||
        (j.skills_required || []).some(s => s.toLowerCase().includes(q))
      );
    }

    if (filtered.length === 0) {
      listContainer.innerHTML = `
        <div class="glass-card" style="text-align:center; padding:48px;">
          <i class="fa-solid fa-magnifying-glass fa-3x" style="color:var(--text-muted); margin-bottom:16px;"></i>
          <h3 style="font-size:1.1rem;">No opportunities matched your search criteria</h3>
          <p style="font-size:0.85rem; color:var(--text-muted); margin-top:8px;">Try clearing filters or searching for different keywords.</p>
        </div>
      `;
      return;
    }

    listContainer.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 16px;">
        ${filtered.map(job => `
          <div class="glass-card job-card" style="display:flex; flex-direction:column; gap:14px;">
            <div class="job-card-top" style="display:flex; justify-content:space-between; align-items:flex-start; gap:16px; flex-wrap:wrap;">
              <div class="job-card-header" style="display:flex; gap:16px; align-items:center;">
                <div style="width:48px; height:48px; border-radius:var(--radius-md); background: rgba(99,102,241,0.15); border:1px solid rgba(99,102,241,0.3); display:flex; align-items:center; justify-content:center; font-size:1.4rem; color:#818cf8;">
                  <i class="fa-solid fa-building"></i>
                </div>
                <div>
                  <div style="display:flex; align-items:center; gap:10px;">
                    <h3 style="font-size:1.15rem; font-weight:700; color:#ffffff;">${job.title}</h3>
                    <span class="badge ${job.job_type === 'internship' ? 'badge-internship' : 'badge-fulltime'}">${job.job_type}</span>
                    ${job.is_remote ? '<span class="badge badge-remote">Remote</span>' : ''}
                  </div>
                  <div style="font-size:0.85rem; color:var(--text-secondary); display:flex; gap:16px; margin-top:4px; flex-wrap:wrap;">
                    <span><i class="fa-regular fa-building"></i> <strong>${job.company}</strong></span>
                    <span><i class="fa-solid fa-location-dot"></i> ${job.location}</span>
                    <span><i class="fa-solid fa-money-bill-wave"></i> ${job.salary_or_stipend}</span>
                    <span><i class="fa-regular fa-calendar"></i> Deadline: <strong>${job.deadline}</strong></span>
                  </div>
                </div>
              </div>

              <!-- Match Badge & Actions -->
              <div class="job-card-actions" style="display:flex; align-items:center; gap:12px;">
                ${job.match_score !== null ? `
                  <button class="badge badge-score ${job.match_score >= 80 ? 'high' : job.match_score >= 65 ? 'medium' : ''}" style="cursor:pointer; border-radius:var(--radius-md); padding:8px 14px; font-size:0.85rem;" onclick="JobsView.showMatchBreakdown(${job.job_id})" title="Click to view full 6-factor score breakdown">
                    🎯 ${job.match_score}% Match <i class="fa-solid fa-chevron-right" style="font-size:0.7rem;"></i>
                  </button>
                ` : ''}

                <button class="btn btn-secondary btn-sm" onclick="JobsView.saveToPipeline(${job.job_id})" title="Save to Kanban Pipeline">
                  <i class="fa-regular fa-bookmark"></i> Save
                </button>
                <button class="btn btn-primary btn-sm" onclick="App.runPipelineForJob(${job.job_id})">
                  <i class="fa-solid fa-bolt"></i> Run AI Suite
                </button>
              </div>
            </div>

            <!-- Job Description Snippet -->
            <p style="font-size:0.88rem; color:var(--text-secondary); line-height:1.5;">
              ${job.description}
            </p>

            <!-- Skills & Qualifications Row -->
            <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--border-glass); padding-top:12px; flex-wrap:wrap; gap:10px;">
              <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                <span style="font-size:0.78rem; font-weight:700; color:var(--text-muted); text-transform:uppercase;">Required Skills:</span>
                ${(job.skills_required || []).map(skill => `<span class="tag">${skill}</span>`).join('')}
              </div>
              <div style="font-size:0.78rem; color:var(--text-muted);">
                Source: <span>${job.source || 'AI Aggregator'}</span>
              </div>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  },

  async showMatchBreakdown(jobId) {
    const job = this.jobsData.find(j => j.job_id === jobId);
    if (!job) return;

    let breakdown = job.match_breakdown;
    if (!breakdown) {
      breakdown = await API.calculateMatch(jobId);
    }

    const content = `
      <div style="display:flex; flex-direction:column; gap:20px;">
        <div style="display:flex; align-items:center; justify-content:space-between; background:rgba(30,41,59,0.5); padding:16px; border-radius:var(--radius-md); border:1px solid var(--border-glass);">
          <div>
            <h4 style="font-size:1.1rem; font-weight:700;">${job.title}</h4>
            <div style="font-size:0.85rem; color:var(--text-secondary);">${job.company} • ${job.location}</div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:1.8rem; font-weight:800; color:${breakdown.overall_match_score >= 80 ? '#34d399' : '#fbbf24'};">
              ${breakdown.overall_match_score}%
            </div>
            <div style="font-size:0.75rem; color:var(--text-muted);">Overall Compatibility</div>
          </div>
        </div>

        <div>
          <h5 style="font-size:0.85rem; text-transform:uppercase; color:var(--text-muted); font-weight:700; margin-bottom:10px;">
            6-Factor Compatibility Breakdown (Spec Section 8)
          </h5>
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
            <div style="background:rgba(15,23,42,0.6); padding:12px; border-radius:var(--radius-sm); border:1px solid var(--border-glass);">
              <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:4px;">
                <span>Skill Match (40% Weight)</span>
                <strong>${breakdown.skill_score}%</strong>
              </div>
              <div style="width:100%; height:6px; background:rgba(255,255,255,0.1); border-radius:3px; overflow:hidden;">
                <div style="width:${breakdown.skill_score}%; height:100%; background:#6366f1;"></div>
              </div>
            </div>

            <div style="background:rgba(15,23,42,0.6); padding:12px; border-radius:var(--radius-sm); border:1px solid var(--border-glass);">
              <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:4px;">
                <span>Education Match (15% Weight)</span>
                <strong>${breakdown.education_score}%</strong>
              </div>
              <div style="width:100%; height:6px; background:rgba(255,255,255,0.1); border-radius:3px; overflow:hidden;">
                <div style="width:${breakdown.education_score}%; height:100%; background:#06b6d4;"></div>
              </div>
            </div>

            <div style="background:rgba(15,23,42,0.6); padding:12px; border-radius:var(--radius-sm); border:1px solid var(--border-glass);">
              <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:4px;">
                <span>Experience Match (15% Weight)</span>
                <strong>${breakdown.experience_score}%</strong>
              </div>
              <div style="width:100%; height:6px; background:rgba(255,255,255,0.1); border-radius:3px; overflow:hidden;">
                <div style="width:${breakdown.experience_score}%; height:100%; background:#10b981;"></div>
              </div>
            </div>

            <div style="background:rgba(15,23,42,0.6); padding:12px; border-radius:var(--radius-sm); border:1px solid var(--border-glass);">
              <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:4px;">
                <span>Project Match (15% Weight)</span>
                <strong>${breakdown.project_score}%</strong>
              </div>
              <div style="width:100%; height:6px; background:rgba(255,255,255,0.1); border-radius:3px; overflow:hidden;">
                <div style="width:${breakdown.project_score}%; height:100%; background:#8b5cf6;"></div>
              </div>
            </div>

            <div style="background:rgba(15,23,42,0.6); padding:12px; border-radius:var(--radius-sm); border:1px solid var(--border-glass);">
              <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:4px;">
                <span>Location Match (5% Weight)</span>
                <strong>${breakdown.location_score}%</strong>
              </div>
              <div style="width:100%; height:6px; background:rgba(255,255,255,0.1); border-radius:3px; overflow:hidden;">
                <div style="width:${breakdown.location_score}%; height:100%; background:#f59e0b;"></div>
              </div>
            </div>

            <div style="background:rgba(15,23,42,0.6); padding:12px; border-radius:var(--radius-sm); border:1px solid var(--border-glass);">
              <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:4px;">
                <span>Role Alignment (10% Weight)</span>
                <strong>${breakdown.other_score}%</strong>
              </div>
              <div style="width:100%; height:6px; background:rgba(255,255,255,0.1); border-radius:3px; overflow:hidden;">
                <div style="width:${breakdown.other_score}%; height:100%; background:#ec4899;"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Matched & Missing Skills -->
        <div style="display:flex; flex-direction:column; gap:8px;">
          <div style="font-size:0.85rem; font-weight:700;">Matching Skills:</div>
          <div style="display:flex; flex-wrap:wrap; gap:6px;">
            ${(breakdown.matched_skills || []).map(s => `<span class="tag match"><i class="fa-solid fa-check"></i> ${s}</span>`).join('') || '<span style="color:var(--text-muted); font-size:0.8rem;">None detected</span>'}
          </div>
        </div>

        ${(breakdown.missing_skills && breakdown.missing_skills.length > 0) ? `
          <div style="display:flex; flex-direction:column; gap:8px;">
            <div style="font-size:0.85rem; font-weight:700;">Skills to Acquire / Highlight:</div>
            <div style="display:flex; flex-wrap:wrap; gap:6px;">
              ${breakdown.missing_skills.map(s => `<span class="tag missing"><i class="fa-solid fa-circle-exclamation"></i> ${s}</span>`).join('')}
            </div>
          </div>
        ` : ''}

        <!-- Recommendations -->
        <div style="background:rgba(99,102,241,0.1); border-left:3px solid #6366f1; padding:12px 16px; border-radius:var(--radius-sm);">
          <div style="font-size:0.85rem; font-weight:700; color:#818cf8; margin-bottom:4px;">AI Recommendation:</div>
          <p style="font-size:0.82rem; color:var(--text-primary); margin:0;">
            ${breakdown.fit_summary}
          </p>
        </div>
      </div>
    `;

    App.showModal('Job Compatibility Report', content, () => {
      App.runPipelineForJob(jobId);
    }, 'Run Full AI Optimization');
  },

  async saveToPipeline(jobId) {
    try {
      await API.createApplication({ job_id: jobId, status: 'saved' });
      App.showToast('Saved to Application Pipeline!', 'success');
    } catch (err) {
      App.showToast(err.message, 'error');
    }
  }
};
