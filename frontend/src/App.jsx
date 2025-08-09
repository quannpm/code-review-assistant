import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import ChatAssistant from './components/ChatAssistant';
import HowToUse from './components/HowToUse';
import CodeEditor from './components/CodeEditor';
import './App.css';

const API_BASE_URL = 'http://localhost:8888/api';

function App() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('java');
  const [commentedCode, setCommentedCode] = useState('');
  const [tokensInfo, setTokensInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [supportedLanguages, setSupportedLanguages] = useState([]);
  const [fileInputRef, setFileInputRef] = useState(null);
  const [chatVisible, setChatVisible] = useState(false);

  useEffect(() => {
    // Fetch supported languages - Lấy danh sách ngôn ngữ được hỗ trợ
    const fetchLanguages = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/languages`);
        if (response.data.success) {
          setSupportedLanguages(response.data.languages);
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

  const triggerFileUpload = () => {
    if (fileInputRef) {
      fileInputRef.click();
    }
  };

  const toggleChat = () => {
    setChatVisible(!chatVisible);
  };

  const handleChatResult = (result, tokensData) => {
    setCommentedCode(result);
    setTokensInfo(tokensData);
    setError('');
  };

  // Quick Action handlers - Xử lý các Quick Action
  const handleQuickAction = async (actionType, prompt) => {
    if (!code.trim()) {
      setError('Please enter code before using Quick Action');
      return;
    }

    setLoading(true);
    setError('');

    const message = `${prompt}\n\n\`\`\`${language}\n${code}\n\`\`\``;

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message: message,
        history: [],
        is_quick_action: true
      });

      if (response.data.success) {
        setCommentedCode(response.data.response);
        setTokensInfo(response.data.tokens_info);
        setError('');
      } else {
        setError(response.data.error || 'An error occurred while processing Quick Action');
      }
    } catch (err) {
      console.error('Quick Action error:', err);
      setError('Unable to connect to AI Assistant');
    } finally {
      setLoading(false);
    }
  };

  const handleCommentCode = () => handleQuickAction('comment', 'Add detailed comments in Vietnamese to this code, explain what each part does:');
  const handleFindBugs = () => handleQuickAction('debug', 'Find and fix bugs in this code:');
  const handleOptimize = () => handleQuickAction('optimize', 'Optimize the performance of this code:');
  const handleGenerateTests = () => handleQuickAction('test', 'Generate unit tests for this code:');

  return (
    <div className="App">
      <header className="app-header">
        <h1>🤖 AI Programming Assistant</h1>
        <p>Smart programming support with AI - Comment code, Debug, Optimize & More</p>
      </header>

      <main className="app-main">
        <div className="controls">
          <div className="controls-left">
            <div className="language-selector">
              <label htmlFor="language">Programming Language:</label>
              <select
                id="language"
                value={language}
                onChange={(e) => handleLanguageChange(e.target.value)}
              >
                {supportedLanguages.map((lang) => (
                  <option key={lang.value} value={lang.value}>
                    {lang.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="action-buttons">
              <input
                type="file"
                ref={(ref) => setFileInputRef(ref)}
                onChange={handleFileUpload}
                accept=".txt,.js,.jsx,.ts,.tsx,.py,.java,.cpp,.c,.cs,.php,.rb,.go,.rs,.swift,.kt,.scala,.clj,.sh,.sql,.html,.css,.json,.xml,.yaml,.yml"
                style={{ display: 'none' }}
              />
              <button
                onClick={triggerFileUpload}
                className="btn btn-secondary"
              >
                📁 Upload File
              </button>
              <button
                onClick={handleClearAll}
                className="btn btn-secondary"
              >
                🗑️ Clear All
              </button>
            </div>
          </div>

          <div className="controls-right">
            {/* Quick Actions */}
            <div className="quick-actions">
              <div className="quick-action-buttons">
                <button
                  onClick={handleCommentCode}
                  className="btn btn-quick-action"
                  disabled={loading || !code.trim()}
                  title="Add detailed comments to code"
                >
                  <span style={{fontSize: '1rem', marginRight: '0.4rem'}}>💬</span>
                  Comment Code
                </button>
                <button
                  onClick={handleFindBugs}
                  className="btn btn-quick-action"
                  disabled={loading || !code.trim()}
                  title="Find and fix bugs in code"
                >
                  <span style={{fontSize: '1rem', marginRight: '0.4rem'}}>🐛</span>
                  Find Bugs
                </button>
                <button
                  onClick={handleOptimize}
                  className="btn btn-quick-action"
                  disabled={loading || !code.trim()}
                  title="Optimize code performance"
                >
                  <span style={{fontSize: '1rem', marginRight: '0.4rem'}}>⚡</span>
                  Optimize
                </button>
                <button
                  onClick={handleGenerateTests}
                  className="btn btn-quick-action"
                  disabled={loading || !code.trim()}
                  title="Generate unit tests for code"
                >
                  <span style={{fontSize: '1rem', marginRight: '0.4rem'}}>🧪</span>
                  Generate Tests
                </button>
              </div>
            </div>
          </div>
        </div>

        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}

        <div className="code-sections">
          <div className="code-section">
            <h3>📥 Input</h3>
            <CodeEditor
              value={code}
              onChange={setCode}
              language={language}
              placeholder={`Enter or paste ${language} code here...`}
              rows={15}
            />
          </div>

          <div className="code-section">
            <h3>📤 Output</h3>
            {loading ? (
              <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>Processing code with AI...</p>
              </div>
            ) : commentedCode ? (
              <div className="code-output">
                <SyntaxHighlighter
                  language={language}
                  style={tomorrow}
                  showLineNumbers={true}
                  wrapLines={true}
                >
                  {commentedCode}
                </SyntaxHighlighter>
              </div>
            ) : (
              <div className="placeholder">
                AI Assistant output will be displayed here...
              </div>
            )}
          </div>
        </div>

        {commentedCode && (
          <div className="stats">
            {tokensInfo && (
              <div className="stats-row">
                <p>
                  📊 <strong>Tokens:</strong> 
                  Input ~{tokensInfo.estimated_input_tokens} tokens | 
                  Max allowed: {tokensInfo.max_tokens_used} tokens | 
                  Output ~{tokensInfo.estimated_output_tokens} tokens
                </p>
                <p className="cost-estimate">
                  💰 <strong>Cost estimate:</strong> 
                  ~${((tokensInfo.estimated_input_tokens * 0.00015 + tokensInfo.estimated_output_tokens * 0.0006) / 1000).toFixed(4)} USD
                </p>
              </div>
            )}
          </div>
        )}
      </main>

      <HowToUse />

      <footer className="app-footer">
        <p>
          © 2025 <strong>[AI-Elevate] X-Eyes Team</strong> - All rights reserved
        </p>
      </footer>

      {/* Floating Chat Button */}
      <button
        onClick={toggleChat}
        className={`floating-chat-btn ${chatVisible ? 'active' : ''}`}
        title={chatVisible ? "Close AI Assistant" : "Open AI Assistant"}
      >
        {chatVisible ? '✕' : '🤖'}
      </button>

      {/* Chat Assistant Sidebar */}
      <ChatAssistant 
        isVisible={chatVisible} 
        onToggle={toggleChat}
        currentCode={code}
        currentLanguage={language}
        onChatResult={handleChatResult}
      />
    </div>
  );
}

export default App;
