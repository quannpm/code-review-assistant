"""
AI Programming Assistant API - Main Application

Cấu trúc modular mới với 3 API modules:
- Chat API: Giao tiếp với AI Assistant
- Language API: Quản lý ngôn ngữ lập trình
- Health API: Monitoring và health checks

Version 3.0.0 - Modular Architecture
"""

from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
import os
from dotenv import load_dotenv

# Import configuration
from config.swagger_config import swagger_config, swagger_template

# Import services
from services.ai_service import AIService
from services.langchain_service import LangchainService
from services.knowledge_base_service import KnowledgeBaseService

# Import API modules
from api.chat_api import chat_bp, init_chat_api
from api.language_api import language_bp
from api.health_api import health_bp, init_health_api
from api.knowledge_base_api import knowledge_base_bp, init_knowledge_base_api
from api.tts_api import tts_bp

# Load environment variables
load_dotenv()

def create_app():
    """
    Application factory pattern để tạo Flask app
    
    Returns:
        Flask app instance đã được cấu hình
    """
    # Tạo Flask application
    app = Flask(__name__)
    
    # Enable CORS cho tất cả routes
    CORS(app)
    
    # Initialize Swagger documentation
    swagger = Swagger(app, config=swagger_config, template=swagger_template)
    
    # Initialize Langchain Service
    langchain_service = LangchainService()
    
    # Initialize Knowledge Base Service với Langchain
    knowledge_base_service = KnowledgeBaseService()
    
    # Initialize AI Service với Langchain integration
    ai_service = AIService(langchain_service=langchain_service)
    
    # Initialize API modules với dependency injection
    init_chat_api(ai_service)
    init_health_api(ai_service)
    init_knowledge_base_api(knowledge_base_service)
    
    # Register API Blueprints với prefix /api
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(language_bp, url_prefix='/api')
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(knowledge_base_bp, url_prefix='/api')
    app.register_blueprint(tts_bp, url_prefix='/api')
    
    # Root endpoint để redirect đến Swagger UI
    @app.route('/')
    def root():
        """
        Root endpoint - redirect đến Swagger documentation
        """
        return {
            "message": "AI Programming Assistant API v3.0.0",
            "description": "Modular architecture với Chat, Language và Health APIs",
            "documentation": "/swagger/",
            "endpoints": {
                "chat": "/api/chat",
                "languages": "/api/languages",
                "health": "/api/health",
                "knowledge-base": "/api/knowledge-base",
                "tts": "/api/tts"
            }
        }
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return {
            "success": False,
            "error": "Endpoint not found",
            "message": "Check /swagger/ for available endpoints"
        }, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        return {
            "success": False,
            "error": "Internal server error",
            "message": "Something went wrong on our end"
        }, 500
    
    return app

# Tạo app instance
app = create_app()

if __name__ == '__main__':
    print("🚀 Starting AI Programming Assistant API v3.0.0...")
    print("📊 Swagger Documentation: http://localhost:8888/swagger/")
    print("💬 Chat API: http://localhost:8888/api/chat")
    print("🌐 Languages API: http://localhost:8888/api/languages") 
    print("💚 Health API: http://localhost:8888/api/health")
    print("📚 Knowledge Base API: http://localhost:8888/api/knowledge-base")
    print("🔊 TTS API: http://localhost:8888/api/tts")
    print("⚙️ Make sure to set up your .env file with Azure OpenAI credentials")
    print("=" * 60)
    
    # Chạy development server
    app.run(
        debug=True,          # Enable debug mode cho development
        host='0.0.0.0',      # Listen trên tất cả interfaces
        port=8888            # Port 8888
    )
