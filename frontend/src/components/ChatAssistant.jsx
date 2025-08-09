import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import CodeBlock from './CodeBlock';
import { parseMessageContent, detectLanguage, formatTextContent } from '../utils/messageParser';
import './ChatAssistant.css';

const API_BASE_URL = 'http://localhost:8888/api';

const ChatAssistant = ({ isVisible, onToggle, currentCode, currentLanguage, onChatResult }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const chatEndRef = useRef(null);
  const inputRef = useRef(null);
  const chatRef = useRef(null);

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

    // For manual chat input, include current file content if available - Cho chat thủ công, bao gồm nội dung file hiện tại nếu có
    let finalMessage = messageText;
    if (!isQuickAction && currentCode && currentCode.trim()) {
      // Add current code context for chat questions - Thêm context code hiện tại cho câu hỏi chat
      finalMessage = `${messageText}\n\nCurrent code for reference:\n\`\`\`${currentLanguage}\n${currentCode}\n\`\`\``;
    }

    // For manual input (chat), always show in chat - Cho input thủ công (chat), luôn hiển thị trong chat
    // For quick actions, don't show in chat but show loading message - Cho quick actions, không hiển thị trong chat nhưng hiển thị tin nhắn loading
    if (!isQuickAction) {
      const userMessage = { type: 'user', content: messageText, timestamp: new Date() };
      setMessages(prev => [...prev, userMessage]);
    } else {
      // For quick actions, add a temporary loading message to show progress - Cho quick actions, thêm tin nhắn loading tạm thời để hiển thị tiến trình
      const loadingMessage = { 
        type: 'bot', 
        content: '🔄 Processing your code...', 
        timestamp: new Date(),
        isQuickActionLoading: true 
      };
      setMessages(prev => [...prev, loadingMessage]);
    }
    
    setInputMessage('');
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message: finalMessage, // Send message with context to API - Gửi tin nhắn với context đến API
        history: messages.slice(-10), // Last 10 messages for context - 10 tin nhắn cuối để làm context
        is_quick_action: isQuickAction // Add flag so backend knows this is quick action - Thêm flag để backend biết đây là quick action
      });

      if (response.data.success) {
        // Quick actions always go to output - Quick actions luôn chuyển đến output
        if (isQuickAction && onChatResult && response.data.response) {
          // Remove the loading message for quick actions - Xóa tin nhắn loading cho quick actions
          setMessages(prev => prev.filter(msg => !msg.isQuickActionLoading));
          onChatResult(response.data.response, response.data.tokens_info);
        } else {
          // Manual input always shows in chat - Input thủ công luôn hiển thị trong chat
          const botMessage = {
            type: 'bot',
            content: response.data.response,
            timestamp: new Date()
          };
          setMessages(prev => [...prev, botMessage]);
        }
      } else {
        // Remove loading message on error - Xóa tin nhắn loading khi có lỗi
        if (isQuickAction) {
          setMessages(prev => prev.filter(msg => !msg.isQuickActionLoading));
        }
        setError(response.data.error || 'An error occurred');
      }
    } catch (err) {
      console.error('Chat error:', err);
      // Remove loading message on error - Xóa tin nhắn loading khi có lỗi
      if (isQuickAction) {
        setMessages(prev => prev.filter(msg => !msg.isQuickActionLoading));
      }
      setError('Unable to connect to AI Assistant');
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
          <h3>AI Programming Assistant</h3>
        </div>
        <div className="chat-controls">
          <button 
            onClick={clearChat} 
            className="control-btn clear-btn"
            title="Clear chat"
          >
            🧽
          </button>
          <button 
            onClick={onToggle} 
            className="control-btn close-btn"
            title="Close chat"
          >
            X
          </button>
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <div className="welcome-icon">🚀</div>
            <h4>Welcome to AI Assistant!</h4>
            <p>I can help you with:</p>
            <ul>
              <li>Code explanation and algorithms</li>
              <li>Programming questions and answers</li>
              <li>Best practices guidance</li>
              <li>Architecture and design consulting</li>
              <li>Debugging and troubleshooting</li>
              <li>Code review and feedback</li>
            </ul>
            <p>💡 Get started by sending a message or asking programming questions!</p>
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
            placeholder="What would you like to ask?"
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
