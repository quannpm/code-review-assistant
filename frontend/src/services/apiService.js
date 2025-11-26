/**
 * API Service - Quản lý tất cả API calls và session management
 * 
 * Features:
 * - Session management với memory support
 * - Centralized API calls
 * - Error handling
 * - Cache management
 */

const API_BASE_URL = 'http://localhost:8888/api';
class ApiService {
  constructor() {
    this.sessionId = this.getOrCreateSessionId();
    this.cache = new Map();
  }

  /**
   * Tạo hoặc lấy session ID từ localStorage
   */
  getOrCreateSessionId() {
    let sessionId = localStorage.getItem('ai_session_id');

    if (!sessionId) {
      sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('ai_session_id', sessionId);
    }

    return sessionId;
  }

  /**
   * Reset session - tạo session mới
   */
  resetSession() {
    localStorage.removeItem('ai_session_id');
    this.sessionId = this.getOrCreateSessionId();
    this.cache.clear();

    // Clear session memory trên backend
    this.clearSessionMemory();
  }

  /**
   * Chat với AI Assistant với session memory
   */
  async chatWithAI(message, history = [], isQuickAction = false, displayLanguage = 'en', programmingLanguage = 'javascript') {
    try {
      const requestBody = {
        message,
        history, // Vẫn gửi history cho backward compatibility
        is_quick_action: isQuickAction,
        session_id: this.sessionId, // Thêm session ID
        display_language: displayLanguage, // Ngôn ngữ hiển thị (en/vi)
        programming_language: programmingLanguage // Ngôn ngữ lập trình (java/php/python...)
      };

      // Debug log để kiểm tra payload
      console.log('API Request payload:', requestBody);

      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'API request failed');
      }

      return data;
    } catch (error) {
      console.error('Chat API error:', error);
      throw error;
    }
  }

  /**
   * Chat với Knowledge Base với memory support
   */
  async chatWithKnowledgeBase(message, fileIds = null, maxResults = 3, displayLanguage = 'en') {
    try {
      const requestBody = {
        message,
        session_id: this.sessionId,
        max_results: maxResults,
        display_language: displayLanguage // Ngôn ngữ hiển thị (en/vi)
      };

      if (fileIds && fileIds.length > 0) {
        requestBody.file_ids = fileIds;
      }

      // Debug log để kiểm tra payload
      console.log('Knowledge Base API Request payload:', requestBody);

      const response = await fetch(`${API_BASE_URL}/knowledge-base/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Knowledge base chat failed');
      }

      return data;
    } catch (error) {
      console.error('Knowledge base chat error:', error);
      throw error;
    }
  }

  /**
   * Upload file to knowledge base
   */
  async uploadFile(file, title, description = '') {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', title);
      formData.append('description', description);

      const response = await fetch(`${API_BASE_URL}/knowledge-base/upload`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'File upload failed');
      }

      return data;
    } catch (error) {
      console.error('Upload error:', error);
      throw error;
    }
  }

  /**
   * Lấy danh sách files đã upload
   */
  async getUploadedFiles() {
    try {
      const cacheKey = 'uploaded_files';

      // Check cache first
      if (this.cache.has(cacheKey)) {
        const cached = this.cache.get(cacheKey);
        if (Date.now() - cached.timestamp < 30000) { // 30 seconds cache
          return cached.data;
        }
      }

      const response = await fetch(`${API_BASE_URL}/knowledge-base/files`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch files');
      }

      // Cache the result
      this.cache.set(cacheKey, {
        data,
        timestamp: Date.now()
      });

      return data;
    } catch (error) {
      console.error('Get files error:', error);
      throw error;
    }
  }

  /**
   * Search trong knowledge base
   */
  async searchKnowledgeBase(query, filenameUuids, maxResults = 5) {
    try {
      const response = await fetch(`${API_BASE_URL}/knowledge-base/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          filename_uuids: filenameUuids,
          max_results: maxResults
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Search failed');
      }

      return data;
    } catch (error) {
      console.error('Search error:', error);
      throw error;
    }
  }

  /**
   * Lấy memory sessions
   */
  async getMemorySessions() {
    try {
      const response = await fetch(`${API_BASE_URL}/knowledge-base/memory/sessions`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to get memory sessions');
      }

      return data;
    } catch (error) {
      console.error('Memory sessions error:', error);
      throw error;
    }
  }

  /**
   * Lấy search history của session
   */
  async getSessionSearchHistory(sessionId = null, limit = 10) {
    try {
      const targetSessionId = sessionId || this.sessionId;
      const response = await fetch(`${API_BASE_URL}/knowledge-base/memory/history/${targetSessionId}?limit=${limit}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to get search history');
      }

      return data;
    } catch (error) {
      console.error('Search history error:', error);
      throw error;
    }
  }

  /**
   * Clear session memory
   */
  async clearSessionMemory(sessionId = null) {
    try {
      const targetSessionId = sessionId || this.sessionId;
      const response = await fetch(`${API_BASE_URL}/knowledge-base/memory/clear/${targetSessionId}`, {
        method: 'POST'
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to clear session memory');
      }

      return data;
    } catch (error) {
      console.error('Clear memory error:', error);
      throw error;
    }
  }

  /**
   * Lấy supported languages
   */
  async getSupportedLanguages() {
    try {
      const cacheKey = 'supported_languages';

      if (this.cache.has(cacheKey)) {
        return this.cache.get(cacheKey);
      }

      const response = await fetch(`${API_BASE_URL}/languages`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to get languages');
      }

      this.cache.set(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Languages error:', error);
      throw error;
    }
  }

  /**
   * Health check
   */
  async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      return await response.json();
    } catch (error) {
      console.error('Health check error:', error);
      return { success: false, error: error.message };
    }
  }

  // Aliases for compatibility with components
  async uploadKnowledgeBaseFile(file, title, description = '') {
    return this.uploadFile(file, title, description);
  }

  async getKnowledgeBaseFiles() {
    return this.getUploadedFiles();
  }

  async knowledgeBaseChat(message, fileIds = null, maxResults = 3, sessionId = null, displayLanguage = 'en') {
    // Use provided sessionId or fall back to current session
    const oldSessionId = this.sessionId;
    if (sessionId) {
      this.sessionId = sessionId;
    }

    try {
      const result = await this.chatWithKnowledgeBase(message, fileIds, maxResults, displayLanguage);
      return result;
    } finally {
      // Restore original sessionId
      this.sessionId = oldSessionId;
    }
  }
}

// Singleton instance
const apiService = new ApiService();

export default apiService;
