"""
AI Service - Xử lý tất cả logic liên quan đến Azure OpenAI

Class này chứa:
- Kết nối Azure OpenAI client
- Token estimation và calculation
- Chat với AI Assistant
- Function calling capabilities
"""

import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class AIService:
    """
    Service class chuyên xử lý AI operations thông qua Azure OpenAI
    
    Chức năng chính:
    - Chat với AI Assistant (normal chat và quick actions)
    - Function calling để xử lý tác vụ chuyên biệt
    - Token management và cost optimization
    - Context management cho conversations
    """
    
    def __init__(self):
        """
        Khởi tạo Azure OpenAI client để kết nối với AI service
        
        Sử dụng environment variables để lấy:
        - AZURE_OPENAI_ENDPOINT: URL endpoint của Azure OpenAI
        - AZURE_OPENAI_API_KEY: API key để xác thực
        - AZURE_OPENAI_DEPLOYMENT_NAME: Tên deployment model (mặc định: GPT-4o-mini)
        """
        try:
            # Khởi tạo Azure OpenAI client với thông tin từ environment variables
            self.client = AzureOpenAI(
                api_version="2024-07-01-preview",                    # API version mới nhất hỗ trợ function calling
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),   # Endpoint Azure OpenAI từ .env
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),           # API key từ .env
            )
            # Tên deployment model, mặc định là GPT-4o-mini nếu không set trong .env
            self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "GPT-4o-mini")
            
        except Exception as e:
            print(f"Error initializing Azure OpenAI client: {e}")
            self.client = None  # Set None nếu không thể kết nối
    
    def _estimate_tokens(self, text):
        """
        Ước tính số tokens từ text để tính toán chi phí và giới hạn API
        
        Công thức ước tính:
        - 1 token ≈ 3-4 characters cho tiếng Anh
        - 1 token ≈ 2-3 characters cho tiếng Việt (do encoding khác nhau)
        
        Args:
            text (str): Text cần ước tính số tokens
            
        Returns:
            int: Số tokens ước tính (chia cho 3 để an toàn)
        """
        # Công thức ước tính đơn giản: độ dài text chia 3
        # Điều này giúp ước tính chi phí và không vượt quá giới hạn API
        return len(text) // 3
    
    def _calculate_max_tokens(self, estimated_input_tokens, is_quick_action=False):
        """
        Tính toán max_tokens phù hợp để tối ưu chi phí và chất lượng output
        
        Args:
            estimated_input_tokens (int): Số tokens của input prompt
            is_quick_action (bool): True nếu là quick action (cần ít tokens hơn)
            
        Returns:
            int: max_tokens được tính toán động
        """
        if is_quick_action:
            # Quick actions: Ít tokens hơn vì chỉ cần code output
            max_tokens = min(3000, max(800, estimated_input_tokens))
        else:
            # Normal chat: Nhiều tokens hơn cho giải thích chi tiết
            max_tokens = min(4000, max(500, estimated_input_tokens))
        
        return max_tokens
    
    def _get_chat_functions(self):
        """
        Định nghĩa các functions mà AI có thể gọi để xử lý tác vụ chuyên biệt
        
        Returns:
            list: Danh sách function definitions cho OpenAI function calling
        """
        return [
            {
                "name": "comment_code",
                "description": "Add detailed comments to source code",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Source code to add comments to"
                        },
                        "language": {
                            "type": "string", 
                            "description": "Programming language of the code"
                        }
                    },
                    "required": ["code", "language"]
                }
            },
            {
                "name": "fix_bugs",
                "description": "Analyze code to find potential bugs and provide fixes",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Source code to analyze for bugs"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language of the code"
                        }
                    },
                    "required": ["code", "language"]
                }
            },
            {
                "name": "optimize_code",
                "description": "Optimize code for better performance and readability",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Source code to optimize"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language of the code"
                        }
                    },
                    "required": ["code", "language"]
                }
            },
            {
                "name": "generate_unit_tests",
                "description": "Generate unit tests for the provided code",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Source code to generate tests for"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language of the code"
                        }
                    },
                    "required": ["code", "language"]
                }
            },
            {
                "name": "explain_code",
                "description": "Explain how the code works and what it does",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Source code to explain"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language of the code"
                        }
                    },
                    "required": ["code", "language"]
                }
            }
        ]
    
    def chat_with_ai(self, message, history=None, is_quick_action=False):
        """
        Giao tiếp với AI Assistant thông qua Azure OpenAI
        
        Args:
            message (str): Tin nhắn từ user
            history (list): Lịch sử chat để maintain context
            is_quick_action (bool): True nếu là quick action
            
        Returns:
            dict: Response từ AI hoặc error message
        """
        if not self.client:
            return {
                "success": False,
                "error": "AI service not available"
            }
        
        try:
            # Bước 1: Tạo context messages dựa trên loại request
            context_messages = []
            
            # Chọn system message phù hợp với từng mode
            if is_quick_action:
                # System message cho quick actions - chỉ trả về code thuần túy
                context_messages.append({
                    "role": "system",
                    "content": """Bạn là một AI Assistant chuyên về lập trình. Khi nhận được yêu cầu từ Quick Action:

QUAN TRỌNG: CHỈ TRẢ VỀ CODE ĐÃ XỬ LÝ, KHÔNG GIẢI THÍCH THÊM!

Quy tắc xử lý:
- Comment Code: Thêm comment chi tiết vào code bằng tiếng Việt, trả về code đã comment
- Find Bugs: Sửa lỗi trong code, trả về code đã sửa  
- Optimize: Tối ưu code, trả về code đã tối ưu
- Generate Tests: Tạo unit tests, trả về code tests

Format trả về:
- KHÔNG bao gồm markdown (```language)
- KHÔNG giải thích hay mô tả
- CHỈ code thuần túy đã xử lý
- Giữ nguyên cấu trúc và format của code gốc
- Comment sử dụng format chuẩn của ngôn ngữ (// cho Java/JS, # cho Python, /* */ cho block comment)

Ví dụ Input: "Hãy thêm comment chi tiết vào code này: [code]"
Ví dụ Output: [code đã được comment, không có gì khác]"""
                })
            else:
                # System message cho chat thường - trả lời đầy đủ với giải thích
                context_messages.append({
                    "role": "system",
                    "content": """Bạn là một AI Assistant thông minh và hữu ích, chuyên về lập trình và công nghệ. 
                    
Nhiệm vụ của bạn:
- Trả lời câu hỏi về lập trình, debug code, giải thích thuật toán
- Hỗ trợ viết code, tối ưu hóa và review code  
- TỰ ĐỘNG COMMENT CODE khi người dùng gửi code block
- Giải thích các khái niệm công nghệ một cách dễ hiểu
- Hướng dẫn best practices trong lập trình
- Trả lời các câu hỏi tổng quát khác

QUAN TRỌNG - ĐỊNH DẠNG RESPONSE:
- SỬ DỤNG markdown code blocks để bao code: ```language
- Luôn specify language cho code blocks (```python, ```java, ```javascript, etc.)
- Text giải thích sử dụng format thuần túy
- Code blocks giúp frontend có thể parse và highlight syntax

Đặc biệt quan trọng - KHI COMMENT CODE:
- Phân tích code và thêm comment tiếng Việt chi tiết
- Giải thích mục đích của từng function/method
- Thêm comment cho các logic phức tạp
- Sử dụng format comment chuẩn của ngôn ngữ (/** */ cho Java, # cho Python, // cho JS...)
- Trả về code đã được comment hoàn chỉnh trong markdown code block với language

Phong cách trả lời:
- Thân thiện, nhiệt tình và chuyên nghiệp
- Giải thích rõ ràng, có ví dụ cụ thể
- Sử dụng emoji phù hợp để tạo không khí vui vẻ
- Trả lời bằng tiếng Việt (trừ khi được yêu cầu khác)
- Khi giải thích code, sử dụng markdown code blocks với syntax highlighting

Khi người dùng chia sẻ code:
- Phân tích và giải thích từng phần
- TỰ ĐỘNG thêm comment vào code
- Chỉ ra điểm mạnh và có thể cải thiện
- Đưa ra gợi ý tối ưu nếu cần
- Format code đúng chuẩn với ```language```

Ví dụ format:
Đây là code Python đã được comment:

```python
# Hàm tính tổng hai số
def add_numbers(a, b):
    return a + b
```

Code này thực hiện phép cộng đơn giản."""
                })

            # Bước 2: Thêm lịch sử chat để maintain context (chỉ cho normal chat)
            if not is_quick_action and history:
                recent_history = history[-5:] if len(history) > 5 else history  # Chỉ lấy 5 tin nhắn gần nhất
                for msg in recent_history:
                    if msg.get('type') == 'user':
                        context_messages.append({
                            "role": "user", 
                            "content": msg.get('content', '')
                        })
                    elif msg.get('type') == 'bot':
                        context_messages.append({
                            "role": "assistant", 
                            "content": msg.get('content', '')
                        })
            
            # Thêm tin nhắn hiện tại vào context
            context_messages.append({
                "role": "user",
                "content": message
            })
            
            # Bước 3: Tính toán tokens và parameters
            total_input = ' '.join([msg['content'] for msg in context_messages])
            estimated_input_tokens = self._estimate_tokens(total_input)
            max_tokens = self._calculate_max_tokens(estimated_input_tokens, is_quick_action)
            
            # Điều chỉnh temperature dựa trên loại request
            temperature = 0.1 if is_quick_action else 0.7
            
            # Bước 4: Gọi Azure OpenAI với function calling capability
            # Function calling cho phép AI tự động gọi các function đã định nghĩa để xử lý tác vụ chuyên biệt
            chat_functions = self._get_chat_functions()  # Lấy danh sách các function AI có thể gọi
            
            # Gọi OpenAI API với function calling enabled
            # AI sẽ phân tích request và tự quyết định có cần gọi function hay không
            response = self.client.chat.completions.create(
                model=self.deployment_name,           # GPT-4o-mini deployment model
                messages=context_messages,            # Context messages đã build với system prompt và history
                max_tokens=max_tokens,                # Max tokens đã tính toán động dựa trên input
                temperature=temperature,              # 0.1 cho code (consistent), 0.7 cho chat (creative)
                top_p=0.9,                            # Nucleus sampling để balance quality vs creativity
                functions=chat_functions,             # Danh sách functions AI có thể gọi (comment, debug, optimize, test, explain)
                function_call="auto"                  # "auto": AI tự quyết định, "none": không gọi function, {"name": "func"}: force gọi function cụ thể
            )
            
            # Bước 5: Xử lý response - kiểm tra AI có gọi function hay không
            response_message = response.choices[0].message
            
            # Kiểm tra xem AI có muốn gọi function không
            if response_message.function_call:
                # === FUNCTION CALLING WORKFLOW ===
                # AI đã quyết định gọi một function để xử lý request
                function_name = response_message.function_call.name        # Tên function AI muốn gọi
                function_args = response_message.function_call.arguments   # Arguments cho function (JSON string)
                
                try:
                    # Parse arguments từ JSON string thành dict
                    args = json.loads(function_args)
                    
                    # Tạo function result message dựa trên function được gọi
                    # Đây là simulation của function execution (thực tế không execute function thật)
                    # Chúng ta chỉ cần cho AI biết function đã "execute thành công"
                    if function_name == "comment_code":
                        function_result = f"Code commented successfully for {args.get('language', 'unknown')} language"
                    elif function_name == "fix_bugs":
                        function_result = f"Bug analysis completed for {args.get('language', 'unknown')} code"
                    elif function_name == "optimize_code":
                        function_result = f"Code optimization completed for {args.get('language', 'unknown')} language"
                    elif function_name == "generate_unit_tests":
                        function_result = f"Unit tests generated for {args.get('language', 'unknown')} code"
                    elif function_name == "explain_code":
                        function_result = f"Code explanation provided for {args.get('language', 'unknown')} code"
                    else:
                        function_result = f"Function {function_name} executed successfully"
                    
                    # === SECOND API CALL ===
                    # Gọi AI lần thứ 2 với function result để AI generate final response
                    # Đây là pattern chuẩn của OpenAI function calling: gọi 2 lần
                    # Lần 1: AI quyết định gọi function
                    # Lần 2: AI nhận function result và generate final response
                    final_response = self.client.chat.completions.create(
                        model=self.deployment_name,
                        messages=context_messages + [
                            # Thêm function call message của AI
                            {"role": "assistant", "content": None, "function_call": response_message.function_call},
                            # Thêm function result message
                            {"role": "function", "name": function_name, "content": function_result}
                        ],
                        max_tokens=max_tokens,
                        temperature=temperature,
                        top_p=0.9
                    )
                    ai_response = final_response.choices[0].message.content.strip()
                    
                except json.JSONDecodeError:
                    ai_response = "Error processing function call"
            else:
                # === NORMAL RESPONSE ===
                # AI không gọi function, trả về response bình thường
                ai_response = response_message.content.strip()
            
            # Bước 6: Clean up response để loại bỏ markdown formatting cho quick actions only
            if is_quick_action:
                # Remove markdown formatting nếu có cho quick actions
                for lang in ["java", "python", "javascript", "typescript", "cpp", "c", "csharp", "go", "rust"]:
                    if ai_response.startswith(f"```{lang}"):
                        ai_response = ai_response.replace(f"```{lang}", "").replace("```", "").strip()
                        break
                
                if ai_response.startswith("```"):
                    ai_response = ai_response.replace("```", "").strip()
            # For normal chat, keep markdown formatting để frontend có thể parse
            
            # Ước tính output tokens để tính cost
            estimated_output_tokens = self._estimate_tokens(ai_response)
            
            return {
                "success": True,
                "response": ai_response,
                "tokens_info": {
                    "estimated_input_tokens": estimated_input_tokens,
                    "max_tokens_used": max_tokens,
                    "estimated_output_tokens": estimated_output_tokens
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing chat: {str(e)}"
            }

    # =========================================
    # END OF AI SERVICE - ONLY SINGLE CHAT SUPPORT
    # =========================================
