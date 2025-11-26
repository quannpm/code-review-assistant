import React, { useState, useEffect, useRef } from 'react';
import ChatAssistant from './components/ChatAssistant';
import HomePage from './pages/HomePage';
import KnowledgeBasePage from './pages/KnowledgeBasePage';
import LanguageSelector from './components/LanguageSelector';
import { SessionProvider } from './components/SessionManager';
import { LanguageProvider, useLanguage } from './contexts/LanguageContext';
import apiService from './services/apiService';
import './App.css';

function AppContent() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('java');
  const [commentedCode, setCommentedCode] = useState('');
  const [tokensInfo, setTokensInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [supportedLanguages, setSupportedLanguages] = useState([]);
  const fileInputRef = useRef(null);
  const [chatVisible, setChatVisible] = useState(false);
  const [currentPage, setCurrentPage] = useState(() => {
    // Check URL path to determine initial page
    const path = window.location.pathname;
    if (path === '/knowledge-base') {
      return 'knowledge-base';
    }
    return 'home';
  }); // Add page state

  // Use language context for display language
  const { language: displayLanguage } = useLanguage();

  useEffect(() => {
    // Fetch supported languages
    const fetchLanguages = async () => {
      try {
        const response = await apiService.getSupportedLanguages();
        if (response.success) {
          setSupportedLanguages(response.languages); // Fix: response.languages thay vì response.data.languages
        }
      } catch (err) {
        console.error('Error fetching languages:', err);
      }
    };

    fetchLanguages();
  }, []);

  const handleLanguageChange = (newLanguage) => {
    setLanguage(newLanguage);
    setCommentedCode('');
    setTokensInfo(null);
    setError('');
  };

  const handleClearAll = () => {
    setCode('');
    setCommentedCode('');
    setTokensInfo(null);
    setError('');
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Check file size (limit to 5MB) - Kiểm tra kích thước file (giới hạn 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('File is too large. Please select a file smaller than 5MB.');
      return;
    }

    // Check file type - Kiểm tra loại file
    const allowedExtensions = ['.txt', '.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.clj', '.sh', '.sql', '.html', '.css', '.json', '.xml', '.yaml', '.yml'];
    const fileName = file.name.toLowerCase();
    const isAllowed = allowedExtensions.some(ext => fileName.endsWith(ext));

    if (!isAllowed) {
      setError('File format not supported. Please select a valid code file.');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target.result;
      setCode(content);
      setCommentedCode('');
      setTokensInfo(null);
      setError('');

      // Auto-detect language from file extension - Tự động phát hiện ngôn ngữ từ phần mở rộng file
      const ext = fileName.split('.').pop();
      const languageMap = {
        'js': 'javascript',
        'jsx': 'javascript',
        'ts': 'typescript',
        'tsx': 'typescript',
        'py': 'python',
        'java': 'java',
        'cpp': 'cpp',
        'c': 'c',
        'cs': 'csharp',
        'php': 'php',
        'rb': 'ruby',
        'go': 'go',
        'rs': 'rust',
        'swift': 'swift',
        'kt': 'kotlin',
        'scala': 'scala',
        'clj': 'clojure',
        'sh': 'bash',
        'sql': 'sql'
      };

      if (languageMap[ext]) {
        setLanguage(languageMap[ext]);
      }
    };

    reader.onerror = () => {
      setError('Cannot read file. Please try again.');
    };

    reader.readAsText(file);

    // Reset input value to allow selecting the same file again - Reset giá trị input để cho phép chọn lại cùng file
    event.target.value = '';
  };

  const toggleChat = () => {
    setChatVisible(!chatVisible);
  };

  const handleChatResult = (result, tokensData) => {
    setCommentedCode(result);
    setTokensInfo(tokensData);
    setError('');
  };

  // Quick Action handlers
  const handleQuickAction = async (actionType, prompt) => {
    if (!code.trim()) {
      setError('Please enter code before using Quick Action');
      return;
    }

    setLoading(true);
    setError('');

    const message = `${prompt}\n\n\`\`\`${language}\n${code}\n\`\`\``;

    try {
      // Debug log để kiểm tra ngôn ngữ
      console.log('Quick Action - Display language:', displayLanguage);
      console.log('Quick Action - Programming language:', language);

      const response = await apiService.chatWithAI(
        message, 
        [], 
        true, 
        displayLanguage, // Display language (en/vi)
        language // Programming language (java/python/javascript...)
      );

      if (response.success) {
        setCommentedCode(response.response); // Fix: response.response thay vì response.data.response
        setTokensInfo(response.tokens_info); // Fix: response.tokens_info thay vì response.data.tokens_info
        setError('');
      } else {
        setError(response.error || 'An error occurred while processing Quick Action');
      }
    } catch (err) {
      console.error('Quick Action error:', err);
      setError('Unable to connect to AI Assistant');
    } finally {
      setLoading(false);
    }
  };

  const handleCommentCode = () => {
    const prompt = displayLanguage === 'vi'
      ? 'Thêm comment chi tiết bằng tiếng Việt vào code này, giải thích từng phần làm gì:'
      : 'Add detailed comments in English to this code, explain what each part does:';
    handleQuickAction('comment', prompt);
  };

  const handleFindBugs = () => {
    const prompt = displayLanguage === 'vi'
      ? 'Tìm và sửa lỗi trong code này:'
      : 'Find and fix bugs in this code:';
    handleQuickAction('debug', prompt);
  };

  const handleOptimize = () => {
    const prompt = displayLanguage === 'vi'
      ? 'Tối ưu hiệu suất của code này:'
      : 'Optimize the performance of this code:';
    handleQuickAction('optimize', prompt);
  };

  const handleGenerateTests = () => {
    const prompt = displayLanguage === 'vi'
      ? 'Tạo unit test cho code này:'
      : 'Generate unit tests for this code:';
    handleQuickAction('test', prompt);
  };

  // Navigation handlers
  const navigateToHome = () => {
    setCurrentPage('home');
    window.history.pushState(null, '', '/');
  };
  const navigateToKnowledgeBase = () => {
    setCurrentPage('knowledge-base');
    window.history.pushState(null, '', '/knowledge-base');
  };
  const handleNavigate = (page) => {
    if (page === 'home') {
      navigateToHome();
    } else if (page === 'knowledge-base') {
      navigateToKnowledgeBase();
    }
  };

  // Handle browser back/forward buttons
  useEffect(() => {
    const handlePopState = () => {
      const path = window.location.pathname;
      if (path === '/knowledge-base') {
        setCurrentPage('knowledge-base');
      } else {
        setCurrentPage('home');
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  // Render different pages based on currentPage
  const renderContent = () => {
    if (currentPage === 'knowledge-base') {
      return <KnowledgeBasePage onNavigate={handleNavigate} />;
    }

    // Default home page content
    return (
      <HomePage
        onNavigate={handleNavigate}
        language={language}
        displayLanguage={displayLanguage}
        supportedLanguages={supportedLanguages}
        onLanguageChange={handleLanguageChange}
        onFileUpload={handleFileUpload}
        fileInputRef={fileInputRef}
        onClearAll={handleClearAll}
        onCommentCode={handleCommentCode}
        onFindBugs={handleFindBugs}
        onOptimize={handleOptimize}
        onGenerateTests={handleGenerateTests}
        loading={loading}
        code={code}
        setCode={setCode}
        error={error}
        commentedCode={commentedCode}
        tokensInfo={tokensInfo}
      />
    );
  };

  return (
    <SessionProvider>
      <div className="App">
        {/* Display Language Selector - Fixed position on left */}
        <LanguageSelector />

        {renderContent()}

        {/* Floating Chat Button - Only show on home page */}
        {currentPage === 'home' && (
          <button
            onClick={toggleChat}
            className={`floating-chat-btn ${chatVisible ? 'active' : ''}`}
            title={chatVisible ? "Close AI Assistant" : "Open AI Assistant"}
          >
            {chatVisible ? '✕' : '🤖'}
          </button>
        )}

        {/* Chat Assistant Sidebar - Only show on home page */}
        {currentPage === 'home' && (
          <ChatAssistant
            isVisible={chatVisible}
            onToggle={toggleChat}
            currentCode={code}
            currentLanguage={language}
            onChatResult={handleChatResult}
          />
        )}
      </div>
    </SessionProvider>
  );
}

function App() {
  return (
    <LanguageProvider>
      <AppContent />
    </LanguageProvider>
  );
}

export default App;
