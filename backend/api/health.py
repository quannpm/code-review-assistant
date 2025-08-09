"""
Health API - Xử lý các endpoints liên quan đến kiểm tra sức khỏe và giám sát hệ thống

Module này chứa:
- GET /api/health: Kiểm tra sức khỏe cơ bản của hệ thống
"""

from flask import Blueprint, jsonify
from flasgger import swag_from
from datetime import datetime

# Tạo Blueprint cho health API
health_bp = Blueprint('health', __name__)

def init_health_api(ai_service):
    """
    Khởi tạo health API với dependency injection cho AI service
    
    Args:
        ai_service: Instance của AIService để kiểm tra tình trạng AI service
    """
    global _ai_service
    _ai_service = ai_service

@health_bp.route('/health', methods=['GET'])
@swag_from({
    'tags': ['health'],
    'summary': 'Basic Health Check',
    'description': 'Check the basic status of the API server',
    'responses': {
        200: {
            'description': 'API is running normally',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {
                        'type': 'string', 
                        'example': 'healthy',
                        'description': 'Overall status of the API'
                    },
                    'message': {
                        'type': 'string', 
                        'example': 'AI Programming Assistant API is running',
                        'description': 'Status message'
                    },
                    'timestamp': {
                        'type': 'string', 
                        'example': '2025-08-02T10:30:00Z',
                        'description': 'Health check timestamp'
                    },
                    'version': {
                        'type': 'string', 
                        'example': '3.0.0',
                        'description': 'Current API version'
                    }
                }
            }
        }
    }
})
def health_check():
    """
    Endpoint kiểm tra sức khỏe cơ bản - Kiểm tra xem API server có đang chạy không
    
    Endpoint này luôn trả về 200 nếu server đang chạy.
    Được sử dụng bởi load balancer và các công cụ giám sát.
    
    Returns:
        JSON response chứa thông tin sức khỏe cơ bản
    """
    return jsonify({
        "status": "healthy",
        "message": "AI Programming Assistant API is running",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "3.0.0"
    })
