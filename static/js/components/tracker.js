/**
 * Application Tracker Component - Kanban Pipeline with Drag & Drop & Deadline Alarms
 */
const TrackerView = {
  applications: [],
  stages: [
    { id: 'saved', name: 'Saved', color: '#94a3b8', icon: 'fa-bookmark' },
    { id: 'applied', name: 'Applied', color: '#6366f1', icon: 'fa-paper-plane' },
    { id: 'assessment', name: 'Assessment', color: '#06b6d4', icon: 'fa-code' },
    { id: 'interview', name: 'Interview', color: '#f59e0b', icon: 'fa-comments' },
    { id: 'selected', name: 'Selected / Offer', color: '#10b981', icon: 'fa-trophy' },
    { id: 'rejected', name: 'Rejected', color: '#f43f5e', icon: 'fa-circle-xmark' }
  ],

  async render(container) {
    container.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; flex-wrap:wrap; gap:12px;">
        <div style="font-size:0.9rem; color:var(--text-muted);">
          Drag and drop opportunities between stages to update your application status.
        </div>
        <button class="btn btn-primary btn-sm" id="btn-add-tracker-app">
          <i class="fa-solid fa-plus"></i> Add New Application
        </button>
      </div>

      <!-- Kanban Columns Container -->
      <div class="kanban-board" id="kanban-board">
        <div style="display:flex; justify-content:center; padding:40px; grid-column:1/-1;">
          <i class="fa-solid fa-circle-notch fa-spin fa-2x" style="color:#6366f1;"></i>
        </div>
      </div>
    `;

    container.querySelector('#btn-add-tracker-app').addEventListener('click', () => {
      this.showAddApplicationModal();
    });

    await this.fetchAndRenderKanban();
  },

  async fetchAndRenderKanban() {
    try {
      this.applications = await API.getApplications();
      const board = document.getElementById('kanban-board');
      if (!board) return;

      board.innerHTML = this.stages.map(stage => {
        const stageApps = this.applications.filter(a => (a.status || 'saved').toLowerCase() === stage.id);

        return `
          <div class="kanban-column" data-stage="${stage.id}">
            <div class="column-header">
              <div class="column-title" style="color:${stage.color};">
                <i class="fa-solid ${stage.icon}"></i>
                <span>${stage.name}</span>
              </div>
              <span class="column-count">${stageApps.length}</span>
            </div>

            <div class="column-body" id="col-${stage.id}">
              ${stageApps.map(app => this.renderKanbanCard(app)).join('')}
            </div>
          </div>
        `;
      }).join('');

      this.attachDragEvents();
    } catch (err) {
      console.error('Error fetching applications for Kanban:', err);
    }
  },

  renderKanbanCard(app) {
    const job = app.job || { title: 'Software Engineer', company: 'Tech Corp', deadline: 'Open' };
    const score = app.match_score || 80;

    return `
      <div class="kanban-card" draggable="true" data-app-id="${app.application_id}">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
          <span style="font-size:0.75rem; font-weight:700; color:var(--text-muted); text-transform:uppercase;">${job.company}</span>
          <span class="badge badge-score ${score >= 80 ? 'high' : ''}" style="font-size:0.7rem; padding:2px 6px;">
            ${score}%
          </span>
        </div>

        <div style="font-weight:700; font-size:0.92rem; color:#ffffff; margin-bottom:6px; line-height:1.3;">
          ${job.title}
        </div>

        ${app.notes ? `
          <p style="font-size:0.75rem; color:var(--text-secondary); margin-bottom:8px; line-height:1.4; background:rgba(0,0,0,0.2); padding:6px 8px; border-radius:4px;">
            <i class="fa-regular fa-note-sticky" style="color:#fbbf24;"></i> ${app.notes}
          </p>
        ` : ''}

        ${app.interview_date ? `
          <div style="font-size:0.75rem; color:#fbbf24; margin-bottom:8px; font-weight:600;">
            <i class="fa-solid fa-calendar-days"></i> Interview: ${new Date(app.interview_date).toLocaleDateString()}
          </div>
        ` : ''}

        <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--border-glass); padding-top:8px; margin-top:6px;">
          <div style="font-size:0.72rem; color:var(--text-muted);">
            <i class="fa-regular fa-clock"></i> ${job.deadline || 'No deadline'}
          </div>
          <div style="display:flex; gap:6px;">
            <button class="btn-icon" style="padding:4px; font-size:0.75rem;" onclick="TrackerView.editApplication(${app.application_id})" title="Edit Notes / Dates">
              <i class="fa-solid fa-pen"></i>
            </button>
            <button class="btn-icon" style="padding:4px; font-size:0.75rem; color:#f43f5e;" onclick="TrackerView.deleteApp(${app.application_id})" title="Delete Application">
              <i class="fa-solid fa-trash-can"></i>
            </button>
          </div>
        </div>
      </div>
    `;
  },

  attachDragEvents() {
    const cards = document.querySelectorAll('.kanban-card');
    const columns = document.querySelectorAll('.column-body');

    cards.forEach(card => {
      card.addEventListener('dragstart', (e) => {
        card.classList.add('dragging');
        e.dataTransfer.setData('text/plain', card.dataset.appId);
      });

      card.addEventListener('dragend', () => {
        card.classList.remove('dragging');
      });
    });

    columns.forEach(col => {
      col.addEventListener('dragover', (e) => {
        e.preventDefault();
        col.style.background = 'rgba(99, 102, 241, 0.08)';
      });

      col.addEventListener('dragleave', () => {
        col.style.background = 'transparent';
      });

      col.addEventListener('drop', async (e) => {
        e.preventDefault();
        col.style.background = 'transparent';
        const appId = parseInt(e.dataTransfer.getData('text/plain'));
        const newStage = col.parentElement.dataset.stage;

        if (appId && newStage) {
          try {
            await API.updateApplication(appId, { status: newStage });
            App.showToast(`Application moved to ${newStage.toUpperCase()}`, 'success');
            
            // Celebration confetti on offer/selected!
            if (newStage === 'selected' && window.confetti) {
              confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } });
            }

            await TrackerView.fetchAndRenderKanban();
          } catch (err) {
            App.showToast(err.message, 'error');
          }
        }
      });
    });
  },

  async showAddApplicationModal() {
    const jobs = await API.getJobs();
    const content = `
      <div style="display:flex; flex-direction:column; gap:16px;">
        <div class="form-group">
          <label class="form-label">Select Opportunity:</label>
          <select id="modal-add-job-select" class="input-field">
            ${jobs.map(j => `<option value="${j.job_id}">${j.title} - ${j.company}</option>`).join('')}
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Initial Stage:</label>
          <select id="modal-add-stage-select" class="input-field">
            <option value="saved">Saved</option>
            <option value="applied">Applied</option>
            <option value="assessment">Assessment</option>
            <option value="interview">Interview</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Application Notes / Reminder:</label>
          <textarea id="modal-add-notes" class="input-field" rows="3" placeholder="e.g. Applied through internal portal, referral from LinkedIn..."></textarea>
        </div>
      </div>
    `;

    App.showModal('Add Application to Kanban Pipeline', content, async () => {
      const jobId = parseInt(document.getElementById('modal-add-job-select').value);
      const status = document.getElementById('modal-add-stage-select').value;
      const notes = document.getElementById('modal-add-notes').value;

      try {
        await API.createApplication({ job_id: jobId, status: status, notes: notes });
        App.showToast('Application added to pipeline!', 'success');
        await TrackerView.fetchAndRenderKanban();
      } catch (err) {
        App.showToast(err.message, 'error');
      }
    }, 'Add to Tracker');
  },

  async editApplication(appId) {
    const app = this.applications.find(a => a.application_id === appId);
    if (!app) return;

    const content = `
      <div style="display:flex; flex-direction:column; gap:16px;">
        <div class="form-group">
          <label class="form-label">Stage:</label>
          <select id="modal-edit-stage-select" class="input-field">
            ${this.stages.map(s => `<option value="${s.id}" ${app.status === s.id ? 'selected' : ''}>${s.name}</option>`).join('')}
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Notes:</label>
          <textarea id="modal-edit-notes" class="input-field" rows="3">${app.notes || ''}</textarea>
        </div>
      </div>
    `;

    App.showModal('Edit Application Details', content, async () => {
      const newStatus = document.getElementById('modal-edit-stage-select').value;
      const newNotes = document.getElementById('modal-edit-notes').value;

      try {
        await API.updateApplication(appId, { status: newStatus, notes: newNotes });
        App.showToast('Application updated!', 'success');
        await TrackerView.fetchAndRenderKanban();
      } catch (err) {
        App.showToast(err.message, 'error');
      }
    }, 'Save Updates');
  },

  async deleteApp(appId) {
    if (confirm('Are you sure you want to remove this opportunity from your tracker?')) {
      try {
        await API.deleteApplication(appId);
        App.showToast('Application deleted', 'info');
        await this.fetchAndRenderKanban();
      } catch (err) {
        App.showToast(err.message, 'error');
      }
    }
  }
};
