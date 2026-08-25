/**
 * AI Mock Interview Simulator Component - Interactive Prep & Instant Feedback
 */
const InterviewView = {
  currentQuestions: [],
  currentIndex: 0,
  evaluations: [],
  isRecording: false,
  speechRecognition: null,

  async render(container) {
    container.innerHTML = `
      <div style="display:grid; grid-template-columns: 1fr 2fr; gap: 24px;">
        <!-- Left: Configuration & Question List -->
        <div style="display:flex; flex-direction:column; gap:20px;">
          <div class="glass-card">
            <div class="card-header">
              <h3 class="card-title"><i class="fa-solid fa-microphone-lines" style="color:#10b981;"></i> Mock Setup</h3>
            </div>

            <div class="form-group">
              <label class="form-label">Target Role Title:</label>
              <input type="text" id="interview-role" class="input-field" value="Python Developer Intern" placeholder="e.g. Full Stack AI Engineer">
            </div>

            <div class="form-group">
              <label class="form-label">Target Company Name:</label>
              <input type="text" id="interview-company" class="input-field" value="Pythonic AI Labs" placeholder="e.g. NextGen Cloud Systems">
            </div>

            <div class="form-group">
              <label class="form-label">Number of Questions:</label>
              <select id="interview-count" class="input-field">
                <option value="3">3 Rapid Fire Questions</option>
                <option value="5" selected>5 Full Round Questions</option>
                <option value="7">7 Deep Dive Questions</option>
              </select>
            </div>

            <button class="btn btn-primary" id="btn-generate-questions" style="width:100%;">
              <i class="fa-solid fa-wand-magic-sparkles"></i> Generate AI Interview Questions
            </button>
          </div>

          <!-- Question Navigator Card -->
          <div class="glass-card" id="interview-nav-card" style="display:none;">
            <div class="card-header" style="margin-bottom:12px;">
              <h4 class="card-title" style="font-size:0.95rem;">Question Navigator</h4>
              <span id="interview-progress-pill" style="font-size:0.8rem; color:var(--accent-emerald); font-weight:700;">1 / 5</span>
            </div>
            <div id="interview-nav-pills" style="display:flex; flex-direction:column; gap:8px;">
              <!-- Dynamic Pill Items -->
            </div>
          </div>
        </div>

        <!-- Right: Interactive Terminal & Feedback Panel -->
        <div id="interview-terminal-container">
          <div class="glass-card" style="text-align:center; padding:60px 24px; min-height:500px; display:flex; flex-direction:column; align-items:center; justify-content:center;">
            <i class="fa-solid fa-headset fa-3x" style="color:var(--text-muted); margin-bottom:16px;"></i>
            <h3 style="font-size:1.2rem;">AI Mock Interview Terminal</h3>
            <p style="font-size:0.85rem; color:var(--text-muted); max-width:400px; margin-top:8px;">
              Click 'Generate AI Interview Questions' on the left to start a personalized technical and behavioral mock interview session.
            </p>
          </div>
        </div>
      </div>
    `;

    this.initEvents(container);
  },

  initEvents(container) {
    const genBtn = container.querySelector('#btn-generate-questions');
    genBtn.addEventListener('click', async () => {
      await this.startInterviewSession(container);
    });

    // Initialize Web Speech API if supported
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      this.speechRecognition = new SpeechRecognition();
      this.speechRecognition.continuous = true;
      this.speechRecognition.interimResults = true;

      this.speechRecognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          transcript += event.results[i][0].transcript;
        }
        const answerBox = document.getElementById('interview-answer-input');
        if (answerBox) {
          answerBox.value += ' ' + transcript;
        }
      };
    }
  },

  async startInterviewSession(container) {
    const role = container.querySelector('#interview-role').value;
    const company = container.querySelector('#interview-company').value;
    const count = parseInt(container.querySelector('#interview-count').value);
    const terminal = container.querySelector('#interview-terminal-container');

    terminal.innerHTML = `
      <div class="glass-card" style="text-align:center; padding:60px 24px;">
        <i class="fa-solid fa-circle-notch fa-spin fa-3x" style="color:#10b981; margin-bottom:16px;"></i>
        <h3>AI Interview Agent is preparing questions for ${role}...</h3>
        <p style="font-size:0.85rem; color:var(--text-muted); margin-top:8px;">Synthesizing technical challenges, behavioral STAR questions, and company culture checks...</p>
      </div>
    `;

    try {
      this.currentQuestions = await API.generateInterviewQuestions({
        role_title: role,
        company_name: company,
        count: count
      });
      this.currentIndex = 0;
      this.evaluations = [];

      container.querySelector('#interview-nav-card').style.display = 'block';
      this.renderQuestionView();
      this.updateNavigator();
    } catch (err) {
      terminal.innerHTML = `
        <div class="glass-card" style="color:#f43f5e;">
          <i class="fa-solid fa-triangle-exclamation"></i> Failed to generate interview questions: ${err.message}
        </div>
      `;
    }
  },

  renderQuestionView() {
    const q = this.currentQuestions[this.currentIndex];
    const terminal = document.getElementById('interview-terminal-container');
    if (!q || !terminal) return;

    const role = document.getElementById('interview-role').value;
    const company = document.getElementById('interview-company').value;

    terminal.innerHTML = `
      <div style="display:flex; flex-direction:column; gap:20px;">
        <!-- Question Display Card -->
        <div class="glass-card" style="border-left: 4px solid var(--primary);">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <div style="display:flex; gap:8px;">
              <span class="badge badge-internship">${q.category}</span>
              <span class="badge badge-score">${q.difficulty}</span>
            </div>
            <button class="btn btn-secondary btn-sm" id="btn-speak-question" title="Read Question Out Loud">
              <i class="fa-solid fa-volume-high"></i> Listen
            </button>
          </div>

          <h3 style="font-size:1.15rem; font-weight:700; line-height:1.5; color:#ffffff; margin-bottom:10px;">
            ${q.question}
          </h3>

          <p style="font-size:0.82rem; color:var(--text-muted); line-height:1.4;">
            <i class="fa-solid fa-circle-info"></i> Context: ${q.context}
          </p>
        </div>

        <!-- Candidate Response Terminal -->
        <div class="glass-card">
          <div class="card-header" style="margin-bottom:12px;">
            <h4 class="card-title" style="font-size:0.95rem;">Your Spoken / Typed Response:</h4>
            <div style="display:flex; gap:8px;">
              <button class="btn btn-secondary btn-sm" id="btn-mic-toggle" style="color:${this.isRecording ? '#f43f5e' : 'inherit'};">
                <i class="fa-solid fa-microphone"></i> ${this.isRecording ? 'Listening...' : 'Voice Dictate'}
              </button>
            </div>
          </div>

          <textarea id="interview-answer-input" class="input-field" style="height:140px; font-size:0.9rem; line-height:1.6; resize:none;" placeholder="Type your answer here or use the voice dictate button to speak your response..."></textarea>

          <div style="display:flex; justify-content:flex-end; margin-top:14px;">
            <button class="btn btn-primary" id="btn-submit-answer">
              <i class="fa-solid fa-paper-plane"></i> Submit Answer for AI Evaluation
            </button>
          </div>
        </div>

        <!-- Evaluation Results Container -->
        <div id="evaluation-result-box"></div>
      </div>
    `;

    // Event listeners
    const speakBtn = document.getElementById('btn-speak-question');
    speakBtn.addEventListener('click', () => {
      this.speakText(q.question);
    });

    const micBtn = document.getElementById('btn-mic-toggle');
    micBtn.addEventListener('click', () => {
      this.toggleMicrophone(micBtn);
    });

    const submitBtn = document.getElementById('btn-submit-answer');
    submitBtn.addEventListener('click', async () => {
      await this.evaluateCurrentAnswer(q, role, company);
    });
  },

  speakText(text) {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    } else {
      App.showToast('Speech synthesis not supported in this browser.', 'info');
    }
  },

  toggleMicrophone(btn) {
    if (!this.speechRecognition) {
      App.showToast('Voice dictation requires Google Chrome or Chromium browser.', 'info');
      return;
    }

    if (!this.isRecording) {
      this.speechRecognition.start();
      this.isRecording = true;
      btn.style.color = '#f43f5e';
      btn.innerHTML = '<i class="fa-solid fa-microphone-slash"></i> Stop Recording';
      App.showToast('Microphone activated. Speak clearly into your mic.', 'info');
    } else {
      this.speechRecognition.stop();
      this.isRecording = false;
      btn.style.color = 'inherit';
      btn.innerHTML = '<i class="fa-solid fa-microphone"></i> Voice Dictate';
    }
  },

  async evaluateCurrentAnswer(q, role, company) {
    const answer = document.getElementById('interview-answer-input').value;
    const evalBox = document.getElementById('evaluation-result-box');

    evalBox.innerHTML = `
      <div class="glass-card" style="text-align:center; padding:30px;">
        <i class="fa-solid fa-circle-notch fa-spin fa-2x" style="color:#10b981; margin-bottom:12px;"></i>
        <div>Evaluating response depth, technical accuracy & STAR alignment...</div>
      </div>
    `;

    try {
      const evalRes = await API.evaluateInterviewAnswer({
        question_id: q.id,
        question: q.question,
        category: q.category,
        user_answer: answer,
        role_title: role,
        company_name: company
      });

      this.evaluations[this.currentIndex] = evalRes;
      this.renderEvaluationReport(evalBox, evalRes);
      this.updateNavigator();
    } catch (err) {
      evalBox.innerHTML = `<div class="glass-card" style="color:#f43f5e;">Evaluation error: ${err.message}</div>`;
    }
  },

  renderEvaluationReport(container, evalRes) {
    container.innerHTML = `
      <div class="glass-card" style="border: 1px solid rgba(16, 185, 129, 0.4); animation: fadeIn 0.4s ease-in-out;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
          <div>
            <div style="font-size:0.8rem; color:var(--text-muted); text-transform:uppercase; font-weight:700;">AI Answer Score</div>
            <h3 style="font-size:1.8rem; font-weight:800; color:${evalRes.score >= 80 ? '#34d399' : '#fbbf24'};">
              ${evalRes.score}<span style="font-size:1rem; color:var(--text-muted);">/100</span>
            </h3>
          </div>
          <button class="btn btn-primary btn-sm" id="btn-next-question">
            ${this.currentIndex < this.currentQuestions.length - 1 ? 'Next Question →' : 'Complete Session 🎉'}
          </button>
        </div>

        <p style="font-size:0.88rem; color:var(--text-primary); margin-bottom:16px; line-height:1.5;">
          ${evalRes.feedback}
        </p>

        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:14px; margin-bottom:16px;">
          <div style="background:rgba(16,185,129,0.1); border-left:3px solid #10b981; padding:10px 14px; border-radius:var(--radius-sm);">
            <div style="font-size:0.8rem; font-weight:700; color:#34d399; margin-bottom:4px;">Key Strengths:</div>
            <ul style="font-size:0.8rem; color:var(--text-primary); padding-left:18px; margin:0;">
              ${evalRes.strengths.map(s => `<li>${s}</li>`).join('')}
            </ul>
          </div>

          <div style="background:rgba(245,158,11,0.1); border-left:3px solid #f59e0b; padding:10px 14px; border-radius:var(--radius-sm);">
            <div style="font-size:0.8rem; font-weight:700; color:#fbbf24; margin-bottom:4px;">Improvement Tips:</div>
            <ul style="font-size:0.8rem; color:var(--text-primary); padding-left:18px; margin:0;">
              ${evalRes.tips_for_improvement.map(t => `<li>${t}</li>`).join('')}
            </ul>
          </div>
        </div>

        <!-- Model Answer Accordion -->
        <div style="background:rgba(15,23,42,0.7); border:1px solid var(--border-glass); border-radius:var(--radius-md); padding:12px 16px;">
          <div style="font-size:0.82rem; font-weight:700; color:#818cf8; margin-bottom:4px;">
            <i class="fa-solid fa-graduation-cap"></i> Ideal Model Answer:
          </div>
          <p style="font-size:0.84rem; color:var(--text-secondary); line-height:1.6; margin:0;">
            ${evalRes.model_answer}
          </p>
        </div>
      </div>
    `;

    document.getElementById('btn-next-question').addEventListener('click', () => {
      if (this.currentIndex < this.currentQuestions.length - 1) {
        this.currentIndex++;
        this.renderQuestionView();
        this.updateNavigator();
      } else {
        App.showToast('Mock Interview Session Completed! Fantastic practice.', 'success');
        if (window.confetti) confetti();
      }
    });
  },

  updateNavigator() {
    const navPills = document.getElementById('interview-nav-pills');
    const pill = document.getElementById('interview-progress-pill');
    if (!navPills) return;

    pill.textContent = `${this.currentIndex + 1} / ${this.currentQuestions.length}`;

    navPills.innerHTML = this.currentQuestions.map((q, idx) => {
      const evaluation = this.evaluations[idx];
      const isCurrent = idx === this.currentIndex;
      const isDone = !!evaluation;

      return `
        <div style="display:flex; align-items:center; justify-content:space-between; background:${isCurrent ? 'rgba(99,102,241,0.2)' : 'rgba(15,23,42,0.6)'}; border:1px solid ${isCurrent ? 'rgba(99,102,241,0.4)' : 'var(--border-glass)'}; padding:8px 12px; border-radius:var(--radius-sm); cursor:pointer; transition:var(--transition);" onclick="InterviewView.switchQuestion(${idx})">
          <div style="font-size:0.8rem; font-weight:600; color:${isCurrent ? '#ffffff' : 'var(--text-secondary)'}; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:180px;">
            Q${idx + 1}: ${q.category}
          </div>
          <div>
            ${isDone ? `<span class="badge badge-score high" style="font-size:0.7rem;">${evaluation.score}%</span>` : `<span style="font-size:0.75rem; color:var(--text-muted);">${isCurrent ? 'Current' : 'Pending'}</span>`}
          </div>
        </div>
      `;
    }).join('');
  },

  switchQuestion(index) {
    this.currentIndex = index;
    this.renderQuestionView();
    this.updateNavigator();
  }
};
