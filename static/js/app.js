/**
 * Main Single Page Application Orchestrator & Router
 */
const App = {
  currentView: 'dashboard',
  views: {
    dashboard: { component: DashboardView, title: 'AI Career Dashboard', subtitle: 'Overview of matches, active applications, deadlines and agent telemetry', icon: 'fa-chart-pie' },
    jobs: { component: JobsView, title: 'Opportunity Discovery & Matcher', subtitle: 'Search, filter and score compatibility across job and internship sources', icon: 'fa-briefcase' },
    orchestrator: { component: OrchestratorView, title: 'Multi-Agent Pipeline Visualizer', subtitle: 'Real-time telemetry and state coordination of all 7 specialized AI agents', icon: 'fa-network-wired' },
    resume: { component: ResumeView, title: 'AI Resume Studio & ATS Analyzer', subtitle: 'ATS keyword optimization, gap identification and impact-driven tailoring', icon: 'fa-file-lines' },
    'cover-letter': { component: CoverLetterView, title: 'Personalized Cover Letter Agent', subtitle: 'Synthesize profile strengths, resume background, and job requirements', icon: 'fa-envelope-open-text' },
    tracker: { component: TrackerView, title: 'Application Kanban & Deadline Tracker', subtitle: 'Pipeline stages, interview schedule tracking and deadline management', icon: 'fa-table-columns' },
    interview: { component: InterviewView, title: 'AI Mock Interview Simulator', subtitle: 'Role-specific question generation, speech practice and instant answer grading', icon: 'fa-microphone-lines' },
    profile: { component: ProfileView, title: 'Candidate Profile & Career Goals', subtitle: 'Education, skill matrix, projects, target roles and preferred locations', icon: 'fa-user-gear' }
  },

  modalCallback: null,

  async init() {
    this.setupNavigation();
    this.setupGlobalActions();
    this.setupModal();

    // Auto-login demo candidate
    if (!API.getToken()) {
      await API.autoDemoLogin();
    }

    try {
      const profile = await API.getProfile();
      this.updateUserBadge(profile.name, profile.email);
    } catch (e) {
      console.warn('Init profile load:', e);
    }

    // Default route
    this.navigate('dashboard');
  },

  setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const viewId = item.dataset.view;
        if (viewId) {
          this.navigate(viewId);
        }
      });
    });
  },

  setupGlobalActions() {
    // Quick sync button
    const syncBtn = document.getElementById('btn-quick-sync');
    if (syncBtn) {
      syncBtn.addEventListener('click', async () => {
        this.showToast('Recalculating 6-factor compatibility scores across all jobs...', 'info');
        this.navigate(this.currentView);
      });
    }

    // Trigger orchestrator button
    const orchBtn = document.getElementById('btn-trigger-orchestrator');
    if (orchBtn) {
      orchBtn.addEventListener('click', () => {
        this.navigate('orchestrator');
      });
    }

    // Logout / Account Switcher
    const logoutBtn = document.getElementById('btn-logout');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', () => {
        this.showAuthModal();
      });
    }
  },

  navigate(viewName) {
    if (!this.views[viewName]) return;

    this.currentView = viewName;
    const viewConfig = this.views[viewName];

    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(item => {
      if (item.dataset.view === viewName) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });

    // Update header
    const titleElem = document.getElementById('view-header-title');
    const subtitleElem = document.getElementById('view-header-subtitle');
    if (titleElem && subtitleElem) {
      titleElem.innerHTML = `<i class="fa-solid ${viewConfig.icon}" style="color:#818cf8;"></i> ${viewConfig.title}`;
      subtitleElem.textContent = viewConfig.subtitle;
    }

    // Render component
    const container = document.getElementById('view-container');
    if (container && viewConfig.component) {
      viewConfig.component.render(container);
    }
  },

  runPipelineForJob(jobId) {
    this.navigate('orchestrator');
    setTimeout(() => {
      const container = document.getElementById('view-container');
      if (container && OrchestratorView.runPipeline) {
        OrchestratorView.runPipeline(container, jobId);
      }
    }, 150);
  },

  updateUserBadge(name, email) {
    const nameElem = document.getElementById('sidebar-username');
    const emailElem = document.getElementById('sidebar-useremail');
    const avatarElem = document.getElementById('sidebar-avatar');

    if (nameElem) nameElem.textContent = name || 'Student User';
    if (emailElem) emailElem.textContent = email || 'student@example.com';
    if (avatarElem) {
      const initials = (name || 'AM').split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
      avatarElem.textContent = initials;
    }
  },

  /* Modal Helpers */
  setupModal() {
    const backdrop = document.getElementById('app-modal');
    const closeBtn = document.getElementById('modal-close-btn');
    const cancelBtn = document.getElementById('modal-cancel-btn');
    const submitBtn = document.getElementById('modal-submit-btn');

    const closeModal = () => {
      backdrop.classList.remove('active');
      this.modalCallback = null;
    };

    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) closeModal();
    });

    submitBtn.addEventListener('click', () => {
      if (this.modalCallback) {
        this.modalCallback();
      }
      closeModal();
    });
  },

  showModal(title, bodyHtml, onSubmit = null, submitText = 'Save Changes') {
    const backdrop = document.getElementById('app-modal');
    const titleElem = document.getElementById('modal-title');
    const bodyElem = document.getElementById('modal-body');
    const submitBtn = document.getElementById('modal-submit-btn');

    titleElem.textContent = title;
    bodyElem.innerHTML = bodyHtml;
    submitBtn.textContent = submitText;

    if (onSubmit) {
      submitBtn.style.display = 'inline-flex';
      this.modalCallback = onSubmit;
    } else {
      submitBtn.style.display = 'none';
    }

    backdrop.classList.add('active');
  },

  showAuthModal() {
    const content = `
      <div style="display:flex; flex-direction:column; gap:16px;">
        <p style="font-size:0.85rem; color:var(--text-secondary);">
          Login with an existing account or register a new candidate profile:
        </p>
        <div class="form-group">
          <label class="form-label">Email Address:</label>
          <input type="email" id="auth-modal-email" class="input-field" value="student@example.com">
        </div>
        <div class="form-group">
          <label class="form-label">Password:</label>
          <input type="password" id="auth-modal-password" class="input-field" value="password123">
        </div>
        <div style="display:flex; gap:10px;">
          <button class="btn btn-primary btn-sm" id="auth-btn-login" style="flex:1;">Login</button>
          <button class="btn btn-secondary btn-sm" id="auth-btn-register" style="flex:1;">Register New</button>
        </div>
      </div>
    `;

    this.showModal('Account Management', content, null);

    setTimeout(() => {
      document.getElementById('auth-btn-login').addEventListener('click', async () => {
        const email = document.getElementById('auth-modal-email').value;
        const pass = document.getElementById('auth-modal-password').value;
        try {
          await API.login(email, pass);
          App.showToast('Logged in successfully!', 'success');
          document.getElementById('app-modal').classList.remove('active');
          const p = await API.getProfile();
          App.updateUserBadge(p.name, p.email);
          App.navigate(App.currentView);
        } catch (err) {
          App.showToast(err.message, 'error');
        }
      });

      document.getElementById('auth-btn-register').addEventListener('click', async () => {
        const email = document.getElementById('auth-modal-email').value;
        const pass = document.getElementById('auth-modal-password').value;
        const name = prompt('Enter candidate full name:', 'Alex Morgan') || 'New Candidate';
        try {
          await API.register(name, email, pass);
          App.showToast('Registered & logged in!', 'success');
          document.getElementById('app-modal').classList.remove('active');
          const p = await API.getProfile();
          App.updateUserBadge(p.name, p.email);
          App.navigate('profile');
        } catch (err) {
          App.showToast(err.message, 'error');
        }
      });
    }, 100);
  },

  /* Toast Notification */
  showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icon = type === 'success' ? 'fa-circle-check' : type === 'error' ? 'fa-circle-exclamation' : 'fa-circle-info';

    toast.innerHTML = `
      <i class="fa-solid ${icon}" style="color:${type === 'success' ? '#10b981' : type === 'error' ? '#f43f5e' : '#6366f1'}; font-size:1.1rem;"></i>
      <span style="font-size:0.85rem; font-weight:500;">${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(50px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }
};

// Initialize Application on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
