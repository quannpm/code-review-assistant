from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger, swag_from
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Swagger configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger/"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Code Commenter API",
        "description": "AI-powered code documentation API using Azure OpenAI",
        "version": "1.0.0",
        "contact": {
            "name": "Code Commenter Team",
            "email": "support@codecommenter.com"
        }
    },
    "host": "localhost:5000",
    "basePath": "/api",
    "schemes": ["http", "https"],
    "tags": [
        {
            "name": "comment",
            "description": "Code commenting operations"
        },
        {
            "name": "health",
            "description": "Health check operations"
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

class CodeCommenter:
    """Class để tự động tạo comment cho code"""
    
    def __init__(self):
        """Khởi tạo client Azure OpenAI"""
        try:
            self.client = AzureOpenAI(
                api_version="2024-07-01-preview",
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            )
            self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "GPT-4o-mini")
        except Exception as e:
            print(f"Error initializing Azure OpenAI client: {e}")
            self.client = None
    
    def _estimate_tokens(self, text):
        """
        Ước tính số tokens từ text (xấp xỉ 1 token = 4 characters cho tiếng Anh, 2-3 cho tiếng Việt)
        
        Args:
            text (str): Text cần ước tính
            
        Returns:
            int: Số tokens ước tính
        """
        # Công thức ước tính: 1 token ≈ 3-4 characters (trung bình)
        # Với text có tiếng Việt, tỷ lệ thấp hơn một chút
        return len(text) // 3
    
    def _calculate_max_tokens(self, input_tokens, code_length):
        """
        Tính toán max_tokens phù hợp dựa trên input
        
        Args:
            input_tokens (int): Số tokens của input
            code_length (int): Độ dài code gốc
            
        Returns:
            int: max_tokens được tính toán
        """
        # Ước tính output sẽ dài hơn input 2-3 lần (do thêm comment)
        estimated_output_tokens = input_tokens * 2.5
        
        # Tính dựa trên độ dài code: code dài hơn cần nhiều comment hơn
        code_based_tokens = code_length // 2  # 1 token per 2 characters of code
        
        # Lấy giá trị lớn hơn và thêm buffer 20%
        calculated_tokens = max(estimated_output_tokens, code_based_tokens) * 1.2
        
        # Giới hạn min/max tokens
        min_tokens = 500   # Tối thiểu cho response ngắn
        max_tokens = 8000  # Tối đa để tránh chi phí cao
        
        # Áp dụng giới hạn
        final_tokens = max(min_tokens, min(int(calculated_tokens), max_tokens))
        
        print(f"Token calculation: input={input_tokens}, code_len={code_length}, final_max_tokens={final_tokens}")
        return final_tokens
    
    def process_code(self, code_content, language="java"):
        """
        Xử lý code và tạo comments
        
        Args:
            code_content (str): Nội dung code cần được comment
            language (str): Ngôn ngữ lập trình (java, python, javascript, etc.)
            
        Returns:
            dict: Kết quả xử lý
        """
        if not self.client:
            return {
                "success": False,
                "error": "Azure OpenAI client not initialized"
            }
            
        if not code_content:
            return {
                "success": False,
                "error": "No code content provided"
            }
        
        # Tạo prompt dựa trên ngôn ngữ
        if language.lower() == "java":
            prompt = f"""
Bạn là một chuyên gia lập trình Java. Hãy phân tích đoạn code Java sau và thêm các comment tiếng Việt chi tiết:

1. Thêm JavaDoc cho các class, method và constructor
2. Thêm comment giải thích cho các dòng code phức tạp
3. Thêm comment mô tả logic và mục đích của từng phần
4. Giữ nguyên format và cấu trúc code gốc
5. Comment phải rõ ràng, dễ hiểu và hữu ích
6. Sử dụng format comment Java chuẩn (// và /* */)

Code Java cần comment:
```java
{code_content}
```

Trả về code Java đã được comment hoàn chỉnh:
"""
        elif language.lower() == "python":
            prompt = f"""
Bạn là một chuyên gia lập trình Python. Hãy phân tích đoạn code Python sau và thêm các comment tiếng Việt chi tiết:

1. Thêm docstring cho các hàm và class
2. Thêm comment giải thích cho các dòng code phức tạp
3. Thêm comment mô tả logic và mục đích của từng phần
4. Giữ nguyên format và cấu trúc code gốc
5. Comment phải rõ ràng, dễ hiểu và hữu ích

Code Python cần comment:
```python
{code_content}
```

Trả về code Python đã được comment hoàn chỉnh:
"""
        else:
            prompt = f"""
Bạn là một chuyên gia lập trình {language}. Hãy phân tích đoạn code sau và thêm các comment tiếng Việt chi tiết:

1. Thêm comment cho các hàm, class và phương thức
2. Thêm comment giải thích cho các dòng code phức tạp
3. Thêm comment mô tả logic và mục đích của từng phần
4. Giữ nguyên format và cấu trúc code gốc
5. Comment phải rõ ràng, dễ hiểu và hữu ích

Code {language} cần comment:
```{language}
{code_content}
```

Trả về code đã được comment hoàn chỉnh:
"""
        
        try:
            # Tính toán max_tokens dựa trên độ dài input
            input_tokens = self._estimate_tokens(prompt)
            max_tokens = self._calculate_max_tokens(input_tokens, len(code_content))
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=max_tokens
            )
            
            commented_code = response.choices[0].message.content.strip()
            
            # Loại bỏ markdown formatting nếu có
            for lang in ["java", "python", "javascript", "cpp", "c", "csharp"]:
                if commented_code.startswith(f"```{lang}"):
                    commented_code = commented_code.replace(f"```{lang}", "").replace("```", "").strip()
                    break
            
            if commented_code.startswith("```"):
                commented_code = commented_code.replace("```", "").strip()
            
            return {
                "success": True,
                "commented_code": commented_code,
                "original_length": len(code_content),
                "commented_length": len(commented_code),
                "tokens_info": {
                    "estimated_input_tokens": input_tokens,
                    "max_tokens_used": max_tokens,
                    "estimated_output_tokens": self._estimate_tokens(commented_code)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing code: {str(e)}"
            }

# Khởi tạo code commenter
commenter = CodeCommenter()

# Thêm biến toàn cục để lưu context code đã comment gần nhất
last_commented_code_context = {}

@app.route('/api/health', methods=['GET'])
@swag_from({
    'tags': ['health'],
    'summary': 'Health Check',
    'description': 'Check if the API is running and healthy',
    'responses': {
        200: {
            'description': 'API is healthy',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'example': 'healthy'},
                    'message': {'type': 'string', 'example': 'Code Commenter API is running'},
                    'timestamp': {'type': 'string', 'example': '2025-07-26T10:30:00Z'},
                    'version': {'type': 'string', 'example': '1.0.0'}
                }
            }
        }
    }
})
def health_check():
    """Health check endpoint"""
    from datetime import datetime
    return jsonify({
        "status": "healthy",
        "message": "Code Commenter API is running",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0"
    })

@app.route('/api/comment-code', methods=['POST'])
@swag_from({
    'tags': ['comment'],
    'summary': 'Generate code comments',
    'description': 'Generate AI-powered comments for source code using Azure OpenAI',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {
                        'type': 'string',
                        'description': 'Source code to be commented',
                        'example': 'public class HelloWorld {\n    public static void main(String[] args) {\n        System.out.println("Hello World");\n    }\n}'
                    },
                    'language': {
                        'type': 'string',
                        'description': 'Programming language of the code',
                        'enum': ['java', 'python', 'javascript', 'cpp', 'c', 'csharp', 'go', 'rust'],
                        'default': 'java',
                        'example': 'java'
                    }
                },
                'required': ['code']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Successfully generated comments',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'commented_code': {
                        'type': 'string',
                        'description': 'Code with AI-generated comments',
                        'example': '/**\n * HelloWorld class - Main entry point\n */\npublic class HelloWorld {\n    /**\n     * Main method\n     * @param args Command line arguments\n     */\n    public static void main(String[] args) {\n        System.out.println("Hello World");\n    }\n}'
                    },
                    'original_length': {'type': 'integer', 'example': 120},
                    'commented_length': {'type': 'integer', 'example': 280},
                    'tokens_info': {
                        'type': 'object',
                        'properties': {
                            'estimated_input_tokens': {'type': 'integer', 'example': 45},
                            'max_tokens_used': {'type': 'integer', 'example': 200},
                            'estimated_output_tokens': {'type': 'integer', 'example': 89}
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Bad request - Invalid input',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': False},
                    'error': {'type': 'string', 'example': 'No code content provided'}
                }
            }
        },
        500: {
            'description': 'Internal server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': False},
                    'error': {'type': 'string', 'example': 'Azure OpenAI API error'}
                }
            }
        }
    }
})
def comment_code():
    """
    API endpoint để comment code
    
    Expected JSON payload:
    {
        "code": "code content here",
        "language": "java" (optional, defaults to "java")
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        code_content = data.get('code', '')
        language = data.get('language', 'java')
        
        if not code_content.strip():
            return jsonify({
                "success": False,
                "error": "No code content provided"
            }), 400
        
        # Xử lý code
        result = commenter.process_code(code_content, language)
        
        if result["success"]:
            # Lưu lại context cho chatbot (ở đây lưu luôn cả code gốc và code đã comment)
            last_commented_code_context["context"] = {
                "original_code": code_content,
                "commented_code": result["commented_code"],
                "language": language
            }
            return jsonify(result), 200
        else:
            return jsonify(result), 500

    except Exception as e:
        print(f"Error in comment_code endpoint: {e}")
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500

@app.route('/api/supported-languages', methods=['GET'])
@swag_from({
    'tags': ['comment'],
    'summary': 'Get supported programming languages',
    'description': 'Retrieve list of programming languages supported by the code commenter',
    'responses': {
        200: {
            'description': 'List of supported languages',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'languages': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'value': {'type': 'string', 'example': 'java'},
                                'label': {'type': 'string', 'example': 'Java'}
                            }
                        }
                    }
                }
            }
        }
    }
})
def get_supported_languages():
    """Lấy danh sách ngôn ngữ được hỗ trợ"""
    languages = [
        {"value": "java", "label": "Java"},
        {"value": "python", "label": "Python"},
        {"value": "javascript", "label": "JavaScript"},
        {"value": "typescript", "label": "TypeScript"},
        {"value": "cpp", "label": "C++"},
        {"value": "c", "label": "C"},
        {"value": "csharp", "label": "C#"},
        {"value": "go", "label": "Go"},
        {"value": "rust", "label": "Rust"}
    ]
    return jsonify({
        "success": True,
        "languages": languages
    })

@app.route('/api/chat', methods=['POST'])
@swag_from({
    'tags': ['chat'],
    'summary': 'Gửi câu hỏi cho chatbot',
    'description': 'Chatbot AI trả lời bằng Azure OpenAI.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'messages': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'role': {'type': 'string', 'example': 'user'},
                                'content': {'type': 'string', 'example': 'Trình bày về LLM'}
                            }
                        }
                    }
                },
                'example': {
                    'messages': [
                        {'role': 'user', 'content': 'Trình bày về LLM'}
                    ]
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Phản hồi từ chatbot',
            'schema': {
                'type': 'object',
                'properties': {
                    'response': {'type': 'string'}
                }
            }
        }
    }
})
def chat_with_ai():
    """Chat với AI sử dụng lại client đã có, có thể truyền thêm context về code đã comment"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No JSON data provided"}), 400

        messages = data.get("messages", [])
        # Lọc bỏ message không hợp lệ
        messages = [m for m in messages if isinstance(m.get("content"), str) and m.get("content").strip() != ""]

        context = last_commented_code_context.get("context", None)

        if not messages:
            return jsonify({"success": False, "error": "messages is required"}), 400

        if not commenter.client:
            return jsonify({"success": False, "error": "AI client not initialized"}), 500

        if context:
            context_text = f"Đây là đoạn code đã được comment:\n\n{context['commented_code']}\n\nNgôn ngữ: {context['language']}"
            messages = [{"role": "system", "content": context_text}] + messages

        response = commenter.client.chat.completions.create(
            model=commenter.deployment_name,
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )

        return jsonify({"success": True, "response": response.choices[0].message.content.strip()})

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Code Commenter API...")
    print("Make sure to set up your .env file with Azure OpenAI credentials")
    app.run(debug=True, host='0.0.0.0', port=5000)
