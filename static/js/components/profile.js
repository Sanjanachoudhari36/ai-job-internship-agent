/**
 * Candidate Profile & Skills Manager Component
 */
const ProfileView = {
  profileData: null,

  async render(container) {
    container.innerHTML = `
      <div style="display:flex; justify-content:center; padding:40px;">
        <i class="fa-solid fa-circle-notch fa-spin fa-2x" style="color:#6366f1;"></i>
      </div>
    `;

    try {
      this.profileData = await API.getProfile();
      const p = this.profileData;

      container.innerHTML = `
        <div class="profile-shell" style="max-width: 900px; margin: 0 auto; display:flex; flex-direction:column; gap:24px;">
          <div class="glass-card">
            <div class="card-header">
              <h3 class="card-title"><i class="fa-solid fa-id-card" style="color:#6366f1;"></i> Candidate Profile & Career Preferences</h3>
              <button class="btn btn-primary btn-sm" id="btn-save-profile">
                <i class="fa-solid fa-floppy-disk"></i> Save Profile
              </button>
            </div>

            <!-- Basic Info Row -->
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
              <div class="form-group">
                <label class="form-label">Full Name:</label>
                <input type="text" id="prof-name" class="input-field" value="${p.name || ''}">
              </div>
              <div class="form-group">
                <label class="form-label">Email Address:</label>
                <input type="email" id="prof-email" class="input-field" value="${p.email || ''}" disabled style="opacity:0.7;">
              </div>
            </div>

            <!-- Education & Graduation -->
            <div class="profile-form-row" style="display:grid; grid-template-columns: 2fr 1fr; gap:16px;">
              <div class="form-group">
                <label class="form-label">Education / Major:</label>
                <input type="text" id="prof-education" class="input-field" value="${p.education || ''}" placeholder="e.g. B.Tech in Computer Science & Engineering">
              </div>
              <div class="form-group">
                <label class="form-label">Graduation Year:</label>
                <input type="number" id="prof-grad-year" class="input-field" value="${p.graduation_year || 2026}">
              </div>
            </div>

            <!-- Skills Chip Manager -->
            <div class="form-group">
              <label class="form-label">Technical & Core Skills:</label>
              <div style="display:flex; gap:8px; margin-bottom:10px;">
                <input type="text" id="skill-add-input" class="input-field" placeholder="Add a skill (e.g., Python, Docker, PyTorch) and press Add...">
                <button class="btn btn-secondary btn-sm" id="btn-add-skill-tag" type="button">
                  <i class="fa-solid fa-plus"></i> Add
                </button>
              </div>
              <div id="profile-skills-chips" style="display:flex; flex-wrap:wrap; gap:8px; min-height:40px; background:rgba(15,23,42,0.5); padding:10px; border-radius:var(--radius-md); border:1px solid var(--border-glass);">
                ${(p.skills || []).map(skill => `
                  <span class="tag" style="background:rgba(99,102,241,0.2); border-color:rgba(99,102,241,0.4); color:#c7d2fe; padding:6px 12px; font-size:0.82rem;">
                    ${skill}
                    <i class="fa-solid fa-xmark" style="cursor:pointer; margin-left:6px;" onclick="ProfileView.removeSkill('${skill}')"></i>
                  </span>
                `).join('')}
              </div>
            </div>

            <!-- Target Roles & Preferred Locations -->
            <div class="profile-form-grid" style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
              <div class="form-group">
                <label class="form-label">Preferred Target Roles (comma separated):</label>
                <input type="text" id="prof-roles" class="input-field" value="${(p.preferred_roles || []).join(', ')}" placeholder="e.g. Python Developer, Full Stack Engineer, AI Engineer">
              </div>
              <div class="form-group">
                <label class="form-label">Preferred Locations (comma separated):</label>
                <input type="text" id="prof-locations" class="input-field" value="${(p.preferred_locations || []).join(', ')}" placeholder="e.g. Remote, San Francisco, CA, Bengaluru">
              </div>
            </div>

            <!-- Experience & Projects -->
            <div class="form-group">
              <label class="form-label">Professional & Internship Experience Summary:</label>
              <textarea id="prof-experience" class="input-field" rows="3" placeholder="Briefly describe past internships, freelance work, or relevant lab experience...">${p.experience || ''}</textarea>
            </div>

            <div class="form-group">
              <label class="form-label">Key Projects (Used by Match & Resume Agents):</label>
              <textarea id="prof-projects" class="input-field" rows="3" placeholder="Describe your key technical projects with measurable outcomes...">${p.projects || ''}</textarea>
            </div>

            <!-- Resume Raw Text -->
            <div class="form-group">
              <label class="form-label">Parsed Resume Content:</label>
              <textarea id="prof-resume-text" class="input-field" rows="5" style="font-family:'JetBrains Mono', monospace; font-size:0.8rem;">${p.resume_text || ''}</textarea>
            </div>
          </div>
        </div>
      `;

      this.initEvents(container);
    } catch (err) {
      container.innerHTML = `<div class="glass-card" style="color:#f43f5e;">Error loading profile: ${err.message}</div>`;
    }
  },

  initEvents(container) {
    const saveBtn = container.querySelector('#btn-save-profile');
    saveBtn.addEventListener('click', async () => {
      await this.saveProfile(container);
    });

    const addSkillBtn = container.querySelector('#btn-add-skill-tag');
    const skillInput = container.querySelector('#skill-add-input');

    const addSkill = () => {
      const val = skillInput.value.trim();
      if (val && !this.profileData.skills.includes(val)) {
        this.profileData.skills.push(val);
        skillInput.value = '';
        this.renderSkillsChips();
      }
    };

    addSkillBtn.addEventListener('click', addSkill);
    skillInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        addSkill();
      }
    });
  },

  removeSkill(skillName) {
    if (this.profileData && this.profileData.skills) {
      this.profileData.skills = this.profileData.skills.filter(s => s !== skillName);
      this.renderSkillsChips();
    }
  },

  renderSkillsChips() {
    const chipsContainer = document.getElementById('profile-skills-chips');
    if (!chipsContainer) return;

    chipsContainer.innerHTML = (this.profileData.skills || []).map(skill => `
      <span class="tag" style="background:rgba(99,102,241,0.2); border-color:rgba(99,102,241,0.4); color:#c7d2fe; padding:6px 12px; font-size:0.82rem;">
        ${skill}
        <i class="fa-solid fa-xmark" style="cursor:pointer; margin-left:6px;" onclick="ProfileView.removeSkill('${skill}')"></i>
      </span>
    `).join('');
  },

  async saveProfile(container) {
    const name = container.querySelector('#prof-name').value;
    const education = container.querySelector('#prof-education').value;
    const gradYear = parseInt(container.querySelector('#prof-grad-year').value);
    const rolesStr = container.querySelector('#prof-roles').value;
    const locsStr = container.querySelector('#prof-locations').value;
    const experience = container.querySelector('#prof-experience').value;
    const projects = container.querySelector('#prof-projects').value;
    const resumeText = container.querySelector('#prof-resume-text').value;

    const payload = {
      name: name,
      education: education,
      graduation_year: isNaN(gradYear) ? null : gradYear,
      skills: this.profileData.skills || [],
      preferred_roles: rolesStr.split(',').map(s => s.strip ? s.strip() : s.trim()).filter(Boolean),
      preferred_locations: locsStr.split(',').map(s => s.strip ? s.strip() : s.trim()).filter(Boolean),
      experience: experience,
      projects: projects,
      resume_text: resumeText
    };

    try {
      await API.updateProfile(payload);
      App.showToast('Profile updated successfully! AI Match scores updated.', 'success');
      App.updateUserBadge(name, this.profileData.email);
    } catch (err) {
      App.showToast(err.message, 'error');
    }
  }
};
