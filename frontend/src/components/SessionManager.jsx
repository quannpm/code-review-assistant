/**
 * Session Manager Component
 * 
 * Quản lý session state và memory cho toàn bộ app
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import apiService from '../services/apiService';

const SessionContext = createContext();

export const useSession = () => {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
};

export const SessionProvider = ({ children }) => {
  const [sessionId, setSessionId] = useState(apiService.sessionId);
  const [searchHistory, setSearchHistory] = useState([]);
  const [memoryStats, setMemoryStats] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Load search history khi component mount
  useEffect(() => {
    loadSearchHistory();
    loadMemoryStats();
  }, [sessionId]);

  const loadSearchHistory = async () => {
    try {
      setIsLoading(true);
      const response = await apiService.getSessionSearchHistory(sessionId);
      if (response.success) {
        setSearchHistory(response.data.search_history || []);
      }
    } catch (error) {
      console.error('Failed to load search history:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadMemoryStats = async () => {
    try {
      const response = await apiService.getMemorySessions();
      if (response.success) {
        setMemoryStats(response.data);
      }
    } catch (error) {
      console.error('Failed to load memory stats:', error);
    }
  };

  const resetSession = async () => {
    try {
      setIsLoading(true);
      
      // Clear memory trên backend
      await apiService.clearSessionMemory(sessionId);
      
      // Reset frontend session
      apiService.resetSession();
      const newSessionId = apiService.sessionId;
      
      setSessionId(newSessionId);
      setSearchHistory([]);
      
      // Reload stats
      await loadMemoryStats();
      
      return newSessionId;
    } catch (error) {
      console.error('Failed to reset session:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const addToSearchHistory = (searchEntry) => {
    setSearchHistory(prev => [searchEntry, ...prev].slice(0, 10)); // Keep only 10 latest
  };

  const clearSearchHistory = async () => {
    try {
      await apiService.clearSessionMemory(sessionId);
      setSearchHistory([]);
      await loadMemoryStats();
    } catch (error) {
      console.error('Failed to clear search history:', error);
      throw error;
    }
  };

  const value = {
    sessionId,
    searchHistory,
    memoryStats,
    isLoading,
    loadSearchHistory,
    loadMemoryStats,
    resetSession,
    addToSearchHistory,
    clearSearchHistory
  };

  return (
    <SessionContext.Provider value={value}>
      {children}
    </SessionContext.Provider>
  );
};
