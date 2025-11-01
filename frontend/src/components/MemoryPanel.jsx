/**
 * Memory Panel Component
 * 
 * Hiển thị thông tin session memory và search history
 */

import React, { useState, useRef, useEffect } from 'react';
import { useSession } from './SessionManager';
import './MemoryPanel.css';

const MemoryPanel = ({ isVisible, onToggle }) => {
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
        <h3>🧠 Memory & Sessions</h3>
        <button onClick={onToggle} className="close-btn">✕</button>
      </div>

      <div className="memory-content">
        {/* Session Info */}
        <div className="session-info">
          <h4>Current Session</h4>
          <div className="session-id">
            <code>{sessionId}</code>
          </div>
          
          <div className="session-actions">
            <button 
              onClick={() => setShowConfirmClear(true)}
              className="btn-secondary"
              disabled={isLoading}
            >
              🗑️ Reset Session
            </button>
            <button 
              onClick={loadMemoryStats}
              className="btn-secondary"
              disabled={isLoading}
            >
              🔄 Refresh
            </button>
          </div>
        </div>

        {/* Search History */}
        <div className="search-history">
          <h4>Search History ({searchHistory.length})</h4>
          
          {searchHistory.length === 0 ? (
            <div className="empty-history">
              <p>No search history yet</p>
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
                        📄 {entry.file_count} files
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
              🧹 Clear History
            </button>
          )}
        </div>
      </div>

      {/* Confirmation Dialog */}
      {showConfirmClear && (
        <div className="confirm-dialog">
          <div className="confirm-content">
            <h4>⚠️ Confirm Reset</h4>
            <p>This will clear all conversation memory and search history for this session. Are you sure?</p>
            <div className="confirm-actions">
              <button 
                onClick={handleResetSession}
                className="btn-danger"
                disabled={isLoading}
              >
                Yes, Reset
              </button>
              <button 
                onClick={() => setShowConfirmClear(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MemoryPanel;
