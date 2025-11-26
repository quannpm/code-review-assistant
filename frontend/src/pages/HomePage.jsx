import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import Header from '../components/Header';
import Footer from '../components/Footer';
import HowToUse from '../components/HowToUse';
import CodeEditor from '../components/CodeEditor';

function HomePage({
  onNavigate,
  language,
  displayLanguage,
  supportedLanguages,
  onLanguageChange,
  onFileUpload,
  fileInputRef,
  onClearAll,
  onCommentCode,
  onFindBugs,
  onOptimize,
  onGenerateTests,
  loading,
  code,
  setCode,
  error,
  commentedCode,
}) {
  return (
    <div className="page-container">
      <Header currentPage="home" onNavigate={onNavigate} />

      <main className="app-main">
        <div className="controls">
          <div className="controls-left">
            <div className="language-selector">
              <label htmlFor="language">{displayLanguage === 'vi' ? 'Ngôn ngữ lập trình:' : 'Programming Language:'}</label>
              <select
                id="language"
                value={language}
                onChange={(e) => onLanguageChange(e.target.value)}
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
                ref={fileInputRef}
                onChange={onFileUpload}
                accept=".txt,.js,.jsx,.ts,.tsx,.py,.java,.cpp,.c,.cs,.php,.rb,.go,.rs,.swift,.kt,.scala,.clj,.sh,.sql,.html,.css,.json,.xml,.yaml,.yml"
                style={{ display: 'none' }}
              />
              <button
                onClick={() => fileInputRef && fileInputRef.current && fileInputRef.current.click()}
                className="btn btn-secondary"
              >
                📁 {displayLanguage === 'vi' ? 'Tải Tập Tin' : 'Upload File'}
              </button>
              <button
                onClick={onClearAll}
                className="btn btn-secondary"
              >
                🗑️ {displayLanguage === 'vi' ? 'Xóa Tất Cả' : 'Clear All'}
              </button>
            </div>
          </div>

          <div className="controls-right">
            <div className="quick-actions">
              <div className="quick-action-buttons">
                <button
                  onClick={onCommentCode}
                  className="btn btn-quick-action"
                  disabled={loading || !code.trim()}
                  title={displayLanguage === 'vi' ? 'Thêm comment chi tiết vào code' : 'Add detailed comments to code'}
                >
                  <span style={{ fontSize: '1rem', marginRight: '0.2rem' }}>💬</span>
                  {displayLanguage === 'vi' ? 'Thêm Ghi Chú' : 'Comment Code'}
                </button>
                <button
                  onClick={onFindBugs}
                  className="btn btn-quick-action"
                  disabled={loading || !code.trim()}
                  title={displayLanguage === 'vi' ? 'Tìm và sửa lỗi trong code' : 'Find and fix bugs in code'}
                >
                  <span style={{ fontSize: '1rem', marginRight: '0.2rem' }}>🐛</span>
                  {displayLanguage === 'vi' ? 'Tìm Lỗi Code' : 'Find Bugs'}
                </button>
                <button
                  onClick={onOptimize}
                  className="btn btn-quick-action"
                  disabled={loading || !code.trim()}
                  title={displayLanguage === 'vi' ? 'Tối ưu hiệu suất code' : 'Optimize code performance'}
                >
                  <span style={{ fontSize: '1rem', marginRight: '0.2rem' }}>⚡</span>
                  {displayLanguage === 'vi' ? 'Tối Ưu Code' : 'Optimize Code'}
                </button>
                <button
                  onClick={onGenerateTests}
                  className="btn btn-quick-action"
                  disabled={loading || !code.trim()}
                  title={displayLanguage === 'vi' ? 'Tạo unit test cho code' : 'Generate unit tests for code'}
                >
                  <span style={{ fontSize: '1rem', marginRight: '0.2rem' }}>🧪</span>
                  {displayLanguage === 'vi' ? 'Tạo Unit Test' : 'Generate Tests'}
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
            <h3>📥 {displayLanguage === 'vi' ? 'Dữ Liệu' : 'Input'}</h3>
            <CodeEditor
              value={code}
              onChange={setCode}
              language={language}
              placeholder={displayLanguage === 'vi' ? `Nhập hoặc dán code ${language} vào đây...` : `Enter or paste ${language} code here...`}
              rows={15}
            />
          </div>

          <div className="code-section">
            <h3>📤 {displayLanguage === 'vi' ? 'Kết Quả' : 'Output'}</h3>
            {loading ? (
              <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>{displayLanguage === 'vi' ? 'Đang xử lý code với AI...' : 'Processing code with AI...'}</p>
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
                {displayLanguage === 'vi' ? 'Kết quả từ AI Assistant sẽ được hiển thị ở đây...' : 'AI Assistant output will be displayed here...'}
              </div>
            )}
          </div>
        </div>
      </main>

      <HowToUse />
      <Footer />
    </div>
  );
}

export default HomePage;
