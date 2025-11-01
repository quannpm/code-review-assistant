"""
Cấu hình Swagger Documentation cho AI Programming Assistant API

File này chứa các thiết lập cho Swagger UI và tài liệu API
Tách biệt cấu hình khỏi code ứng dụng chính
"""

# Cấu hình Swagger UI và tài liệu API
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # Bao gồm tất cả routes
            "model_filter": lambda tag: True,  # Bao gồm tất cả models
        }
    ],
    "static_url_path": "/flasgger_static",  # Đường dẫn cho static files của Swagger
    "swagger_ui": True,                     # Bật Swagger UI
    "specs_route": "/swagger/"              # Route để truy cập Swagger UI
}

# Template chứa thông tin metadata của API với chi tiết endpoints
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "AI Programming Assistant API",
        "description": "AI-powered programming assistance API with chat, language support and health monitoring",
        "version": "3.0.0",
        "contact": {
            "name": "AI Programming Assistant Team",
            "email": "support@aiprogrammingassistant.com"
        }
    },
    "host": "localhost:8888",              # Host và port của API
    "basePath": "/api",                    # Đường dẫn gốc cho tất cả endpoints
    "schemes": ["http", "https"],          # Giao thức được hỗ trợ
    "tags": [
        {
            "name": "chat", 
            "description": "🤖 AI Chat Operations - Chat with AI Assistant via /api/chat"
        },
        {
            "name": "language",
            "description": "🌐 Language Support - Programming language management via /api/languages"
        },
        {
            "name": "health",
            "description": "💚 Health Check Operations - API status monitoring via /api/health"
        },
        {
            "name": "knowledge-base",
            "description": "📚 Knowledge Base Operations - Upload and manage PDF documents via /api/knowledge-base"
        },
        {
            "name": "tts",
            "description": "🔊 Text-to-Speech Operations - Convert text to audio via /api/tts"
        }
    ],
    "paths": {
        "/chat": {
            "post": {
                "tags": ["chat"],
                "summary": "Chat with AI Assistant",
                "description": "Main endpoint for chatting with AI Assistant - supports both normal chat and quick actions"
            }
        },
        "/languages": {
            "get": {
                "tags": ["language"],
                "summary": "Get supported languages",
                "description": "Get list of all supported programming languages"
            }
        },
        "/languages/{language_code}": {
            "get": {
                "tags": ["language"],
                "summary": "Get specific language info",
                "description": "Get detailed information about a specific programming language"
            }
        },
        "/health": {
            "get": {
                "tags": ["health"],
                "summary": "Basic health check",
                "description": "Check basic status of API server"
            }
        },
        "/knowledge-base/upload": {
            "post": {
                "tags": ["knowledge-base"],
                "summary": "Upload PDF file",
                "description": "Upload a PDF file to build knowledge base for AI Assistant"
            }
        },
        "/knowledge-base/files": {
            "get": {
                "tags": ["knowledge-base"],
                "summary": "List uploaded files",
                "description": "Get list of all uploaded PDF files in knowledge base"
            }
        },
        "/knowledge-base/search": {
            "post": {
                "tags": ["knowledge-base"],
                "summary": "Search knowledge base",
                "description": "Search for relevant content using vector similarity"
            }
        },
        "/knowledge-base/chunks": {
            "get": {
                "tags": ["knowledge-base"],
                "summary": "Get all chunks",
                "description": "Get all text chunks from ChromaDB"
            }
        },
        "/knowledge-base/reset": {
            "post": {
                "tags": ["knowledge-base"],
                "summary": "Reset ChromaDB",
                "description": "Reset ChromaDB - Delete all chunks and recreate collection"
            }
        },
        "/knowledge-base/clear": {
            "post": {
                "tags": ["knowledge-base"],
                "summary": "Clear all chunks",
                "description": "Clear all chunks from ChromaDB but keep collection"
            }
        },
        "/knowledge-base/chat": {
            "post": {
                "tags": ["knowledge-base"],
                "summary": "Chat with Knowledge Base",
                "description": "Chat with AI Assistant using vector database as knowledge source"
            }
        },
        "/tts": {
            "post": {
                "tags": ["tts"],
                "summary": "Convert text to speech",
                "description": "Convert text input to audio output in base64 format"
            }
        }
    }
}
