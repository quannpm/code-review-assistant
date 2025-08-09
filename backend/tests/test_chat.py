"""
Test cases cho Chat API - Kiểm thử tất cả chức năng chat với AI Assistant

Test suite này bao gồm:
- Unit tests cho chat endpoint
- Integration tests với AI service
- Mock tests cho Azure OpenAI
- Validation tests cho input/output
- Error handling tests
"""

import unittest
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add backend directory to path để import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from services.ai_service import AIService

class TestChatAPI(unittest.TestCase):
    """Test cases cho Chat API endpoint"""
    
    def setUp(self):
        """Setup test environment trước mỗi test case"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Mock AI service để tránh gọi thật Azure OpenAI
        self.mock_ai_service = Mock(spec=AIService)
        
    def test_chat_success_normal_message(self):
        """Test chat thành công với tin nhắn thông thường"""
        # Setup mock response
        self.mock_ai_service.chat_with_ai.return_value = {
            "success": True,
            "response": "Hello! I can help you with programming questions."
        }
        
        # Patch AI service trong ứng dụng
        with patch('api.chat._ai_service', self.mock_ai_service):
            response = self.client.post('/api/chat', 
                json={
                    'message': 'Hello, can you help me?',
                    'history': [],
                    'is_quick_action': False
                },
                content_type='application/json'
            )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('response', data)
        
        # Verify AI service được gọi với đúng parameters
        self.mock_ai_service.chat_with_ai.assert_called_once_with(
            message='Hello, can you help me?',
            history=[],
            is_quick_action=False
        )
    
    def test_chat_success_quick_action(self):
        """Test chat thành công với quick action"""
        # Setup mock response cho quick action
        self.mock_ai_service.chat_with_ai.return_value = {
            "success": True,
            "response": "// This function calculates the sum of two numbers\nfunction add(a, b) {\n    return a + b;\n}"
        }
        
        with patch('api.chat._ai_service', self.mock_ai_service):
            response = self.client.post('/api/chat',
                json={
                    'message': 'function add(a, b) { return a + b; }',
                    'history': [],
                    'is_quick_action': True
                },
                content_type='application/json'
            )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('response', data)
        
        # Verify quick action flag được truyền đúng
        self.mock_ai_service.chat_with_ai.assert_called_once_with(
            message='function add(a, b) { return a + b; }',
            history=[],
            is_quick_action=True
        )
    
    def test_chat_with_conversation_history(self):
        """Test chat với lịch sử hội thoại"""
        # Setup mock response
        self.mock_ai_service.chat_with_ai.return_value = {
            "success": True,
            "response": "Based on our previous conversation about JavaScript, here's more info..."
        }
        
        conversation_history = [
            {"type": "user", "content": "Tell me about JavaScript"},
            {"type": "bot", "content": "JavaScript is a programming language..."},
            {"type": "user", "content": "What about functions?"}
        ]
        
        with patch('api.chat._ai_service', self.mock_ai_service):
            response = self.client.post('/api/chat',
                json={
                    'message': 'Can you give me more examples?',
                    'history': conversation_history,
                    'is_quick_action': False
                },
                content_type='application/json'
            )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # Verify history được truyền đúng
        self.mock_ai_service.chat_with_ai.assert_called_once_with(
            message='Can you give me more examples?',
            history=conversation_history,
            is_quick_action=False
        )
    
    def test_chat_missing_message(self):
        """Test lỗi khi không có message"""
        response = self.client.post('/api/chat',
            json={},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Message is required')
    
    def test_chat_empty_message(self):
        """Test lỗi khi message rỗng"""
        response = self.client.post('/api/chat',
            json={'message': '   '},  # Chỉ có spaces
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Message cannot be empty')
    
    def test_chat_invalid_json(self):
        """Test lỗi khi JSON không hợp lệ"""
        response = self.client.post('/api/chat',
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_chat_ai_service_error(self):
        """Test xử lý lỗi từ AI service"""
        # Setup mock để trả về lỗi
        self.mock_ai_service.chat_with_ai.return_value = {
            "success": False,
            "error": "Azure OpenAI API error"
        }
        
        with patch('api.chat._ai_service', self.mock_ai_service):
            response = self.client.post('/api/chat',
                json={
                    'message': 'Hello',
                    'history': [],
                    'is_quick_action': False
                },
                content_type='application/json'
            )
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
    
    def test_chat_ai_service_exception(self):
        """Test xử lý exception từ AI service"""
        # Setup mock để raise exception
        self.mock_ai_service.chat_with_ai.side_effect = Exception("Connection timeout")
        
        with patch('api.chat._ai_service', self.mock_ai_service):
            response = self.client.post('/api/chat',
                json={
                    'message': 'Hello',
                    'history': [],
                    'is_quick_action': False
                },
                content_type='application/json'
            )
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('Error processing chat', data['error'])


class TestAIServiceChat(unittest.TestCase):
    """Test cases cho AI Service chat functionality"""
    
    def setUp(self):
        """Setup test environment"""
        # Mock Azure OpenAI client
        self.mock_client = Mock()
        self.ai_service = AIService()
        self.ai_service.client = self.mock_client
        self.ai_service.deployment_name = "gpt-4o-mini"
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_OPENAI_API_KEY': 'test-key',
        'AZURE_OPENAI_DEPLOYMENT_NAME': 'gpt-4o-mini'
    })
    def test_chat_with_ai_normal_conversation(self):
        """Test chat thông thường với AI"""
        # Setup mock response từ Azure OpenAI
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hello! I can help you with programming."
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Test normal conversation
        result = self.ai_service.chat_with_ai(
            message="Hello, can you help me with Python?",
            history=[],
            is_quick_action=False
        )
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertEqual(result['response'], "Hello! I can help you with programming.")
        
        # Verify Azure OpenAI được gọi với đúng parameters
        self.mock_client.chat.completions.create.assert_called_once()
        call_args = self.mock_client.chat.completions.create.call_args
        self.assertEqual(call_args[1]['model'], 'gpt-4o-mini')
        self.assertIn('messages', call_args[1])
    
    def test_chat_with_ai_quick_action_comment(self):
        """Test quick action để thêm comments"""
        # Setup mock response cho comment action
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "// This function adds two numbers\nfunction add(a, b) {\n    return a + b;\n}"
        self.mock_client.chat.completions.create.return_value = mock_response
        
        result = self.ai_service.chat_with_ai(
            message="function add(a, b) { return a + b; }",
            history=[],
            is_quick_action=True
        )
        
        self.assertTrue(result['success'])
        self.assertIn('// This function adds two numbers', result['response'])
    
    def test_chat_with_ai_conversation_history(self):
        """Test chat với conversation history"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Based on our previous discussion about Python..."
        self.mock_client.chat.completions.create.return_value = mock_response
        
        history = [
            {"type": "user", "content": "What is Python?"},
            {"type": "bot", "content": "Python is a programming language..."}
        ]
        
        result = self.ai_service.chat_with_ai(
            message="Tell me more about Python functions",
            history=history,
            is_quick_action=False
        )
        
        self.assertTrue(result['success'])
        self.assertIn('Based on our previous discussion', result['response'])
        
        # Verify history được include trong messages
        call_args = self.mock_client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        self.assertGreater(len(messages), 1)  # Có history + current message
    
    def test_chat_with_ai_azure_openai_error(self):
        """Test xử lý lỗi từ Azure OpenAI"""
        # Setup mock để raise exception
        self.mock_client.chat.completions.create.side_effect = Exception("API rate limit exceeded")
        
        result = self.ai_service.chat_with_ai(
            message="Hello",
            history=[],
            is_quick_action=False
        )
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('API rate limit exceeded', result['error'])


class TestChatValidation(unittest.TestCase):
    """Test cases cho validation logic"""
    
    def test_valid_message_formats(self):
        """Test các format message hợp lệ"""
        valid_messages = [
            "Hello world",
            "function test() { return true; }",
            "What is the difference between let and var in JavaScript?",
            "```python\nprint('hello')\n```",
            "🎉 Can you help me with this code?",
            "Multi\nline\nmessage"
        ]
        
        app = create_app()
        app.config['TESTING'] = True
        client = app.test_client()
        
        mock_ai_service = Mock()
        mock_ai_service.chat_with_ai.return_value = {"success": True, "response": "OK"}
        
        for message in valid_messages:
            with patch('api.chat._ai_service', mock_ai_service):
                response = client.post('/api/chat',
                    json={'message': message},
                    content_type='application/json'
                )
            self.assertEqual(response.status_code, 200, f"Failed for message: {message}")
    
    def test_invalid_message_formats(self):
        """Test các format message không hợp lệ"""
        invalid_messages = [
            "",          # Empty string
            "   ",       # Only spaces
            "\n\n\n",    # Only newlines
            "\t\t",      # Only tabs
        ]
        
        app = create_app()
        app.config['TESTING'] = True
        client = app.test_client()
        
        for message in invalid_messages:
            response = client.post('/api/chat',
                json={'message': message},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400, f"Should fail for message: '{message}'")
    
    def test_history_validation(self):
        """Test validation cho conversation history"""
        app = create_app()
        app.config['TESTING'] = True
        client = app.test_client()
        
        mock_ai_service = Mock()
        mock_ai_service.chat_with_ai.return_value = {"success": True, "response": "OK"}
        
        # Valid history formats
        valid_histories = [
            [],  # Empty history
            [{"type": "user", "content": "Hello"}],
            [
                {"type": "user", "content": "What is Python?"},
                {"type": "bot", "content": "Python is a programming language"}
            ]
        ]
        
        for history in valid_histories:
            with patch('api.chat._ai_service', mock_ai_service):
                response = client.post('/api/chat',
                    json={
                        'message': 'Test message',
                        'history': history
                    },
                    content_type='application/json'
                )
            self.assertEqual(response.status_code, 200)
    
    def test_java_hello_world_explanation(self):
        """Test giải thích code Java Hello World"""
        app = create_app()
        app.config['TESTING'] = True
        client = app.test_client()
        
        # Đoạn code Java Hello World
        java_code = """
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
"""
        
        # Mock response từ AI về giải thích code Java
        mock_ai_service = Mock()
        mock_ai_service.chat_with_ai.return_value = {
            "success": True,
            "response": """
Đây là chương trình Java cơ bản "Hello World". Giải thích từng phần:

1. **public class HelloWorld**: Khai báo một class public tên HelloWorld
2. **public static void main(String[] args)**: Method main - điểm bắt đầu chương trình
   - public: có thể truy cập từ bên ngoài
   - static: có thể gọi mà không cần tạo object
   - void: không trả về giá trị
   - String[] args: tham số command line
3. **System.out.println("Hello, World!")**: In ra màn hình dòng chữ "Hello, World!"

Chương trình này sẽ xuất ra: Hello, World!
"""
        }
        
        with patch('api.chat._ai_service', mock_ai_service):
            response = client.post('/api/chat',
                json={
                    'message': f'Hãy giải thích đoạn code Java này:\n{java_code}',
                    'history': [],
                    'is_quick_action': False
                },
                content_type='application/json'
            )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('response', data)
        
        # Verify AI service được gọi với đúng parameters
        mock_ai_service.chat_with_ai.assert_called_once()
        call_args = mock_ai_service.chat_with_ai.call_args
        
        # Verify message chứa code Java
        self.assertIn('public class HelloWorld', call_args[0][0])  # message parameter
        self.assertIn('System.out.println', call_args[0][0])
        self.assertIn('Hãy giải thích', call_args[0][0])
        
        # Verify không phải quick action
        self.assertEqual(call_args[1]['is_quick_action'], False)
        
        # Verify response chứa giải thích
        response_text = data['response']
        self.assertIn('Hello World', response_text)
        self.assertIn('public class', response_text)
        self.assertIn('main', response_text)
        self.assertIn('System.out.println', response_text)
    
    def test_java_code_quick_action_comment(self):
        """Test quick action thêm comment cho code Java"""
        app = create_app()
        app.config['TESTING'] = True
        client = app.test_client()
        
        # Đoạn code Java không có comment
        java_code = """
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
    
    public int multiply(int x, int y) {
        return x * y;
    }
}
"""
        
        # Mock response với code Java đã được thêm comment
        mock_ai_service = Mock()
        mock_ai_service.chat_with_ai.return_value = {
            "success": True,
            "response": """
/**
 * Calculator class provides basic arithmetic operations
 */
public class Calculator {
    
    /**
     * Adds two integers and returns the result
     * @param a first integer
     * @param b second integer  
     * @return sum of a and b
     */
    public int add(int a, int b) {
        return a + b;
    }
    
    /**
     * Multiplies two integers and returns the result
     * @param x first integer
     * @param y second integer
     * @return product of x and y
     */
    public int multiply(int x, int y) {
        return x * y;
    }
}
"""
        }
        
        with patch('api.chat._ai_service', mock_ai_service):
            response = client.post('/api/chat',
                json={
                    'message': java_code,
                    'history': [],
                    'is_quick_action': True  # Quick action để thêm comment
                },
                content_type='application/json'
            )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # Verify AI service được gọi với quick action
        mock_ai_service.chat_with_ai.assert_called_once()
        call_args = mock_ai_service.chat_with_ai.call_args
        self.assertEqual(call_args[1]['is_quick_action'], True)
        
        # Verify response chứa comments
        response_text = data['response']
        self.assertIn('/**', response_text)  # Javadoc comment
        self.assertIn('@param', response_text)
        self.assertIn('@return', response_text)
        self.assertIn('Calculator class', response_text)
    
    def test_java_code_different_formats(self):
        """Test xử lý code Java với các format khác nhau"""
        app = create_app()
        app.config['TESTING'] = True
        client = app.test_client()
        
        mock_ai_service = Mock()
        mock_ai_service.chat_with_ai.return_value = {"success": True, "response": "Code analyzed successfully"}
        
        # Test các format code Java khác nhau
        java_formats = [
            # Format 1: Code block với markdown
            """```java
public class Test {
    public static void main(String[] args) {
        System.out.println("Test");
    }
}
```""",
            
            # Format 2: Code thông thường
            """public class Test {
    public static void main(String[] args) {
        System.out.println("Test");
    }
}""",
            
            # Format 3: Single line
            'System.out.println("Hello World");',
            
            # Format 4: Method only
            """public void printMessage() {
    System.out.println("Hello");
}"""
        ]
        
        for i, java_code in enumerate(java_formats):
            with patch('api.chat._ai_service', mock_ai_service):
                response = client.post('/api/chat',
                    json={
                        'message': f'Explain this Java code: {java_code}',
                        'history': [],
                        'is_quick_action': False
                    },
                    content_type='application/json'
                )
            
            self.assertEqual(response.status_code, 200, f"Failed for Java format {i+1}")
            data = json.loads(response.data)
            self.assertTrue(data['success'], f"Failed for Java format {i+1}")


class TestChatPerformance(unittest.TestCase):
    """Test cases cho performance và optimization"""
    
    def test_large_message_handling(self):
        """Test xử lý tin nhắn lớn"""
        app = create_app()
        app.config['TESTING'] = True
        client = app.test_client()
        
        # Tạo message lớn (10KB)
        large_message = "x" * 10000
        
        mock_ai_service = Mock()
        mock_ai_service.chat_with_ai.return_value = {"success": True, "response": "Processed large message"}
        
        with patch('api.chat._ai_service', mock_ai_service):
            response = client.post('/api/chat',
                json={'message': large_message},
                content_type='application/json'
            )
        
        self.assertEqual(response.status_code, 200)
        mock_ai_service.chat_with_ai.assert_called_once()
    
    def test_long_conversation_history(self):
        """Test xử lý lịch sử hội thoại dài"""
        app = create_app()
        app.config['TESTING'] = True
        client = app.test_client()
        
        # Tạo lịch sử hội thoại dài (100 messages)
        long_history = []
        for i in range(100):
            long_history.append({"type": "user" if i % 2 == 0 else "bot", "content": f"Message {i}"})
        
        mock_ai_service = Mock()
        mock_ai_service.chat_with_ai.return_value = {"success": True, "response": "Processed long history"}
        
        with patch('api.chat._ai_service', mock_ai_service):
            response = client.post('/api/chat',
                json={
                    'message': 'Continue conversation',
                    'history': long_history
                },
                content_type='application/json'
            )
        
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    # Run tất cả test cases
    unittest.main(verbosity=2)
