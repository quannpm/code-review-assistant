import React, { useState, useRef, useEffect } from 'react';
import { useSession } from './SessionManager';
import { useLanguage } from '../contexts/LanguageContext'; // Thêm dòng này
import './MemoryPanel.css';

const translations = {
  en: {
    memorySessions: '🧠 Memory & Sessions',
    currentSession: 'Current Session',
    resetSession: '🗑️ Reset Session',
    refresh: '🔄 Refresh',
    searchHistory: count => `Search History (${count})`,
    noHistory: 'No search history yet',
    clearHistory: '🧹 Clear History',
    confirmReset: '⚠️ Confirm Reset',
    confirmText: 'This will clear all conversation memory and search history for this session. Are you sure?',
    yesReset: 'Yes, Reset',
    cancel: 'Cancel',
    files: count => `📄 ${count} files`
  },
  vi: {
    memorySessions: '🧠 Bộ nhớ & Phiên',
    currentSession: 'Phiên hiện tại',
    resetSession: '🗑️ Đặt lại phiên',
    refresh: '🔄 Làm mới',
    searchHistory: count => `Lịch sử tìm kiếm (${count})`,
    noHistory: 'Chưa có lịch sử tìm kiếm',
    clearHistory: '🧹 Xóa lịch sử',
    confirmReset: '⚠️ Xác nhận đặt lại',
    confirmText: 'Thao tác này sẽ xóa toàn bộ bộ nhớ hội thoại và lịch sử tìm kiếm của phiên này. Bạn có chắc không?',
    yesReset: 'Đồng ý đặt lại',
    cancel: 'Hủy',
    files: count => `📄 ${count} tệp`
  }
};

const MemoryPanel = ({ isVisible, onToggle }) => {
  const { language } = useLanguage(); // Thêm dòng này
  const t = translations[language] || translations.en;

  const {
    sessionId,
    searchHistory,
    memoryStats,
    isLoading,
    resetSession,
    clearSearchHistory,
    loadMemoryStats
  } = useSession();

  const panelRef = useRef(null);

  const [showConfirmClear, setShowConfirmClear] = useState(false);

  const handleResetSession = async () => {
    try {
      await resetSession();
      setShowConfirmClear(false);
    } catch (error) {
      console.error('Failed to reset session:', error);
    }
  };

  const handleClearHistory = async () => {
    try {
      await clearSearchHistory();
      setShowConfirmClear(false);
    } catch (error) {
      console.error('Failed to clear history:', error);
    }
  };

  const formatTimestamp = (timestamp) => {
    if (typeof timestamp === 'string') {
      timestamp = new Date(timestamp);
    }
    return timestamp.toLocaleString();
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'chat': return '💬';
      case 'quick_action': return '⚡';
      case 'knowledge_base': return '📚';
      default: return '🔍';
    }
  };

  // Handle click outside to close panel
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (panelRef.current && !panelRef.current.contains(event.target) && isVisible) {
        onToggle();
      }
    };

    if (isVisible) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isVisible, onToggle]);

  if (!isVisible) return null;

  return (
    <div className="memory-panel" ref={panelRef}>
      <div className="memory-header">
        <h3>{t.memorySessions}</h3>
        <button onClick={onToggle} className="close-btn">✕</button>
      </div>

      <div className="memory-content">
        {/* Session Info */}
        <div className="session-info">
          <h4>{t.currentSession}</h4>
          <div className="session-id">
            <code>{sessionId}</code>
          </div>

          <div className="session-actions">
            <button
              onClick={() => setShowConfirmClear(true)}
              className="btn-secondary"
              disabled={isLoading}
            >
              {t.resetSession}
            </button>
            <button
              onClick={loadMemoryStats}
              className="btn-secondary"
              disabled={isLoading}
            >
              {t.refresh}
            </button>
          </div>
        </div>

        {/* Search History */}
        <div className="search-history">
          <h4>{t.searchHistory(searchHistory.length)}</h4>

          {searchHistory.length === 0 ? (
            <div className="empty-history">
              <p>{t.noHistory}</p>
            </div>
          ) : (
            <div className="history-list">
              {searchHistory.map((entry, index) => (
                <div key={index} className="history-item">
                  <div className="history-header">
                    <span className="type-icon">{getTypeIcon(entry.type)}</span>
                    <span className="query-preview">
                      {entry.query.length > 50
                        ? entry.query.substring(0, 50) + '...'
                        : entry.query}
                    </span>
                  </div>
                  <div className="history-meta">
                    <span className="timestamp">
                      {formatTimestamp(entry.timestamp)}
                    </span>
                    {entry.file_count && (
                      <span className="file-count">
                        {t.files(entry.file_count)}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {searchHistory.length > 0 && (
            <button
              onClick={handleClearHistory}
              className="btn-secondary clear-history-btn"
              disabled={isLoading}
            >
              {t.clearHistory}
            </button>
          )}
        </div>
      </div>

      {/* Confirmation Dialog */}
      {showConfirmClear && (
        <div className="confirm-dialog">
          <div className="confirm-content">
            <h4>{t.confirmReset}</h4>
            <p>{t.confirmText}</p>
            <div className="confirm-actions">
              <button
                onClick={handleResetSession}
                className="btn-danger"
                disabled={isLoading}
              >
                {t.yesReset}
              </button>
              <button
                onClick={() => setShowConfirmClear(false)}
                className="btn-secondary"
              >
                {t.cancel}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MemoryPanel;
