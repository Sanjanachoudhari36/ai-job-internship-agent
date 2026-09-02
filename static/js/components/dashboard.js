/**
 * Dashboard View Component - Conforming to Section 7 of Specification Sheet
 */
const DashboardView = {
  chartInstance: null,

  async render(container) {
    container.innerHTML = `
      <div style="display:flex; justify-content:center; padding:40px;">
        <i class="fa-solid fa-circle-notch fa-spin fa-2x" style="color:#6366f1;"></i>
      </div>
    `;

    try {
      const data = await API.getDashboardAnalytics();
      const best = data.best_match;
      const good = data.good_match;
      const breakdown = data.applications_breakdown || {};
      const deadlines = data.upcoming_deadlines || [];
      const interviews = data.upcoming_interviews || [];
      const formatDate = (value, fallback = 'Date not set') => {
        if (!value) return fallback;
        const date = new Date(value);
        return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString(undefined, {
          day: 'numeric', month: 'short', year: 'numeric'
        });
      };
      const formatInterviewDate = (value) => {
        if (!value) return 'Time not set';
        const date = new Date(value);
        return Number.isNaN(date.getTime()) ? value : date.toLocaleString(undefined, {
          day: 'numeric', month: 'short', year: 'numeric', hour: 'numeric', minute: '2-digit'
        });
      };
      const matchTitle = (match) => match ? `${match.title} (${match.company})` : 'No match available';
      const renderEvents = () => {
        const eventMarkup = [
          ...deadlines.map(event => `
            <div style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid #f59e0b; padding: 10px 12px; border-radius: var(--radius-sm);">
              <div style="font-size:0.82rem; font-weight:700; color:#fbbf24;">Application Deadline: ${event.company}</div>
              <div style="font-size:0.75rem; color:var(--text-secondary);">${formatDate(event.deadline)} • ${event.title}</div>
            </div>
          `),
          ...interviews.map(event => `
            <div style="background: rgba(99, 102, 241, 0.1); border-left: 3px solid #818cf8; padding: 10px 12px; border-radius: var(--radius-sm);">
              <div style="font-size:0.82rem; font-weight:700; color:#a5b4fc;">Interview: ${event.company}</div>
              <div style="font-size:0.75rem; color:var(--text-secondary);">${formatInterviewDate(event.interview_date)} • ${event.title}</div>
            </div>
          `)
        ].join('');
        return eventMarkup || '<div style="font-size:0.82rem; color:var(--text-muted);">No upcoming events.</div>';
      };

      container.innerHTML = `
        <!-- KPI Row -->
        <div class="kpi-grid">
          <div class="kpi-card">
            <div class="kpi-icon indigo">
              <i class="fa-solid fa-layer-group"></i>
            </div>
            <div class="kpi-details">
              <div class="kpi-label">Recommended Opportunities</div>
              <div class="kpi-value">${data.recommended_opportunities_count || 24}</div>
              <div class="kpi-subtitle"><i class="fa-solid fa-bolt"></i> Live AI matched</div>
            </div>
          </div>

          <div class="kpi-card" style="border-color: rgba(16, 185, 129, 0.4);">
            <div class="kpi-icon emerald">
              <i class="fa-solid fa-fire"></i>
            </div>
            <div class="kpi-details">
              <div class="kpi-label">🔥 Best Match</div>
              <div class="kpi-value" style="color:#34d399;">${best?.match_score ?? 0}%</div>
              <div class="kpi-subtitle" style="color:#cbd5e1; font-size:0.75rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                ${matchTitle(best)}
              </div>
            </div>
          </div>

          <div class="kpi-card">
            <div class="kpi-icon cyan">
              <i class="fa-solid fa-bullseye"></i>
            </div>
            <div class="kpi-details">
              <div class="kpi-label">🎯 Good Match</div>
              <div class="kpi-value" style="color:#22d3ee;">${good?.match_score ?? 0}%</div>
              <div class="kpi-subtitle" style="color:#cbd5e1; font-size:0.75rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                ${matchTitle(good)}
              </div>
            </div>
          </div>

          <div class="kpi-card">
            <div class="kpi-icon amber">
              <i class="fa-solid fa-calendar-check"></i>
            </div>
            <div class="kpi-details">
              <div class="kpi-label">📅 Upcoming Deadlines</div>
              <div class="kpi-value" style="color:#fbbf24;">${deadlines.length}</div>
              <div class="kpi-subtitle" style="color:#cbd5e1; font-size:0.75rem;">
                ${deadlines[0] ? `${deadlines[0].company} (${formatDate(deadlines[0].deadline)})` : 'No deadlines scheduled'}
              </div>
            </div>
          </div>
        </div>

        <!-- 2-Column Dashboard Grid -->
        <div class="dashboard-shell" style="display:grid; grid-template-columns: 2fr 1fr; gap: 24px;">
          <!-- Left Column: Opportunities & Funnel -->
          <div class="dashboard-column dashboard-main-column" style="display:flex; flex-direction:column; gap:24px;">
            <!-- Top Matches Table -->
            <div class="glass-card">
              <div class="card-header">
                <h3 class="card-title"><i class="fa-solid fa-sparkles" style="color:#818cf8;"></i> AI Top Recommended Opportunities</h3>
                <button class="btn btn-secondary btn-sm" onclick="App.navigate('jobs')">View All</button>
              </div>

              <div style="display:flex; flex-direction:column; gap:12px;">
                ${(data.top_recommendations || []).map(item => `
                  <div style="background: rgba(30, 41, 59, 0.5); border:1px solid var(--border-glass); border-radius: var(--radius-md); padding: 14px 18px; display:flex; align-items:center; justify-content:space-between; transition:var(--transition);" onmouseover="this.style.borderColor='rgba(99,102,241,0.4)'" onmouseout="this.style.borderColor='var(--border-glass)'">
                    <div>
                      <div style="font-weight:700; font-size:0.95rem; color:#ffffff;">${item.title}</div>
                      <div style="font-size:0.8rem; color:var(--text-muted); display:flex; gap:12px; margin-top:3px;">
                        <span><i class="fa-regular fa-building"></i> ${item.company}</span>
                        <span><i class="fa-solid fa-location-dot"></i> ${item.location}</span>
                        <span><i class="fa-regular fa-clock"></i> ${item.deadline}</span>
                      </div>
                    </div>

                    <div style="display:flex; align-items:center; gap:16px;">
                      <span class="badge badge-score ${item.match_score >= 85 ? 'high' : item.match_score >= 70 ? 'medium' : ''}">
                        ${item.match_score}% Match
                      </span>
                      <button class="btn btn-primary btn-sm" onclick="App.runPipelineForJob(${item.job_id})">
                        <i class="fa-solid fa-bolt"></i> Optimize
                      </button>
                    </div>
                  </div>
                `).join('')}
              </div>
            </div>

            <!-- Application Pipeline Summary -->
            <div class="glass-card">
              <div class="card-header">
                <h3 class="card-title"><i class="fa-solid fa-chart-simple" style="color:#06b6d4;"></i> Application Pipeline Status</h3>
                <button class="btn btn-secondary btn-sm" onclick="App.navigate('tracker')">Open Kanban</button>
              </div>
              <div style="height: 200px; position:relative;">
                <canvas id="pipelineChart"></canvas>
              </div>
            </div>
          </div>

          <!-- Right Column: Quick Status & Actions -->
          <div class="dashboard-column dashboard-side-column" style="display:flex; flex-direction:column; gap:24px;">
            <!-- Profile Readiness Widget -->
            <div class="glass-card" style="background: linear-gradient(145deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9));">
              <div class="card-header" style="margin-bottom:12px;">
                <h3 class="card-title" style="font-size:0.95rem;"><i class="fa-solid fa-circle-check" style="color:#10b981;"></i> Profile Readiness</h3>
                <span style="font-weight:800; font-size:1.1rem; color:#34d399;">${data.profile_completion_percent}%</span>
              </div>
              <div style="width:100%; height:8px; background:rgba(255,255,255,0.08); border-radius:4px; overflow:hidden; margin-bottom:16px;">
                <div style="width:${data.profile_completion_percent}%; height:100%; background:linear-gradient(90deg, #10b981, #06b6d4); border-radius:4px;"></div>
              </div>
              <p style="font-size:0.8rem; color:var(--text-muted); margin-bottom:16px;">
                High profile completion directly improves your AI Match Score accuracy across all jobs.
              </p>
              <button class="btn btn-secondary btn-sm" style="width:100%;" onclick="App.navigate('profile')">
                <i class="fa-solid fa-sliders"></i> Edit Profile & Skills
              </button>
            </div>

            <!-- Multi-Agent Quick Action Hub -->
            <div class="glass-card">
              <div class="card-header">
                <h3 class="card-title" style="font-size:0.95rem;"><i class="fa-solid fa-wand-magic-sparkles" style="color:#d946ef;"></i> Quick AI Workflows</h3>
              </div>
              <div style="display:flex; flex-direction:column; gap:10px;">
                <button class="btn btn-secondary btn-sm" style="justify-content:flex-start;" onclick="App.navigate('resume')">
                  <i class="fa-solid fa-file-lines" style="color:#818cf8; width:20px;"></i>
                  <span>Scan Resume with ATS Agent</span>
                </button>
                <button class="btn btn-secondary btn-sm" style="justify-content:flex-start;" onclick="App.navigate('cover-letter')">
                  <i class="fa-solid fa-envelope-open-text" style="color:#06b6d4; width:20px;"></i>
                  <span>Generate Custom Cover Letter</span>
                </button>
                <button class="btn btn-secondary btn-sm" style="justify-content:flex-start;" onclick="App.navigate('interview')">
                  <i class="fa-solid fa-microphone-lines" style="color:#10b981; width:20px;"></i>
                  <span>Launch AI Mock Interview</span>
                </button>
                <button class="btn btn-primary btn-sm" style="margin-top:6px;" onclick="App.navigate('orchestrator')">
                  <i class="fa-solid fa-robot"></i>
                  <span>View 7-Agent Pipeline</span>
                </button>
              </div>
            </div>

            <!-- Upcoming Deadlines & Interviews -->
            <div class="glass-card">
              <div class="card-header" style="margin-bottom:12px;">
                <h3 class="card-title" style="font-size:0.95rem;"><i class="fa-solid fa-bell" style="color:#f59e0b;"></i> Upcoming Events</h3>
              </div>
              <div style="display:flex; flex-direction:column; gap:10px;">
                ${renderEvents()}
              </div>
            </div>
          </div>
        </div>
      `;

      // Render Pipeline Chart
      const ctx = document.getElementById('pipelineChart');
      if (ctx && window.Chart) {
        if (this.chartInstance) {
          this.chartInstance.destroy();
        }
        this.chartInstance = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: ['Applied', 'Assessment', 'Interview', 'Selected', 'Rejected'],
            datasets: [{
              label: 'Applications',
              data: [
                breakdown.applied || 12,
                breakdown.assessment || 3,
                breakdown.interview || 2,
                breakdown.selected || 1,
                breakdown.rejected || 4
              ],
              backgroundColor: [
                'rgba(99, 102, 241, 0.7)',
                'rgba(6, 182, 212, 0.7)',
                'rgba(245, 158, 11, 0.7)',
                'rgba(16, 185, 129, 0.7)',
                'rgba(244, 63, 94, 0.7)'
              ],
              borderRadius: 6
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false }
            },
            scales: {
              y: {
                beginAtZero: true,
                grid: { color: 'rgba(255,255,255,0.05)' },
                ticks: { color: '#94a3b8', font: { size: 11 } }
              },
              x: {
                grid: { display: false },
                ticks: { color: '#94a3b8', font: { size: 11 } }
              }
            }
          }
        });
      }
    } catch (err) {
      container.innerHTML = `<div class="glass-card" style="color:#f43f5e;"><i class="fa-solid fa-triangle-exclamation"></i> Error loading dashboard data: ${err.message}</div>`;
    }
  }
};
