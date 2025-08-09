"""
Chat API - Xử lý tất cả các endpoint liên quan đến trò chuyện với AI Assistant

Module này chứa:
- POST /api/chat: Trò chuyện với AI Assistant (yêu cầu đơn lẻ)
- Hỗ trợ cả trò chuyện thông thường (normal chat) và các hành động nhanh (quick action)
"""

from flask import Blueprint, request, jsonify
from flasgger import swag_from
import traceback

# Tạo Blueprint cho API chat
chat_bp = Blueprint('chat', __name__)

def init_chat_api(ai_service):
    """
    Khởi tạo chat API với dependency injection cho AI service
    
    Args:
        ai_service: Instance của AIService để xử lý các thao tác AI
    """
    global _ai_service
    _ai_service = ai_service

@chat_bp.route('/chat', methods=['POST'])
@swag_from({
    'tags': ['chat'],
    'summary': 'Chat with AI Assistant',
    'description': 'Send message to AI Assistant and receive intelligent response',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'description': 'Message to send to AI Assistant',
                        'example': 'Hello, can you help me explain this code?'
                    },
                    'history': {
                        'type': 'array',
                        'description': 'Conversation history to maintain context',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'type': {'type': 'string', 'enum': ['user', 'bot']},
                                'content': {'type': 'string'}
                            }
                        }
                    },
                    'is_quick_action': {
                        'type': 'boolean',
                        'description': 'True if this is a quick action (comment, debug, optimize, test)',
                        'example': False
                    }
                },
                'required': ['message']
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'AI response generated successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'response': {
                        'type': 'string', 
                        'example': 'Hello! I can help you explain code. Please share the code you want me to explain.'
                    }
                }
            }
        },
        '400': {
            'description': 'Bad request - invalid input data',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': False},
                    'error': {'type': 'string', 'example': 'Message is required'}
                }
            }
        },
        '500': {
            'description': 'Internal server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': False},
                    'error': {'type': 'string', 'example': 'Error processing request'}
                }
            }
        }
    }
})
def chat():
    """
    Endpoint trò chuyện - Giao tiếp với AI Assistant thông qua cuộc hội thoại
    
    Hỗ trợ 2 chế độ:
    1. Hành động nhanh: Trả về code đã được xử lý (comment, debug, optimize, test)
    2. Trò chuyện thông thường: Trả lời câu hỏi, giải thích code với ngữ cảnh đầy đủ
    
    Quy trình xử lý:
    1. Xác thực dữ liệu yêu cầu
    2. Trích xuất message, history và is_quick_action
    3. Gọi AI service để xử lý
    4. Trả về phản hồi hoặc lỗi
    """
    try:
        # Bước 1: Xác thực dữ liệu yêu cầu
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Message is required"
            }), 400
        
        # Trích xuất các tham số từ yêu cầu
        message = data['message']
        history = data.get('history', [])                    # Lịch sử trò chuyện để duy trì ngữ cảnh
        is_quick_action = data.get('is_quick_action', False) # Cờ để phân biệt hành động nhanh vs trò chuyện thông thường
        
        if not message.strip():
            return jsonify({
                "success": False,
                "error": "Message cannot be empty"
            }), 400
        
        # Bước 2: Gọi AI service để xử lý
        result = _ai_service.chat_with_ai(
            message=message,
            history=history,
            is_quick_action=is_quick_action
        )
        
        # Bước 3: Trả về phản hồi
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
        
    except Exception as e:
        # Xử lý ngoại lệ và ghi log lỗi để debug
        print(f"Error in chat endpoint: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": f"Error processing chat: {str(e)}"
        }), 500
