/**
 * Central API Client for AI Job & Internship Automation Platform
 */
const API = {
  baseUrl: '/api',
  tokenKey: 'career_agent_token',

  getToken() {
    return localStorage.getItem(this.tokenKey);
  },

  setToken(token) {
    localStorage.setItem(this.tokenKey, token);
  },

  clearToken() {
    localStorage.removeItem(this.tokenKey);
  },

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = options.headers || {};

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    if (!(options.body instanceof FormData) && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers
      });

      if (response.status === 401 && !endpoint.includes('/auth/login')) {
        // Attempt auto demo login
        await this.autoDemoLogin();
        // Retry request once
        headers['Authorization'] = `Bearer ${this.getToken()}`;
        const retry = await fetch(url, { ...options, headers });
        return await retry.json();
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(errorData.detail || `HTTP Error ${response.status}`);
      }

      return await response.json();
    } catch (err) {
      console.error(`[API Error] ${endpoint}:`, err);
      throw err;
    }
  },

  // Auth
  async login(email, password) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    if (data.access_token) {
      this.setToken(data.access_token);
    }
    return data;
  },

  async register(name, email, password) {
    const data = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password })
    });
    if (data.access_token) {
      this.setToken(data.access_token);
    }
    return data;
  },

  async getProfile() {
    return await this.request('/profile');
  },

  async updateProfile(profileData) {
    return await this.request('/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData)
    });
  },

  async uploadResume(file) {
    const formData = new FormData();
    formData.append('file', file);
    return await this.request('/profile/upload-resume', {
      method: 'POST',
      body: formData
    });
  },

  // Jobs
  async getJobs(params = {}) {
    const searchParams = new URLSearchParams();
    if (params.q) searchParams.append('q', params.q);
    if (params.job_type) searchParams.append('job_type', params.job_type);
    if (params.location) searchParams.append('location', params.location);
    if (params.is_remote !== undefined) searchParams.append('is_remote', params.is_remote);
    const query = searchParams.toString();
    return await this.request(`/jobs${query ? '?' + query : ''}`);
  },

  async getJobById(jobId) {
    return await this.request(`/jobs/${jobId}`);
  },

  // Matching
  async calculateMatch(jobId) {
    return await this.request(`/match/calculate/${jobId}`, { method: 'POST' });
  },

  async getRecommendations() {
    return await this.request('/match/recommendations');
  },

  // Agents
  async analyzeResume(jobId, customJd, targetRole) {
    return await this.request('/agents/analyze-resume', {
      method: 'POST',
      body: JSON.stringify({
        job_id: jobId,
        job_description: customJd,
        target_role: targetRole
      })
    });
  },

  async generateCoverLetter(payload) {
    return await this.request('/agents/generate-cover-letter', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  async runOrchestrator(payload) {
    return await this.request('/agents/orchestrate', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  // Workflows (AI Builder)
  async getWorkflows() {
    return await this.request('/workflows');
  },

  async getWorkflowById(workflowId) {
    return await this.request(`/workflows/${workflowId}`);
  },

  async createWorkflow(payload) {
    return await this.request('/workflows', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  async updateWorkflow(workflowId, payload) {
    return await this.request(`/workflows/${workflowId}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    });
  },

  async deleteWorkflow(workflowId) {
    return await this.request(`/workflows/${workflowId}`, {
      method: 'DELETE'
    });
  },

  async runWorkflow(workflowId, payload = {}) {
    return await this.request(`/workflows/${workflowId}/run`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  // Applications
  async getApplications(status = null) {
    return await this.request(`/applications${status ? '?status=' + status : ''}`);
  },

  async createApplication(payload) {
    return await this.request('/applications', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  async updateApplication(id, payload) {
    return await this.request(`/applications/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    });
  },

  async deleteApplication(id) {
    return await this.request(`/applications/${id}`, {
      method: 'DELETE'
    });
  },

  // Interview
  async generateInterviewQuestions(payload) {
    return await this.request('/interview/questions', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  async evaluateInterviewAnswer(payload) {
    return await this.request('/interview/evaluate', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  // Analytics
  async getDashboardAnalytics() {
    return await this.request('/analytics/dashboard');
  },

  // Auto demo login helper
  async autoDemoLogin() {
    try {
      await this.login('student@example.com', 'password123');
    } catch (e) {
      console.warn('Auto demo login fell back:', e);
    }
  }
};
