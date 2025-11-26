import React, { useState, useRef, useEffect } from 'react';
import CodeBlock from './CodeBlock';
import { parseMessageContent, detectLanguage, formatTextContent } from '../utils/messageParser';
import { useSession } from './SessionManager';
import { useLanguage } from '../contexts/LanguageContext';
import apiService from '../services/apiService';
import './ChatAssistant.css';

const ChatAssistant = ({ isVisible, onToggle, currentCode, currentLanguage, onChatResult }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const chatEndRef = useRef(null);
  const inputRef = useRef(null);
  const chatRef = useRef(null);

  // Use session context
  const { sessionId, addToSearchHistory } = useSession();
  
  // Use language context for display language
  const { language: displayLanguage } = useLanguage();

  // Auto scroll to bottom - Tự động cuộn xuống cuối
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus input when sidebar opens - Focus vào input khi sidebar mở
  useEffect(() => {
    if (isVisible && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isVisible]);

  // Handle click outside to close chat - Xử lý click bên ngoài để đóng chat
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (isVisible && chatRef.current && !chatRef.current.contains(event.target)) {
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

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (messageText = inputMessage, isQuickAction = false) => {
    if (!messageText.trim() || loading) return;

    // For manual chat input, include current file content if available
    let finalMessage = messageText;
    if (!isQuickAction && currentCode && currentCode.trim()) {
      finalMessage = `${messageText}\n\nCurrent code for reference:\n\`\`\`${currentLanguage}\n${currentCode}\n\`\`\``;
    }

    // Add message to UI if not quick action
    if (!isQuickAction) {
      const userMessage = { type: 'user', content: messageText, timestamp: new Date() };
      setMessages(prev => [...prev, userMessage]);
    } else {
      const loadingMessage = { 
        type: 'bot', 
        content: displayLanguage === 'vi' ? '🔄 Đang xử lý code của bạn...' : '🔄 Processing your code...', 
        timestamp: new Date(),
        isQuickActionLoading: true 
      };
      setMessages(prev => [...prev, loadingMessage]);
    }
    
    setInputMessage('');
    setLoading(true);
    setError('');

    try {
      // Debug log để kiểm tra ngôn ngữ
      console.log('Display language:', displayLanguage);
      console.log('Programming language:', currentLanguage);
      
      // Use apiService with session support (no need to send message history)
      const response = await apiService.chatWithAI(
        finalMessage,
        [], // Empty history since session is managed on backend
        isQuickAction,
        displayLanguage, // Ngôn ngữ hiển thị (en/vi)
        currentLanguage || 'javascript' // Ngôn ngữ lập trình
      );

      if (response.success) {
        // Add to search history for tracking
        addToSearchHistory({
          query: messageText,
          timestamp: new Date(),
          type: isQuickAction ? 'quick_action' : 'chat'
        });

        if (isQuickAction && onChatResult && response.response) {
          // Remove loading message and send to output
          setMessages(prev => prev.filter(msg => !msg.isQuickActionLoading));
          onChatResult(response.response, response.tokens_info);
        } else {
          // Show in chat
          const botMessage = {
            type: 'bot',
            content: response.response,
            timestamp: new Date()
          };
          setMessages(prev => [...prev, botMessage]);
        }
      } else {
        if (isQuickAction) {
          setMessages(prev => prev.filter(msg => !msg.isQuickActionLoading));
        }
        setError(response.error || (displayLanguage === 'vi' ? 'Đã xảy ra lỗi' : 'An error occurred'));
      }
    } catch (err) {
      console.error('Chat error:', err);
      if (isQuickAction) {
        setMessages(prev => prev.filter(msg => !msg.isQuickActionLoading));
      }
      setError(displayLanguage === 'vi' ? 'Không thể kết nối với Trợ Lý AI' : 'Unable to connect to AI Assistant');
    } finally {
      setLoading(false);
    }
  };

  const handleCommentCurrentCode = () => {
    if (currentCode && currentCode.trim()) {
      const message = `Please add detailed comments to this code:\n\n\`\`\`${currentLanguage}\n${currentCode}\n\`\`\``;
      handleSendMessage(message);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleInputChange = (e) => {
    setInputMessage(e.target.value);
    
    // Auto-resize textarea - Tự động thay đổi kích thước textarea
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = Math.min(inputRef.current.scrollHeight, 160) + 'px';
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError('');
    // Note: Session memory is not cleared here - only UI
    // Use SessionManager to clear actual memory if needed
  };

  const renderMessage = (message, index) => {
    const isUser = message.type === 'user';
    const isQuickActionLoading = message.isQuickActionLoading;
    
    return (
      <div key={index} className={`message ${isUser ? 'user' : 'bot'} ${isQuickActionLoading ? 'loading' : ''}`}>
        <div className="message-avatar">
          {isUser ? '👤' : '🤖'}
        </div>
        <div className="message-content">
          {isQuickActionLoading ? (
            <div className="message-text">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <span style={{ marginLeft: '0.5rem', fontSize: '0.9rem' }}>
                {message.content}
              </span>
            </div>
          ) : (
            <div className="message-text">
              {renderMessageContent(message.content)}
            </div>
          )}
          <div className="message-time">
            {message.timestamp.toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </div>
        </div>
      </div>
    );
  };

  const renderMessageContent = (content) => {
    // Parse content để tách text và code blocks
    const parts = parseMessageContent(content);
    
    return (
      <div className="message-parts">
        {parts.map((part, index) => {
          if (part.type === 'code') {
            // Detect language nếu không có hoặc là 'text'
            const language = part.language === 'text' || !part.language 
              ? detectLanguage(part.content) 
              : part.language;
              
            return (
              <CodeBlock
                key={index}
                code={part.content}
                language={language}
              />
            );
          } else {
            // Render text với line breaks
            return (
              <div 
                key={index} 
                className="text-part"
                dangerouslySetInnerHTML={{ 
                  __html: formatTextContent(part.content)
                }} 
              />
            );
          }
        })}
      </div>
    );
  };  return (
    <div ref={chatRef} className={`chat-assistant ${isVisible ? 'visible' : 'hidden'}`}>
      <div className="chat-header">
        <div className="chat-title">
          <span className="chat-icon">🤖</span>
          <h3>{displayLanguage === 'vi' ? 'Trợ Lý Lập Trình AI' : 'AI Programming Assistant'}</h3>
        </div>
        <div className="chat-controls">
          <button 
            onClick={clearChat} 
            className="control-btn clear-btn"
            title={displayLanguage === 'vi' ? 'Xóa cuộc trò chuyện' : 'Clear chat'}
          >
            🧽
          </button>
          <button 
            onClick={onToggle} 
            className="control-btn close-btn"
            title={displayLanguage === 'vi' ? 'Đóng chat' : 'Close chat'}
          >
            X
          </button>
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <div className="welcome-icon">🚀</div>
            <h4>{displayLanguage === 'vi' ? 'Chào mừng đến với Trợ Lý AI!' : 'Welcome to AI Assistant!'}</h4>
            <p>{displayLanguage === 'vi' ? 'Tôi có thể giúp bạn với:' : 'I can help you with:'}</p>
            <ul>
              {displayLanguage === 'vi' ? (
                <>
                  <li>Giải thích code và thuật toán</li>
                  <li>Câu hỏi và trả lời về lập trình</li>
                  <li>Hướng dẫn best practices</li>
                  <li>Tư vấn kiến trúc và thiết kế</li>
                  <li>Debug và khắc phục sự cố</li>
                  <li>Review code và phản hồi</li>
                </>
              ) : (
                <>
                  <li>Code explanation and algorithms</li>
                  <li>Programming questions and answers</li>
                  <li>Best practices guidance</li>
                  <li>Architecture and design consulting</li>
                  <li>Debugging and troubleshooting</li>
                  <li>Code review and feedback</li>
                </>
              )}
            </ul>
            <p>{displayLanguage === 'vi' ? '💡 Bắt đầu bằng cách gửi tin nhắn hoặc đặt câu hỏi về lập trình!' : '💡 Get started by sending a message or asking programming questions!'}</p>
          </div>
        ) : (
          messages.map(renderMessage)
        )}
        
        {loading && (
          <div className="message bot loading">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}
        
        <div ref={chatEndRef} />
      </div>

      <div className="chat-input">
        <div className="input-container">
          <textarea
            ref={inputRef}
            value={inputMessage}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder={displayLanguage === 'vi' ? 'Bạn muốn hỏi gì?' : 'What would you like to ask?'}
            className="message-input"
            rows="1"
            disabled={loading}
          />
          <button
            onClick={() => handleSendMessage()}
            disabled={!inputMessage.trim() || loading}
            className="send-btn"
          >
            {loading ? '⏳' : '📤'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatAssistant;
