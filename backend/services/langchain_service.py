"""
Langchain Service - Xử lý AI workflows với Langchain framework

Service này chứa:
- Langchain chains cho various AI tasks
- Vector store integration với ChromaDB
- Tools và agents cho complex workflows
- RAG (Retrieval Augmented Generation) capabilities
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Langchain imports
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType

# OpenAI imports
from openai import OpenAI

# Langchain OpenAI (cho compatibility)
from langchain_openai import ChatOpenAI

# Langchain ChromaDB
from langchain_chroma import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

# Load environment variables
load_dotenv()

class LangchainService:
    """
    Service class sử dụng Langchain framework để xử lý AI workflows
    
    Chức năng chính:
    - RAG (Retrieval Augmented Generation) với knowledge base
    - Conversation chains với memory
    - Agent-based workflows với tools
    - Vector store operations
    """
    
    def __init__(self, chroma_db_path='./chroma_db'):
        """
        Khởi tạo Langchain service với các components cần thiết
        
        Args:
            chroma_db_path: Đường dẫn đến ChromaDB
        """
        self.chroma_db_path = chroma_db_path
        
        # Khởi tạo Azure OpenAI LLM
        self._init_llm()
        
        # Khởi tạo embeddings
        self._init_embeddings()
        
        # Khởi tạo vector store
        self._init_vector_store()
        
        # Khởi tạo memory
        self._init_memory()
        
        # Khởi tạo chains và agents
        self._init_chains()
        self._init_tools()
        self._init_agent()
    
    def _init_llm(self):
        """Khởi tạo OpenAI client cho LiteLLM proxy"""
        try:
            # Initialize OpenAI client with custom base URL for LiteLLM proxy
            base_url = os.getenv("AZURE_OPENAI_ENDPOINT")
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            
            # Ensure base URL has /v1 endpoint for OpenAI compatibility
            if not base_url.endswith('/v1'):
                base_url = base_url.rstrip('/') + '/v1'
            
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            
            # Store deployment name for later use
            self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "GPT-4o-mini")
            
            print("✅ OpenAI client for LiteLLM proxy initialized successfully")
            print(f"🔧 Base URL: {base_url}")
            print(f"🔧 Model: {self.deployment_name}")
            print(f"🔧 API Key: {api_key[:10]}...")
            
            # Test connection
            try:
                models = self.client.models.list()
                print(f"✅ Connection test successful. Available models: {[model.id for model in models.data[:3]]}")
            except Exception as test_error:
                print(f"⚠️  Connection test failed: {test_error}")
            
            # Also create Langchain wrapper for compatibility
            try:
                self.llm = ChatOpenAI(
                    model=self.deployment_name,
                    openai_api_key=api_key,
                    openai_api_base=base_url,
                    temperature=0.7,
                    max_tokens=4000
                )
                print("✅ Langchain wrapper also initialized")
            except Exception as langchain_error:
                print(f"⚠️  Langchain wrapper failed (will use direct client): {langchain_error}")
                self.llm = None
                
        except Exception as e:
            print(f"❌ Error initializing OpenAI client: {e}")
            print(f"❌ Exception details: {type(e).__name__}: {str(e)}")
            self.client = None
            self.llm = None
    
    def _init_embeddings(self):
        """Khởi tạo embeddings model"""
        try:
            self.embeddings = SentenceTransformerEmbeddings(
                model_name="all-MiniLM-L6-v2"
            )
            print("✅ Embeddings model initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing embeddings: {e}")
            self.embeddings = None
    
    def _init_vector_store(self):
        """Khởi tạo ChromaDB vector store"""
        try:
            if self.embeddings:
                self.vector_store = Chroma(
                    persist_directory=self.chroma_db_path,
                    embedding_function=self.embeddings,
                    collection_name="knowledge_base"
                )
                print("✅ ChromaDB vector store initialized successfully")
            else:
                self.vector_store = None
        except Exception as e:
            print(f"❌ Error initializing vector store: {e}")
            self.vector_store = None
    
    def _init_memory(self):
        """Khởi tạo conversation và search memory"""
        # Conversation memory cho chat
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # Search history memory - lưu lại search queries và results
        self.search_history = {}  # session_id -> search history
        self.conversation_sessions = {}  # session_id -> conversation memory
        
        # Default session
        self.current_session_id = "default"
        self.conversation_sessions[self.current_session_id] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
    
    def _init_chains(self):
        """Khởi tạo các Langchain chains"""
        if not self.llm:
            self.qa_chain = None
            self.code_chain = None
            return
        
        # RAG Chain cho knowledge base
        if self.vector_store:
            self.qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=self.vector_store.as_retriever(search_kwargs={"k": 3}),
                memory=self.memory,
                return_source_documents=True,
                verbose=True
            )
        else:
            self.qa_chain = None
        
        # Code processing chain
        code_prompt = PromptTemplate(
            input_variables=["task", "code", "programming_language", "system_language"],
            template="""
You are an AI Assistant specialized in programming. Based on the system language, respond appropriately.

System Language: {system_language}
Task: {task}
Programming Language: {programming_language}
Code:
```{programming_language}
{code}
```

If system_language is 'vi':
- Respond in Vietnamese
- Use Vietnamese technical terms and explanations
- Be friendly and detailed in Vietnamese

If system_language is 'en':
- Respond in English
- Use English technical terms and explanations
- Be professional and clear in English

Please complete the requested task and return the result in the appropriate format.
For code tasks, always wrap code in markdown code blocks with the correct language identifier.
"""
        )
        
        self.code_chain = LLMChain(
            llm=self.llm,
            prompt=code_prompt,
            verbose=True
        )
    
    def _init_tools(self):
        """Khởi tạo tools cho agent"""
        self.tools = []
        
        # Knowledge Base Search Tool
        if self.vector_store:
            knowledge_search_tool = Tool(
                name="knowledge_search",
                description="Search the knowledge base for relevant information about coding standards, conventions, and best practices",
                func=self._knowledge_search
            )
            self.tools.append(knowledge_search_tool)
        
        # Code Analysis Tool
        code_analysis_tool = Tool(
            name="code_analysis",
            description="Analyze code for bugs, optimization opportunities, or explanations",
            func=self._analyze_code
        )
        self.tools.append(code_analysis_tool)
        
        # Code Generation Tool
        code_generation_tool = Tool(
            name="code_generation",
            description="Generate code, comments, or unit tests based on requirements",
            func=self._generate_code
        )
        self.tools.append(code_generation_tool)
    
    def _init_agent(self):
        """Khởi tạo Langchain agent"""
        if not self.llm or not self.tools:
            self.agent = None
            return
        
        try:
            self.agent = initialize_agent(
                tools=self.tools,
                llm=self.llm,
                agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
                memory=self.memory,
                verbose=True,
                max_iterations=3,
                early_stopping_method="generate"
            )
            print("✅ Langchain agent initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing agent: {e}")
            self.agent = None
    
    def _knowledge_search(self, query: str) -> str:
        """Tool function để search knowledge base"""
        try:
            if not self.vector_store:
                return "Knowledge base not available"
            
            docs = self.vector_store.similarity_search(query, k=3)
            if not docs:
                return "No relevant information found in knowledge base"
            
            results = []
            for i, doc in enumerate(docs, 1):
                results.append(f"Result {i}: {doc.page_content[:500]}...")
            
            return "\n\n".join(results)
        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"
    
    def _analyze_code(self, code_info: str) -> str:
        """Tool function để analyze code"""
        try:
            if not self.code_chain:
                return "Code analysis not available"
            
            # Parse code_info (should contain task and code)
            parts = code_info.split("|||")
            if len(parts) < 3:
                return "Invalid format. Use: task|||code|||language"
            
            task, code, language = parts[0], parts[1], parts[2]
            
            result = self.code_chain.run(
                task=task,
                code=code,
                language=language
            )
            return result
        except Exception as e:
            return f"Error analyzing code: {str(e)}"
    
    def _generate_code(self, requirements: str) -> str:
        """Tool function để generate code"""
        try:
            if not self.llm:
                return "Code generation not available"
            
            prompt = f"""
Generate code based on the following requirements:
{requirements}

Please provide clean, well-commented code with explanations.
"""
            
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"Error generating code: {str(e)}"
    
    # ================================
    # PUBLIC METHODS
    # ================================
    
    def chat_with_rag(self, question: str, chat_history: List = None, session_id: str = None, system_language: str = 'en') -> Dict[str, Any]:
        """
        Chat với knowledge base sử dụng RAG với memory support
        
        Args:
            question: Câu hỏi từ user
            chat_history: Lịch sử chat (optional)  
            session_id: Session ID để quản lý memory riêng biệt
            system_language: Ngôn ngữ hệ thống ('en' hoặc 'vi')
            
        Returns:
            dict: Response với answer, source documents và search history
        """
        try:
            # Sử dụng Azure OpenAI client trực tiếp thay vì Langchain
            if not self.client:
                return {
                    "success": False,
                    "error": "Azure OpenAI client not available"
                }
            
            # Lấy memory cho session
            session_memory = self.get_or_create_session_memory(session_id) if session_id else None
            
            # Tạo messages từ memory và question hiện tại
            messages = []
            
            # Tạo system message dựa trên ngôn ngữ
            if system_language == 'vi':
                system_content = """Bạn là một AI Assistant thông minh và hữu ích, chuyên về lập trình và công nghệ. 

Nhiệm vụ của bạn:
- Trả lời câu hỏi về lập trình, debug code, giải thích thuật toán
- Hỗ trợ viết code, tối ưu hóa và review code  
- Giải thích các khái niệm công nghệ một cách dễ hiểu
- Hướng dẫn best practices trong lập trình
- Trả lời các câu hỏi tổng quát khác

Phong cách trả lời:
- Thân thiện, nhiệt tình và chuyên nghiệp
- Giải thích rõ ràng, có ví dụ cụ thể
- Sử dụng emoji phù hợp để tạo không khí vui vẻ
- Trả lời bằng tiếng Việt
- Khi giải thích code, sử dụng markdown code blocks với syntax highlighting"""
            else:
                system_content = """You are an intelligent and helpful AI Assistant specializing in programming and technology.

Your tasks:
- Answer programming questions, debug code, explain algorithms
- Help write code, optimize and review code
- Explain technology concepts in an easy-to-understand way
- Guide best practices in programming
- Answer other general questions

Response style:
- Friendly, enthusiastic and professional
- Clear explanations with specific examples
- Use appropriate emojis to create a pleasant atmosphere
- Respond in English
- When explaining code, use markdown code blocks with syntax highlighting"""
            
            # Thêm system message
            messages.append({
                "role": "system",
                "content": system_content
            })
            
            # Thêm chat history từ memory nếu có
            if session_memory and hasattr(session_memory, 'chat_memory'):
                for message in session_memory.chat_memory.messages[-10:]:  # Lấy 10 tin nhắn gần nhất
                    if hasattr(message, 'content'):
                        role = "user" if message.__class__.__name__ == "HumanMessage" else "assistant"
                        messages.append({
                            "role": role,
                            "content": message.content
                        })
            
            # Thêm question hiện tại
            messages.append({
                "role": "user", 
                "content": question
            })
            
            # Gọi Azure OpenAI
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=0.7,
                max_tokens=4000
            )
            
            answer = response.choices[0].message.content
            
            # Lưu vào memory nếu có session
            if session_memory:
                session_memory.chat_memory.add_user_message(question)
                session_memory.chat_memory.add_ai_message(answer)
            
            return {
                "success": True,
                "answer": answer,
                "source_documents": [],  # Sẽ được thêm từ vector search
                "search_context": {},
                "session_id": session_id or self.current_session_id
            }
            
        except Exception as e:
            print(f"Error in RAG chat: {str(e)}")
            return {
                "success": False,
                "error": f"Error in RAG chat: {str(e)}"
            }
    
    def process_code_with_langchain(self, task: str, code: str, programming_language: str, system_language: str = 'en') -> Dict[str, Any]:
        """
        Xử lý code sử dụng Langchain
        
        Args:
            task: Loại task (comment, fix_bugs, optimize, etc.)
            code: Source code
            programming_language: Programming language (javascript, python, java, ...)
            system_language: Ngôn ngữ hệ thống ('en' hoặc 'vi')
            
        Returns:
            dict: Processed result
        """
        try:
            # Debug log để kiểm tra tham số
            print(f"Langchain Service - process_code_with_langchain: task={task}, programming_language={programming_language}, system_language={system_language}")
            
            if not self.code_chain:
                return {
                    "success": False,
                    "error": "Code chain not available"
                }

            result = self.code_chain.run(
                task=task,
                code=code,
                programming_language=programming_language,
                system_language=system_language
            )
            
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing code: {str(e)}"
            }
    
    def chat_with_agent(self, message: str) -> Dict[str, Any]:
        """
        Chat với Langchain agent (có thể sử dụng tools)
        
        Args:
            message: Message từ user
            
        Returns:
            dict: Response từ agent
        """
        try:
            if not self.agent:
                return {
                    "success": False,
                    "error": "Agent not available"
                }
            
            result = self.agent.run(message)
            
            return {
                "success": True,
                "response": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error in agent chat: {str(e)}"
            }
    
    def add_documents_to_vector_store(self, documents: List[Document]):
        """
        Thêm documents vào vector store
        
        Args:
            documents: List of Langchain Document objects
        """
        try:
            if not self.vector_store:
                return False, "Vector store not available"
            
            self.vector_store.add_documents(documents)
            return True, "Documents added successfully"
        except Exception as e:
            return False, f"Error adding documents: {str(e)}"
    
    def search_vector_store(self, query: str, k: int = 3) -> List[Document]:
        """
        Search vector store với caching
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List of relevant documents
        """
        try:
            if not self.vector_store:
                return []
            
            return self.vector_store.similarity_search(query, k=k)
        except Exception as e:
            print(f"Error searching vector store: {e}")
            return []
    
    # ================================
    # MEMORY MANAGEMENT METHODS
    # ================================
    
    def get_or_create_session_memory(self, session_id: str):
        """
        Lấy hoặc tạo memory cho session cụ thể
        
        Args:
            session_id: ID của session
            
        Returns:
            ConversationBufferMemory instance
        """
        if session_id not in self.conversation_sessions:
            self.conversation_sessions[session_id] = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
        return self.conversation_sessions[session_id]
    
    def get_search_context(self, question: str, session_id: str = None) -> Dict[str, Any]:
        """
        Lấy context từ search history để tránh duplicate searches
        
        Args:
            question: Câu hỏi hiện tại
            session_id: Session ID
            
        Returns:
            dict: Search context với related searches
        """
        session_id = session_id or self.current_session_id
        
        if session_id not in self.search_history:
            return {"related_searches": [], "cache_hit": False}
        
        session_history = self.search_history[session_id]
        
        # Tìm kiếm tương tự trong history
        related_searches = []
        for prev_search in session_history[-10:]:  # Chỉ check 10 searches gần nhất
            similarity = self._calculate_question_similarity(question, prev_search["question"])
            if similarity > 0.7:  # Threshold cho similar questions
                related_searches.append({
                    "question": prev_search["question"],
                    "timestamp": prev_search["timestamp"],
                    "similarity": similarity,
                    "answer_preview": prev_search.get("answer", "")[:100] + "..."
                })
        
        return {
            "related_searches": related_searches,
            "cache_hit": len(related_searches) > 0,
            "total_searches_in_session": len(session_history)
        }
    
    def save_search_to_history(self, question: str, result: Dict, session_id: str = None):
        """
        Lưu search result vào history
        
        Args:
            question: Câu hỏi
            result: Kết quả từ RAG chain
            session_id: Session ID
        """
        session_id = session_id or self.current_session_id
        
        if session_id not in self.search_history:
            self.search_history[session_id] = []
        
        from datetime import datetime
        
        search_record = {
            "question": question,
            "answer": result.get("answer", ""),
            "source_docs_count": len(result.get("source_documents", [])),
            "timestamp": datetime.now().isoformat(),
            "source_documents": [
                {
                    "content_preview": doc.page_content[:100] + "...",
                    "metadata": doc.metadata
                } for doc in result.get("source_documents", [])
            ]
        }
        
        self.search_history[session_id].append(search_record)
        
        # Giới hạn history size (giữ 50 searches gần nhất)
        if len(self.search_history[session_id]) > 50:
            self.search_history[session_id] = self.search_history[session_id][-50:]
    
    def get_session_search_history(self, session_id: str = None, limit: int = 10) -> List[Dict]:
        """
        Lấy search history của session
        
        Args:
            session_id: Session ID
            limit: Số lượng results trả về
            
        Returns:
            List các search records
        """
        session_id = session_id or self.current_session_id
        
        if session_id not in self.search_history:
            return []
        
        return self.search_history[session_id][-limit:]
    
    def clear_session_memory(self, session_id: str = None):
        """
        Xóa memory và search history của session
        
        Args:
            session_id: Session ID để xóa
        """
        session_id = session_id or self.current_session_id
        
        if session_id in self.conversation_sessions:
            self.conversation_sessions[session_id].clear()
        
        if session_id in self.search_history:
            self.search_history[session_id] = []
    
    def _calculate_question_similarity(self, question1: str, question2: str) -> float:
        """
        Tính similarity giữa 2 câu hỏi (simple implementation)
        
        Args:
            question1: Câu hỏi thứ nhất
            question2: Câu hỏi thứ hai
            
        Returns:
            float: Similarity score (0-1)
        """
        # Simple word overlap similarity
        words1 = set(question1.lower().split())
        words2 = set(question2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Lấy thống kê về memory usage
        
        Returns:
            dict: Memory statistics
        """
        stats = {
            "total_sessions": len(self.conversation_sessions),
            "total_search_history_entries": sum(len(history) for history in self.search_history.values()),
            "sessions": {}
        }
        
        for session_id in self.conversation_sessions.keys():
            conversation_messages = len(self.conversation_sessions[session_id].chat_memory.messages) if hasattr(self.conversation_sessions[session_id], 'chat_memory') else 0
            search_entries = len(self.search_history.get(session_id, []))
            
            stats["sessions"][session_id] = {
                "conversation_messages": conversation_messages,
                "search_history_entries": search_entries
            }
        
        return stats
