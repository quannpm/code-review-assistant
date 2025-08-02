import React, { useState, useEffect } from 'react';
import ChatBot from "./components/ChatBot";
import axios from 'axios';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './App.css';

const API_BASE_URL = 'http://localhost:5000/api';

function App() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('java');
  const [commentedCode, setCommentedCode] = useState('');
  const [tokensInfo, setTokensInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [supportedLanguages, setSupportedLanguages] = useState([]);

  // Sample code examples
  const sampleCodes = {
    java: `public class MaxFinder {
    
    public int findMax(int[] numbers) {
        if (numbers == null || numbers.length == 0) {
            throw new IllegalArgumentException("Array cannot be null or empty");
        }
        
        int max = numbers[0];
        for (int i = 1; i < numbers.length; i++) {
            if (numbers[i] > max) {
                max = numbers[i];
            }
        }
        return max;
    }
    
    public static void main(String[] args) {
        MaxFinder finder = new MaxFinder();
        int[] array = {5, 2, 9, 1, 7, 6};
        int maxInArray = finder.findMax(array);
        System.out.println("Max in array: " + maxInArray);
    }
}`,
    python: `def find_max(numbers):
    if not numbers:
        raise ValueError("List cannot be empty")
    
    max_val = numbers[0]
    for num in numbers[1:]:
        if num > max_val:
            max_val = num
    return max_val

def main():
    numbers = [5, 2, 9, 1, 7, 6]
    result = find_max(numbers)
    print(f"Max in list: {result}")

if __name__ == "__main__":
    main()`,
    javascript: `function findMax(numbers) {
    if (!numbers || numbers.length === 0) {
        throw new Error("Array cannot be null or empty");
    }
    
    let max = numbers[0];
    for (let i = 1; i < numbers.length; i++) {
        if (numbers[i] > max) {
            max = numbers[i];
        }
    }
    return max;
}

const numbers = [5, 2, 9, 1, 7, 6];
const result = findMax(numbers);
console.log("Max in array:", result);`
  };

  useEffect(() => {
    // Fetch supported languages
    const fetchLanguages = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/supported-languages`);
        if (response.data.success) {
          setSupportedLanguages(response.data.languages);
        }
      } catch (err) {
        console.error('Error fetching languages:', err);
      }
    };

    fetchLanguages();
    
    // Set initial sample code
    setCode(sampleCodes[language]);
  }, []);

  const handleLanguageChange = (newLanguage) => {
    setLanguage(newLanguage);
    setCode(sampleCodes[newLanguage] || '');
    setCommentedCode('');
    setTokensInfo(null);
    setError('');
  };

  const handleCommentCode = async () => {
    if (!code.trim()) {
      setError('Vui lòng nhập code để comment');
      return;
    }

    setLoading(true);
    setError('');
    setCommentedCode('');

    try {
      const response = await axios.post(`${API_BASE_URL}/comment-code`, {
        code: code,
        language: language
      });

      if (response.data.success) {
        setCommentedCode(response.data.commented_code);
        setTokensInfo(response.data.tokens_info || null);
      } else {
        setError(response.data.error || 'Có lỗi xảy ra khi xử lý code');
      }
    } catch (err) {
      console.error('Error commenting code:', err);
      setError(
        err.response?.data?.error || 
        'Không thể kết nối đến server. Vui lòng kiểm tra backend đã chạy chưa.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleClearAll = () => {
    setCode('');
    setCommentedCode('');
    setTokensInfo(null);
    setError('');
  };

  const handleLoadSample = () => {
    setCode(sampleCodes[language] || '');
    setCommentedCode('');
    setTokensInfo(null);
    setError('');
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🚀 Code Commenter</h1>
        <p>Tự động tạo comment cho code sử dụng AI</p>
      </header>

      <main className="app-main">
        <div className="controls">
          <div className="language-selector">
            <label htmlFor="language">Ngôn ngữ lập trình:</label>
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
            <button
              onClick={handleLoadSample}
              className="btn btn-secondary"
            >
              📝 Load Sample Code
            </button>
            <button
              onClick={handleClearAll}
              className="btn btn-secondary"
            >
              🗑️ Clear All
            </button>
            <button
              onClick={handleCommentCode}
              disabled={loading || !code.trim()}
              className="btn btn-primary"
            >
              {loading ? '⏳ Đang xử lý...' : '✨ Comment Code'}
            </button>
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
            <textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder={`Nhập ${language} code tại đây...`}
              className="code-input"
              rows={15}
            />
          </div>

          <div className="code-section">
            <h3>📤 Output</h3>
            {loading ? (
              <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>Đang xử lý code bằng AI...</p>
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
                Code đã được comment sẽ hiển thị tại đây...
              </div>
            )}
          </div>
        </div>

        {commentedCode && (
          <div className="stats">
            <div className="stats-row">
              <p>
                📊 <strong>Thống kê:</strong> Code gốc {code.length} ký tự → Code đã comment {commentedCode.length} ký tự
              </p>
            </div>
            
            {tokensInfo && (
              <div className="stats-row tokens-info">
                <p>
                  🔢 <strong>Tokens:</strong> 
                  Input ~{tokensInfo.estimated_input_tokens} tokens | 
                  Max allowed: {tokensInfo.max_tokens_used} tokens | 
                  Output ~{tokensInfo.estimated_output_tokens} tokens
                </p>
                <p className="cost-estimate">
                  💰 <strong>Ước tính chi phí:</strong> 
                  ~${((tokensInfo.estimated_input_tokens * 0.00015 + tokensInfo.estimated_output_tokens * 0.0006) / 1000).toFixed(4)} USD
                </p>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Thay vì chỉ <ChatBot /> */}
      <div className="chatbot-container">
        <ChatBot />
      </div>

      <footer className="app-footer">
        <p>
          💡 <strong>Step 1:</strong> Chọn ngôn ngữ và nhập code → 
          <strong> Step 2:</strong> AI xử lý và tạo comment → 
          <strong> Step 3:</strong> Nhận kết quả code đã được comment
        </p>
      </footer>
    </div>
  );
}

export default App;
