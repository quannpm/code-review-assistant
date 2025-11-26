# AI Programming Assistant API v3.0.0

## 🏗️ Cấu trúc Modular Architecture

API đã được tái cấu trúc thành 3 modules chính:

### 📁 Cấu trúc Project

```
backend/
├── app_new.py              # Main application với modular structure
├── app_old.py              # Backup của version cũ
├── requirements.txt        # Dependencies
├── .env                   # Environment variables
├── config/                # 📋 Configuration modules
│   ├── __init__.py
│   └── swagger_config.py  # Swagger documentation config
├── services/              # 🔧 Business logic services  
│   ├── __init__.py
│   └── ai_service.py      # AI operations với Azure OpenAI
└── api/                   # 🚀 API endpoint modules
    ├── __init__.py
    ├── chat.py            # 🤖 Chat với AI Assistant
    ├── language.py        # 🌐 Language support operations
    └── health.py          # 💚 Health monitoring endpoints
```

### 🌟 API Endpoints

#### 🤖 Chat API (`/api/chat`)
- **POST** `/api/chat` - Chat với AI Assistant (single request)
  - Normal chat: Trả lời đầy đủ với giải thích
  - Quick actions: Chỉ trả code đã xử lý (comment, debug, optimize, test)
  - Function calling integration
  - Context management với chat history

- **POST** `/api/chat/batch` - Chat với AI Assistant (batch requests)
  - Request batching for efficiency: Xử lý multiple requests đồng thời
  - Concurrent processing với ThreadPoolExecutor
  - Tối ưu hiệu suất và giảm latency
  - Aggregated results với batch statistics

- **POST** `/api/chat/batch/intelligent` - Chat với AI Assistant (intelligent batching)
  - 🧠 **Intelligent Context Merging**: Gộp multiple questions thành 1 prompt
  - 💡 **Smart Response Parsing**: Tách response thành các câu trả lời riêng
  - ⚡ **Ultra Efficiency**: Tiết kiệm 60-80% API calls
  - 🎯 **Context Optimization**: Tận dụng context liên quan giữa các câu hỏi

- **GET** `/api/chat/queue/status` - Lấy trạng thái batch queue
  - Monitor queue size và batch processing status
  - Debugging và performance monitoring

#### 🌐 Language API (`/api/languages`)
- **GET** `/api/languages` - Lấy danh sách ngôn ngữ được hỗ trợ
- **GET** `/api/languages/{language_code}` - Thông tin chi tiết về ngôn ngữ

#### 💚 Health API (`/api/health`)
- **GET** `/api/health` - Basic health check
- **GET** `/api/health/detailed` - Detailed health status
- **GET** `/api/health/version` - Version và changelog information

### 🚀 Cách chạy

1. **Setup Environment**:
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env  # Và điền thông tin Azure OpenAI
   ```

2. **Chạy API**:
   ```bash
   python app_new.py
   ```

3. **Access Documentation**:
   - Swagger UI: http://localhost:8888/swagger/
   - API Base: http://localhost:8888/api/

### 📋 Environment Variables

Cần thiết trong file `.env`:

```env
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_DEPLOYMENT_NAME=GPT-4o-mini
```

### 🔄 Thay đổi từ v2.0.0

#### ❌ Removed:
- **Comment API** (`/api/comment-code`) - Đã tích hợp vào Chat API
- **Supported Languages endpoint** cũ - Thay thế bằng Language API mới

#### ✅ Added:
- **Modular architecture** với separation of concerns
- **Enhanced Language API** với detailed information
- **Comprehensive Health monitoring** 
- **Better error handling** và logging
- **Function calling** integration trong Chat API
- **Request batching** for efficiency và concurrent processing

#### 🚀 Enhanced:
- **Chat API** giờ handle cả commenting, debugging, optimization
- **Batch processing** để xử lý multiple requests đồng thời
- **Swagger documentation** với đường dẫn endpoints chi tiết
- **Dependency injection** pattern cho services

### 📊 API Examples

#### Chat với AI:
```bash
curl -X POST http://localhost:8888/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Giải thích đoạn code này: def hello(): print(\"Hello\")",
    "is_quick_action": false
  }'
```

#### Batch Chat - Multiple requests:
```bash
curl -X POST http://localhost:8888/api/chat/batch \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "id": "req_001",
        "message": "Comment code này: def greet(): return \"Hi\"",
        "is_quick_action": true
      },
      {
        "id": "req_002",
        "message": "Giải thích bubble sort algorithm",
        "is_quick_action": false
      }
    ]
  }'
```

#### Intelligent Batch Chat - Gộp nhiều câu hỏi:
```bash
curl -X POST http://localhost:8888/api/chat/batch/intelligent \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "id": "q1",
        "message": "Giải thích bubble sort",
        "is_quick_action": false
      },
      {
        "id": "q2",
        "message": "Ví dụ code bubble sort",
        "is_quick_action": false
      },
      {
        "id": "q3", 
        "message": "Độ phức tạp của bubble sort",
        "is_quick_action": false
      }
    ]
  }'
```

**⚡ Thay vì 3 API calls → CHỈ 1 API call! Tiết kiệm 66% chi phí**

#### Lấy danh sách ngôn ngữ:
```bash
curl http://localhost:8888/api/languages
```

#### Health check:
```bash
curl http://localhost:8888/api/health/detailed
```

### 🔧 Development Notes

- **Blueprint pattern** để organize routes
- **Factory pattern** cho app creation
- **Dependency injection** cho services
- **Error handling** với custom error pages
- **CORS enabled** cho frontend integration
- **Swagger integration** cho API documentation

### 🎯 Future Enhancements

- [ ] Authentication & Authorization
- [ ] Rate limiting
- [ ] Caching layer
- [ ] Database integration
- [ ] Metrics & Analytics
- [ ] Docker containerization
- [ ] CI/CD pipeline
