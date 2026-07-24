const API_BASE = import.meta.env.VITE_API_URL || '';

/**
 * API client with JWT authentication support.
 * Uses fetch() for zero-dependency HTTP requests.
 */
class ApiClient {
  constructor() {
    this.baseUrl = API_BASE;
  }

  /** Get the stored JWT token. */
  getToken() {
    return localStorage.getItem('stylesense_token');
  }

  /** Set the JWT token. */
  setToken(token) {
    localStorage.setItem('stylesense_token', token);
  }

  /** Remove the JWT token. */
  removeToken() {
    localStorage.removeItem('stylesense_token');
  }

  /** Build headers with optional auth. */
  _headers(isJson = true) {
    const headers = {};
    if (isJson) headers['Content-Type'] = 'application/json';
    const token = this.getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
    return headers;
  }

  /** Make an API request and handle errors uniformly. */
  async _request(method, path, { body, isFormData = false } = {}) {
    const url = `${this.baseUrl}${path}`;
    const options = {
      method,
      headers: this._headers(!isFormData),
    };

    if (body) {
      options.body = isFormData ? body : JSON.stringify(body);
    }

    const response = await fetch(url, options);
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      const error = new Error(data.error || data.message || `Request failed (${response.status})`);
      error.status = response.status;
      error.data = data;
      throw error;
    }

    return data;
  }

  // ── Auth ──────────────────────────────────────────────────────────
  async register(email, password) {
    const data = await this._request('POST', '/api/auth/register', {
      body: { email, password },
    });
    if (data.access_token) this.setToken(data.access_token);
    return data;
  }

  async login(email, password) {
    const data = await this._request('POST', '/api/auth/login', {
      body: { email, password },
    });
    if (data.access_token) this.setToken(data.access_token);
    return data;
  }

  async getMe() {
    return this._request('GET', '/api/auth/me');
  }

  async logout() {
    try {
      await this._request('POST', '/api/auth/logout');
    } finally {
      this.removeToken();
    }
  }

  // ── Analysis ──────────────────────────────────────────────────────
  async analyze(faceImage, bodyImage) {
    const formData = new FormData();
    if (faceImage) formData.append('face_image', faceImage);
    if (bodyImage) formData.append('body_image', bodyImage);

    return this._request('POST', '/api/analysis/analyze', {
      body: formData,
      isFormData: true,
    });
  }

  // ── History ───────────────────────────────────────────────────────
  async getHistory(page = 1, perPage = 12) {
    return this._request('GET', `/api/history?page=${page}&per_page=${perPage}`);
  }

  async getAnalysis(id) {
    return this._request('GET', `/api/history/${id}`);
  }

  async deleteAnalysis(id) {
    return this._request('DELETE', `/api/history/${id}`);
  }

  // ── Feedback ──────────────────────────────────────────────────────
  /**
   * Record a verdict on one recommendation.
   * Pass verdict = null to clear it (toggling a button off).
   */
  async setFeedback(analysisId, category, recommendation, verdict) {
    return this._request('PUT', `/api/feedback/analysis/${analysisId}`, {
      body: { category, recommendation, verdict },
    });
  }

  /** All verdicts for one analysis, keyed by "category::recommendation". */
  async getFeedback(analysisId) {
    return this._request('GET', `/api/feedback/analysis/${analysisId}`);
  }

  /** Everything the user has liked, across every analysis. */
  async getSaved(page = 1, perPage = 20) {
    return this._request('GET', `/api/feedback/saved?page=${page}&per_page=${perPage}`);
  }

  /**
   * Fetch an analysis thumbnail as an object URL.
   *
   * The endpoint reads the JWT from the Authorization header, so the image
   * cannot be loaded by putting a token in a plain <img src>. Callers own
   * the returned URL and must revokeObjectURL it on unmount.
   */
  async getThumbnailObjectUrl(analysisId) {
    const response = await fetch(
      `${this.baseUrl}/api/history/${analysisId}/thumbnail`,
      { headers: this._headers(false) },
    );
    if (!response.ok) return null;
    return URL.createObjectURL(await response.blob());
  }
}

const api = new ApiClient();
export default api;
