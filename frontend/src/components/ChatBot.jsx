// src/components/ChatBot.jsx
import React, { useState, useRef, useEffect } from "react";
import axios from "axios";

const ChatBot = () => {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hi! How can I help you with code review today?" },
  ]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { role: "user", content: input }];
    setMessages(newMessages);
    setInput("");

    try {
      const filteredMessages = newMessages.filter(
        m => typeof m.content === 'string' && m.content.trim() !== ''
      );
      const response = await axios.post('http://localhost:5000/api/chat', { messages: filteredMessages });

      setMessages([
        ...newMessages,
        { role: "assistant", content: response.data.response || "Không nhận được phản hồi từ AI." }
      ]);
    } catch (error) {
      setMessages([
        ...newMessages,
        { role: "assistant", content: "Oops! Something went wrong." }
      ]);
    }
  };

  // Tự động scroll xuống cuối khi có tin nhắn mới
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="chatbot-box max-w-xl mx-auto mt-10 p-4 border rounded shadow">
      <div className="chatbot-messages h-64 overflow-y-auto space-y-2 mb-4 bg-gray-50 p-2 rounded">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`chatbot-bubble ${msg.role} ${msg.role === "user" ? "text-right" : "text-left"}`}
            style={{ alignSelf: msg.role === "user" ? "flex-end" : "flex-start" }}
          >
            <span className="px-3 py-2 rounded inline-block bg-white shadow">
              <strong>{msg.role === "user" ? "You" : "Bot"}:</strong> {msg.content}
            </span>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div className="chatbot-input-row flex gap-2">
        <input
          type="text"
          className="flex-1 border px-3 py-2 rounded"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button className="bg-blue-500 text-white px-4 py-2 rounded" onClick={sendMessage}>
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatBot;
