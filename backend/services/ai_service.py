"""
AI Service - Service chính để giao tiếp với Langchain

Class này chứa:
- Integration với LangchainService để xử lý RAG và workflows phức tạp
- Fallback operations cho các tác vụ cơ bản
- Legacy function calling support (deprecated)
"""

import os
from dotenv import load_dotenv
import json
from typing import List, Dict, Any, Optional

# Load environment variables
load_dotenv()

class AIService:
    """
    Service class tích hợp với Langchain để xử lý AI operations
    
    Chức năng chính:
    - Delegation cho LangchainService để xử lý các tác vụ phức tạp
    - RAG operations với knowledge base
    - Agent-based workflows
    - Backward compatibility với legacy function calls
    """
    
    def __init__(self, langchain_service=None):
        """
        Khởi tạo AI Service với Langchain integration
        
        Args:
            langchain_service: Instance của LangchainService
        """
        self.langchain_service = langchain_service
        
        # Khởi tạo legacy Azure OpenAI client cho backward compatibility
        self._init_legacy_client()
    
    def _init_legacy_client(self):
        """
        Khởi tạo legacy Azure OpenAI client cho fallback operations
        """
        try:
            from openai import AzureOpenAI
            
            self.client = AzureOpenAI(
                api_version="2024-07-01-preview",
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            )
            self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "GPT-4o-mini")
            print("✅ Legacy Azure OpenAI client initialized for fallback")
            
        except Exception as e:
            print(f"⚠️ Legacy client initialization failed: {e}")
            self.client = None
    
    def _estimate_tokens(self, text):
        """
        Ước tính số tokens (legacy method)
        """
        return len(text) // 3
    
    def _calculate_max_tokens(self, estimated_input_tokens, is_quick_action=False):
        """
        Tính toán max_tokens (legacy method)
        """
        if is_quick_action:
            max_tokens = min(3000, max(800, estimated_input_tokens))
        else:
            max_tokens = min(4000, max(500, estimated_input_tokens))
        return max_tokens
    
    def _get_chat_functions(self):
        """
        Legacy function definitions (deprecated - được thay thế bởi Langchain Tools)
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
    
    def chat_with_ai(self, message: str, history: Optional[List] = None, is_quick_action: bool = False, session_id: str = None, display_language: str = 'en', programming_language: str = 'javascript') -> Dict[str, Any]:
        """
        Chat với AI sử dụng Langchain hoặc fallback to legacy với session support
        
        Args:
            message: Tin nhắn từ user
            history: Lịch sử chat để maintain context
            is_quick_action: True nếu là quick action
            session_id: Session ID để maintain memory
            display_language: Ngôn ngữ hiển thị ('en' hoặc 'vi')
            programming_language: Ngôn ngữ lập trình (javascript, python, java, ...)
            
        Returns:
            dict: Response từ AI hoặc error message
        """
        # Nếu có Langchain service, ưu tiên sử dụng
        if self.langchain_service:
            return self._chat_with_langchain(message, history, is_quick_action, session_id, display_language, programming_language)
        
        # Fallback to legacy implementation
        return self._chat_with_legacy(message, history, is_quick_action, display_language)
    
    def _chat_with_langchain(self, message: str, history: Optional[List] = None, is_quick_action: bool = False, session_id: str = None, display_language: str = 'en', programming_language: str = 'javascript') -> Dict[str, Any]:
        """
        Chat sử dụng Langchain service với session support
        """
        try:
            if is_quick_action:
                # Xử lý quick actions với Langchain tools
                result = self.langchain_service.process_code_with_langchain(
                    task=self._extract_task_from_message(message),
                    code=self._extract_code_from_message(message),
                    language=programming_language,  # Sử dụng programming language
                    system_language=display_language  # Ngôn ngữ hiển thị
                )
                
                if result["success"]:
                    return {
                        "success": True,
                        "response": result["result"],
                        "tokens_info": {"source": "langchain"},
                        "session_id": session_id
                    }
                else:
                    # Fallback to legacy if Langchain fails
                    return self._chat_with_legacy(message, history, is_quick_action, display_language)
            
            else:
                # Normal chat với RAG capabilities và session memory
                result = self.langchain_service.chat_with_rag(
                    question=message, 
                    chat_history=history,
                    session_id=session_id,
                    system_language=display_language  # Ngôn ngữ hiển thị
                )
                
                if result["success"]:
                    return {
                        "success": True,
                        "response": result["answer"],
                        "source_documents": result.get("source_documents", []),
                        "tokens_info": {"source": "langchain_rag"},
                        "session_id": result.get("session_id"),
                        "search_context": result.get("search_context", {})
                    }
                else:
                    # Fallback to legacy
                    return self._chat_with_legacy(message, history, is_quick_action, display_language)
                    
        except Exception as e:
            print(f"⚠️ Langchain chat failed: {str(e)}, falling back to legacy")
            return self._chat_with_legacy(message, history, is_quick_action, display_language)
    
    def _extract_task_from_message(self, message: str) -> str:
        """Extract task type from message"""
        message_lower = message.lower()
        if "comment" in message_lower or "chú thích" in message_lower:
            return "comment_code"
        elif "bug" in message_lower or "lỗi" in message_lower:
            return "fix_bugs"
        elif "optimize" in message_lower or "tối ưu" in message_lower:
            return "optimize_code"
        elif "test" in message_lower or "kiểm tra" in message_lower:
            return "generate_unit_tests"
        else:
            return "explain_code"
    
    def _extract_code_from_message(self, message: str) -> str:
        """Extract code from message"""
        # Simple extraction - có thể cải thiện
        lines = message.split('\n')
        code_lines = []
        for line in lines:
            if any(keyword in line.lower() for keyword in ['class', 'function', 'def', 'public', 'private', 'int', 'string']):
                code_lines.append(line)
        return '\n'.join(code_lines) if code_lines else message
    
    def _detect_language_from_message(self, message: str) -> str:
        """Detect programming language from message"""
        message_lower = message.lower()
        if 'java' in message_lower:
            return 'java'
        elif 'python' in message_lower:
            return 'python'
        elif 'javascript' in message_lower or 'js' in message_lower:
            return 'javascript'
        else:
            return 'unknown'
    def _chat_with_legacy(self, message: str, history: Optional[List] = None, is_quick_action: bool = False, display_language: str = 'en') -> Dict[str, Any]:
        """
        Legacy chat implementation (deprecated, dùng cho fallback)
        """
        if not self.client:
            return {
                "success": False,
                "error": "AI service not available"
            }
        
        try:
            # Bước 1: Tạo context messages dựa trên loại request
            context_messages = []
            
            # Chọn system message phù hợp với từng mode và ngôn ngữ
            if is_quick_action:
                # System message cho quick actions - chỉ trả về code thuần túy
                if display_language == 'vi':
                    system_content = """Bạn là một AI Assistant chuyên về lập trình. Khi nhận được yêu cầu từ Quick Action:

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
                else:
                    system_content = """You are a programming AI Assistant. When receiving Quick Action requests:

IMPORTANT: ONLY RETURN PROCESSED CODE, NO ADDITIONAL EXPLANATIONS!

Processing rules:
- Comment Code: Add detailed comments to code in English, return commented code
- Find Bugs: Fix bugs in code, return fixed code  
- Optimize: Optimize code, return optimized code
- Generate Tests: Create unit tests, return test code

Return format:
- DO NOT include markdown (```language)
- DO NOT explain or describe
- ONLY pure processed code
- Keep original code structure and format
- Comments using standard format for language (// for Java/JS, # for Python, /* */ for block comments)

Example Input: "Please add detailed comments to this code: [code]"
Example Output: [commented code, nothing else]"""
                
                context_messages.append({
                    "role": "system",
                    "content": system_content
                })
            else:
                # System message cho chat thường - trả lời đầy đủ với giải thích
                if display_language == 'vi':
                    system_content = """Bạn là một AI Assistant thông minh và hữu ích, chuyên về lập trình và công nghệ. 
                    
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
                else:
                    system_content = """You are an intelligent and helpful AI Assistant specializing in programming and technology.
                    
Your tasks:
- Answer programming questions, debug code, explain algorithms
- Help write code, optimize and review code
- AUTOMATICALLY COMMENT CODE when users send code blocks
- Explain technology concepts in an easy-to-understand way
- Guide best practices in programming
- Answer other general questions

IMPORTANT - RESPONSE FORMAT:
- USE markdown code blocks to wrap code: ```language
- Always specify language for code blocks (```python, ```java, ```javascript, etc.)
- Explanatory text uses plain format
- Code blocks help frontend parse and highlight syntax

Especially important - WHEN COMMENTING CODE:
- Analyze code and add detailed English comments
- Explain the purpose of each function/method
- Add comments for complex logic
- Use standard comment format for the language (/** */ for Java, # for Python, // for JS...)
- Return fully commented code in markdown code block with language

Response style:
- Friendly, enthusiastic and professional
- Clear explanations with specific examples
- Use appropriate emojis to create a pleasant atmosphere
- Respond in English (unless requested otherwise)
- When explaining code, use markdown code blocks with syntax highlighting

When users share code:
- Analyze and explain each part
- AUTOMATICALLY add comments to code
- Point out strengths and potential improvements
- Provide optimization suggestions if needed
- Format code properly with ```language```

Example format:
Here is the commented Python code:

```python
# Function to add two numbers
def add_numbers(a, b):
    return a + b
```

This code performs simple addition."""
                
                context_messages.append({
                    "role": "system",
                    "content": system_content
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
