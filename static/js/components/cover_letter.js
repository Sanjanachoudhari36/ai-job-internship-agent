/**
 * Cover Letter Agent Component - Personalized Cover Letter Generator & Editor
 */
const CoverLetterView = {
  jobsList: [],

  async render(container) {
    container.innerHTML = `
      <div style="display:grid; grid-template-columns: 1fr 1.3fr; gap: 24px;">
        <!-- Left: Configuration & Prompts -->
        <div style="display:flex; flex-direction:column; gap:20px;">
          <div class="glass-card">
            <div class="card-header">
              <h3 class="card-title"><i class="fa-solid fa-envelope-open-text" style="color:#06b6d4;"></i> Cover Letter Agent</h3>
            </div>

            <div class="form-group">
              <label class="form-label">Select Target Opportunity:</label>
              <select id="cl-job-select" class="input-field">
                <option value="">-- Or enter custom company & role --</option>
              </select>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
              <div class="form-group">
                <label class="form-label">Company Name:</label>
                <input type="text" id="cl-company" class="input-field" placeholder="e.g., Pythonic AI Labs">
              </div>
              <div class="form-group">
                <label class="form-label">Job Title / Role:</label>
                <input type="text" id="cl-role" class="input-field" placeholder="e.g., Python Developer Intern">
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Tone & Style:</label>
              <select id="cl-tone" class="input-field">
                <option value="Professional and Enthusiastic">Professional & Enthusiastic (Recommended)</option>
                <option value="Confident and Highly Technical">Confident & Highly Technical</option>
                <option value="Direct, Impact-Driven and Concise">Direct & Concise</option>
                <option value="Creative and Passionate">Creative & Passionate</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Custom Highlights / Key Projects to Emphasize:</label>
              <textarea id="cl-highlights" class="input-field" rows="3" placeholder="e.g., Mention my experience building FastAPI backends and 35% performance optimizations..."></textarea>
            </div>

            <button class="btn btn-primary" id="btn-generate-cover-letter" style="width:100%;">
              <i class="fa-solid fa-wand-magic-sparkles"></i> Generate Custom Cover Letter
            </button>
          </div>
        </div>

        <!-- Right: Generated Document Editor -->
        <div class="glass-card" style="display:flex; flex-direction:column; min-height:550px;">
          <div class="card-header">
            <h3 class="card-title" style="font-size:1rem;"><i class="fa-solid fa-file-lines" style="color:#818cf8;"></i> Generated Cover Letter</h3>
            <div style="display:flex; gap:8px;">
              <button class="btn btn-secondary btn-sm" id="btn-copy-cover-letter" title="Copy to Clipboard">
                <i class="fa-regular fa-copy"></i> Copy
              </button>
              <button class="btn btn-secondary btn-sm" id="btn-download-cover-letter" title="Download Text">
                <i class="fa-solid fa-download"></i> Export
              </button>
            </div>
          </div>

          <div style="flex:1; display:flex; flex-direction:column; position:relative;">
            <textarea id="cover-letter-output" class="input-field" style="flex:1; height:420px; font-family:'Inter', sans-serif; line-height:1.7; font-size:0.9rem; resize:none;" placeholder="Your personalized, high-converting cover letter will appear here ready to review and edit..."></textarea>
          </div>
        </div>
      </div>
    `;

    await this.init(container);
  },

  async init(container) {
    try {
      this.jobsList = await API.getJobs();
      const select = container.querySelector('#cl-job-select');
      this.jobsList.forEach(job => {
        const opt = document.createElement('option');
        opt.value = job.job_id;
        opt.textContent = `${job.title} - ${job.company}`;
        select.appendChild(opt);
      });

      select.addEventListener('change', () => {
        const selectedId = parseInt(select.value);
        const job = this.jobsList.find(j => j.job_id === selectedId);
        if (job) {
          container.querySelector('#cl-company').value = job.company;
          container.querySelector('#cl-role').value = job.title;
        }
      });
    } catch (e) {
      console.warn('Failed to load jobs in cover letter view:', e);
    }

    const genBtn = container.querySelector('#btn-generate-cover-letter');
    genBtn.addEventListener('click', async () => {
      await this.generateLetter(container);
    });

    const copyBtn = container.querySelector('#btn-copy-cover-letter');
    copyBtn.addEventListener('click', () => {
      const output = container.querySelector('#cover-letter-output');
      if (output && output.value) {
        navigator.clipboard.writeText(output.value);
        App.showToast('Cover letter copied to clipboard!', 'success');
      }
    });

    const downloadBtn = container.querySelector('#btn-download-cover-letter');
    downloadBtn.addEventListener('click', () => {
      const output = container.querySelector('#cover-letter-output');
      if (output && output.value) {
        const blob = new Blob([output.value], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Cover_Letter_${(container.querySelector('#cl-company').value || 'Application').replace(/\s+/g, '_')}.txt`;
        a.click();
        URL.revokeObjectURL(url);
      }
    });
  },

  async generateLetter(container) {
    const jobSelect = container.querySelector('#cl-job-select');
    const comp = container.querySelector('#cl-company').value;
    const role = container.querySelector('#cl-role').value;
    const tone = container.querySelector('#cl-tone').value;
    const highlights = container.querySelector('#cl-highlights').value;
    const output = container.querySelector('#cover-letter-output');

    output.value = "AI Cover Letter Agent synthesizing candidate background and company mission...\nPlease wait...";

    try {
      const res = await API.generateCoverLetter({
        job_id: jobSelect.value ? parseInt(jobSelect.value) : null,
        company_name: comp,
        job_title: role,
        tone: tone,
        key_highlights: highlights
      });

      output.value = res.cover_letter;
      App.showToast('Personalized cover letter generated!', 'success');
    } catch (err) {
      output.value = `Error generating cover letter: ${err.message}`;
      App.showToast(err.message, 'error');
    }
  }
};
