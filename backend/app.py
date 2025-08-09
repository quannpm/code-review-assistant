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

# Import API modules
from api.chat import chat_bp, init_chat_api
from api.language import language_bp
from api.health import health_bp, init_health_api

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
    
    # Initialize AI Service
    ai_service = AIService()
    
    # Initialize API modules với dependency injection
    init_chat_api(ai_service)
    init_health_api(ai_service)
    
    # Register API Blueprints với prefix /api
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(language_bp, url_prefix='/api')
    app.register_blueprint(health_bp, url_prefix='/api')
    
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
                "health": "/api/health"
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
    print("⚙️ Make sure to set up your .env file with Azure OpenAI credentials")
    print("=" * 60)
    
    # Chạy development server
    app.run(
        debug=True,          # Enable debug mode cho development
        host='0.0.0.0',      # Listen trên tất cả interfaces
        port=8888            # Port 8888
    )
