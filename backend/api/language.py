"""
Language API - Các endpoint liên quan đến ngôn ngữ lập trình

Chứa:
- GET /api/languages: Lấy danh sách ngôn ngữ lập trình được hỗ trợ
- Xác thực ngôn ngữ và metadata
"""

from flask import Blueprint, jsonify
from flasgger import swag_from

# Tạo Blueprint cho API ngôn ngữ
language_bp = Blueprint('language', __name__)

@language_bp.route('/languages', methods=['GET'])
@swag_from({
    'tags': ['language'],
    'summary': 'Get supported programming languages',
    'description': 'Get list of programming languages supported by AI Assistant',
    'responses': {
        200: {
            'description': 'List of languages returned successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'languages': {
                        'type': 'array',
                        'description': 'List of languages with value and label',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'value': {
                                    'type': 'string', 
                                    'description': 'Language code value',
                                    'example': 'java'
                                },
                                'label': {
                                    'type': 'string',
                                    'description': 'Language display name', 
                                    'example': 'Java'
                                },
                                'description': {
                                    'type': 'string',
                                    'description': 'Brief language description',
                                    'example': 'Object-oriented programming language'
                                }
                            }
                        }
                    },
                    'total': {
                        'type': 'integer',
                        'description': 'Total number of supported languages',
                        'example': 9
                    }
                }
            }
        }
    }
})
def get_supported_languages():
    """
    Lấy danh sách các ngôn ngữ lập trình được hỗ trợ bởi AI Assistant
    
    Returns:
        JSON response chứa danh sách ngôn ngữ, mỗi ngôn ngữ bao gồm:
        - value: Mã code để gọi API
        - label: Tên hiển thị cho giao diện
        - description: Mô tả ngắn gọn về ngôn ngữ
    """
    # Danh sách ngôn ngữ được hỗ trợ với metadata đầy đủ
    languages = [
        {
            "value": "java", 
            "label": "Java",
            "description": "Object-oriented programming language"
        },
        {
            "value": "python", 
            "label": "Python",
            "description": "High-level programming language"
        },
        {
            "value": "javascript", 
            "label": "JavaScript",
            "description": "Dynamic programming language"
        },
        {
            "value": "typescript", 
            "label": "TypeScript",
            "description": "JavaScript with static typing"
        },
        {
            "value": "cpp", 
            "label": "C++",
            "description": "Systems programming language"
        },
        {
            "value": "c", 
            "label": "C",
            "description": "Low-level programming language"
        },
        {
            "value": "csharp", 
            "label": "C#",
            "description": "Microsoft programming language"
        },
        {
            "value": "go", 
            "label": "Go",
            "description": "Google programming language"
        },
        {
            "value": "rust", 
            "label": "Rust",
            "description": "Systems programming language"
        }
    ]
    
    return jsonify({
        "success": True,
        "languages": languages,
        "total": len(languages)
    })

@language_bp.route('/languages/<language_code>', methods=['GET'])
@swag_from({
    'tags': ['language'],
    'summary': 'Get specific language information',
    'description': 'Get detailed information about a specific programming language',
    'parameters': [
        {
            'name': 'language_code',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Language code (java, python, javascript, etc.)',
            'example': 'java'
        }
    ],
    'responses': {
        200: {
            'description': 'Language information returned successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'language': {
                        'type': 'object',
                        'properties': {
                            'value': {'type': 'string', 'example': 'java'},
                            'label': {'type': 'string', 'example': 'Java'},
                            'description': {'type': 'string', 'example': 'Object-oriented programming language'},
                            'features': {
                                'type': 'array',
                                'items': {'type': 'string'},
                                'example': ['Comment support', 'Bug fixing', 'Code optimization']
                            }
                        }
                    }
                }
            }
        },
        404: {
            'description': 'Language not supported',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': False},
                    'error': {'type': 'string', 'example': 'Language not supported'}
                }
            }
        }
    }
})
def get_language_info(language_code):
    """
    Lấy thông tin chi tiết về một ngôn ngữ lập trình cụ thể
    
    Args:
        language_code (str): Mã ngôn ngữ cần lấy thông tin
        
    Returns:
        JSON response chứa thông tin chi tiết về ngôn ngữ
    """
    # Ánh xạ ngôn ngữ với thông tin chi tiết
    language_details = {
        "java": {
            "value": "java",
            "label": "Java",
            "description": "Object-oriented programming language",
            "features": ["JavaDoc comments", "Bug detection", "Performance optimization", "Unit testing", "Code explanation"]
        },
        "python": {
            "value": "python",
            "label": "Python",
            "description": "High-level programming language",
            "features": ["Docstring comments", "Bug detection", "Code optimization", "Unit testing", "Algorithm explanation"]
        },
        "javascript": {
            "value": "javascript",
            "label": "JavaScript",
            "description": "Dynamic programming language",
            "features": ["JSDoc comments", "Bug detection", "Performance optimization", "Unit testing", "Async code explanation"]
        },
        "typescript": {
            "value": "typescript",
            "label": "TypeScript",
            "description": "JavaScript with static typing",
            "features": ["TSDoc comments", "Type checking", "Code refactoring", "Unit testing", "Type explanation"]
        },
        "cpp": {
            "value": "cpp",
            "label": "C++",
            "description": "Systems programming language",
            "features": ["Doxygen comments", "Memory leak detection", "Performance optimization", "Unit testing", "Pointer explanation"]
        },
        "c": {
            "value": "c",
            "label": "C",
            "description": "Low-level programming language",
            "features": ["C-style comments", "Memory management", "Performance optimization", "Testing", "Low-level explanation"]
        },
        "csharp": {
            "value": "csharp",
            "label": "C#",
            "description": "Microsoft programming language",
            "features": ["XML documentation", "Exception handling", "LINQ optimization", "Unit testing", ".NET explanation"]
        },
        "go": {
            "value": "go",
            "label": "Go",
            "description": "Google programming language",
            "features": ["GoDoc comments", "Race condition detection", "Goroutine optimization", "Testing", "Concurrency explanation"]
        },
        "rust": {
            "value": "rust",
            "label": "Rust",
            "description": "Systems programming language",
            "features": ["Rustdoc comments", "Ownership checking", "Performance optimization", "Unit testing", "Memory safety explanation"]
        }
    }
    
    # Tìm kiếm ngôn ngữ theo mã code
    language_info = language_details.get(language_code.lower())
    
    if language_info:
        return jsonify({
            "success": True,
            "language": language_info
        })
    else:
        return jsonify({
            "success": False,
            "error": f"Language '{language_code}' is not supported"
        }), 404
