# AI Programming Assistant

A comprehensive web-based AI assistant for developers with chat capabilities, code explanation, and quick action tools.

## 📋 Overview

AI Programming Assistant is a full-stack application designed to help developers:
- **AI Chat**: Ask questions and get programming consultation
- **Code Explanation**: Analyze and explain code snippets
- **Quick Actions**: Comment, debug, optimize, and test code
- **Multi-language**: Support for 9+ programming languages
- **API Documentation**: Integrated Swagger UI

## ⚡ Application Features

### 🤖 AI Chat Assistant
- **Programming Consultation**: Q&A about algorithms, data structures, and best practices
- **Problem Solving**: Debug code, identify errors and provide solutions
- **Code Review**: Evaluate and suggest code improvements
- **Learning Support**: Explain concepts, patterns, and frameworks

### 🧠 LangChain AI Integration
- **Prompt & Chain Management**: Sophisticated prompt engineering and chain orchestration for complex AI workflows
- **Vector Search**: Semantic search capabilities using ChromaDB for intelligent document retrieval
- **Function Calling**: Dynamic function execution based on AI decisions and user requests
- **Handle Prompts**: Advanced prompt handling with context management and response optimization
- **Chain Orchestration**: Sequential AI operations for complex programming tasks
- **Memory Management**: Persistent conversation context and session management

### 🔍 Code Analysis
- **Code Explanation**: Analyze logic and flow of code snippets
- **Code Documentation**: Auto-generate comments and documentation
- **Security Scan**: Detect potential security issues
- **Performance Analysis**: Evaluate performance and suggest optimizations

### Quick Actions
- **Add Comments**: Automatically add comments to code
- **Debug Code**: Detect and fix bugs in code
- **Optimize Code**: Improve performance and clean code
- **Generate Tests**: Create unit tests for functions/methods
- **Refactor Code**: Restructure code for better readability and maintainability
- **Format Code**: Auto-format code according to coding standards

### Real-time Chat
- **Code Q&A**: Explain syntax, functions, and logic of code snippets
- **Architecture Consultation**: System design, design patterns, and best practices
- **Debugging Support**: Help find and fix bugs in code
- **Code Review**: Evaluate code quality and suggest improvements
- **Learning Guidance**: Guide learning of new languages and frameworks
- **Technical Discussions**: Discuss algorithms, data structures, and performance
- **Project Consultation**: Advise on suitable technologies, tools, and workflows

### 🔊 Text-to-Speech (TTS)
- **Voice Synthesis**: Convert text to speech
- **Multiple Language Support**: Support reading text in multiple languages
- **Audio Streaming**: Return audio in base64 encoding format
- **Real-time Processing**: Fast and efficient TTS processing

### 📚 Knowledge Base
- **Document Upload**: Upload and process PDF files
- **Smart Search**: Search information in knowledge base
- **Content Extraction**: Extract and store content from documents
- **Vector Database**: Use ChromaDB for semantic search

## 🏗️ Project Structure

```
ai-assistant/
├── .env                         # Environment configuration
├── docker-compose.yml           # Container orchestration
├── Workshop_AI_Programming_Assistant.pptx  # Project presentation
├── backend/                     # Python Flask API
│   ├── app.py                   # Main application entry point
│   ├── Dockerfile               # Backend container config
│   ├── requirements.txt         # Python dependencies
│   ├── .env                     # Environment variables
│   ├── api/                     # API endpoints
│   │   ├── __init__.py
│   │   ├── chat_api.py          # AI Chat endpoints
│   │   ├── health_api.py        # Health check endpoints
│   │   ├── knowledge_base_api.py # Knowledge base endpoints
│   │   ├── language_api.py      # Language support endpoints
│   │   └── tts_api.py           # Text-to-Speech endpoints
│   ├── config/                  # Configuration modules
│   │   ├── __init__.py
│   │   └── swagger_config.py    # Swagger documentation config
│   ├── services/                # Business logic services
│   │   ├── __init__.py
│   │   ├── ai_service.py        # AI service logic
│   │   ├── knowledge_base_service.py # Knowledge base operations
│   │   └── langchain_service.py # LangChain integration
│   ├── chroma_db/               # Vector database storage
│   └── uploads/                 # File upload storage
├── frontend/                    # React Frontend
│   ├── Dockerfile               # Frontend container config
│   ├── index.html               # HTML entry point
│   ├── nginx.conf               # Nginx configuration
│   ├── package.json             # Node.js dependencies
│   ├── vite.config.js           # Vite build configuration
│   └── src/
│       ├── App.jsx              # Main React component
│       ├── App.css              # Main application styles
│       ├── main.jsx             # React entry point
│       ├── index.css            # Global styles
│       ├── components/          # Reusable UI components
│       │   ├── ChatAssistant.jsx/.css
│       │   ├── CodeBlock.jsx/.css
│       │   ├── CodeEditor.jsx/.css
│       │   ├── Footer.jsx/.css
│       │   ├── Header.jsx/.css
│       │   ├── HowToUse.jsx/.css
│       │   ├── LanguageSelector.jsx/.css
│       │   ├── MemoryPanel.jsx/.css
│       │   ├── MessageContent.jsx/.css
│       │   └── SessionManager.jsx
│       ├── contexts/            # React contexts
│       │   └── LanguageContext.jsx
│       ├── pages/               # Page components
│       │   ├── HomePage.jsx
│       │   └── KnowledgeBasePage.jsx/.css
│       ├── services/            # API service layer
│       │   └── apiService.js
│       └── utils/               # Utility functions
│           └── messageParser.js
├── nginx/                       # Load balancer configuration
│   └── nginx.conf
├── screenshots/                 # Project screenshots
└── README.md                    # Project documentation
```

## 🚀 Getting Started

### Quick Start with Docker

```bash
# 1. Clone repository
git clone <repository-url>
cd ai-assistant

# 2. Setup environment
# Create backend/.env file with Azure OpenAI credentials
echo "AZURE_OPENAI_ENDPOINT=your-endpoint" > backend/.env
echo "AZURE_OPENAI_API_KEY=your-key" >> backend/.env
echo "AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini" >> backend/.env

# 3. Start all services
docker-compose up --build
```

### Development Mode

```bash
# Backend only
cd backend
pip install -r requirements.txt
python app.py

# Frontend only
cd frontend
npm install
npm run dev
```

## 🔧 Backend

**Tech Stack:**
- **Flask**: Web framework
- **Azure OpenAI**: AI integration
- **LangChain**: AI framework for prompt management, chains, and function calling
- **pyttsx3**: Text-to-Speech engine
- **ChromaDB**: Vector database
- **PyPDF2**: PDF processing
- **Sentence Transformers**: Text embeddings
- **Flasgger**: Swagger documentation
- **Flask-CORS**: Cross-origin support

**Main Endpoints:**
- `POST /api/chat` - Chat with AI Assistant
- `GET /api/languages` - List of supported programming languages
- `GET /api/languages/<language_code>` - Get specific language details
- `GET /api/health` - Health check and system status
- `POST /api/tts` - Text-to-Speech conversion
- `POST /api/knowledge-base/upload` - Upload PDF documents
- `GET /api/knowledge-base/files` - List uploaded files
- `POST /api/knowledge-base/search` - Search knowledge base
- `POST /api/knowledge-base/chat` - Chat with knowledge base context
- `GET /api/knowledge-base/chunks` - Get all stored chunks
- `POST /api/knowledge-base/reset` - Reset knowledge base database
- `POST /api/knowledge-base/clear` - Clear all chunks
- `GET /api/knowledge-base/memory/sessions` - Get chat sessions
- `GET /api/knowledge-base/memory/history/<session_id>` - Get session history
- `POST /api/knowledge-base/memory/clear/<session_id>` - Clear session memory

**Key Features:**
- AI chat with context management
- LangChain prompt engineering and chain orchestration
- Function calling and dynamic AI operations
- Quick actions (comment, debug, optimize)
- Multi-language programming support
- Text-to-Speech functionality
- Knowledge base with PDF upload
- Vector search with ChromaDB
- Swagger API documentation
- Error handling and logging

## ⚛️ Frontend

**Tech Stack:**
- **React**: UI framework
- **Vite**: Build tool
- **CSS Modules**: Styling
- **Axios**: HTTP client

---

**Happy Coding! 🚀**
