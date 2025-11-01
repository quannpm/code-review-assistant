"""
Knowledge Base Service - Xử lý logic nghiệp vụ cho knowledge base với Langchain

Service này chứa:
- Xử lý upload file PDF sử dụng Langchain DocumentLoaders
- Trích xuất và split text với Langchain TextSplitters
- Vector store operations với Langchain ChromaDB integration
- Quản lý metadata với Langchain Document format
"""

import os
import hashlib
import json
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
import PyPDF2
import re
from typing import List, Dict, Optional

# Langchain imports
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_chroma import Chroma

class KnowledgeBaseService:
    """
    Service xử lý các thao tác liên quan đến knowledge base
    """
    
    def __init__(self, upload_folder='uploads', chroma_db_path='./chroma_db'):
        """
        Khởi tạo service với Langchain integration
        
        Args:
            upload_folder: Thư mục lưu file upload
            chroma_db_path: Đường dẫn đến ChromaDB
        """
        self.upload_folder = upload_folder
        self.chroma_db_path = chroma_db_path
        self.allowed_extensions = {'pdf'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
        # Tạo thư mục uploads nếu chưa tồn tại
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
        
        # Khởi tạo Langchain components
        self._init_langchain_components()
    
    def _init_langchain_components(self):
        """
        Khởi tạo các components của Langchain
        """
        try:
            # Khởi tạo embeddings
            self.embeddings = SentenceTransformerEmbeddings(
                model_name="all-MiniLM-L6-v2"
            )
            
            # Khởi tạo text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=['\n\n', '\n', '. ', '! ', '? ', '; ', ': ', ' ', '']
            )
            
            # Khởi tạo Langchain ChromaDB vector store
            self.vector_store = Chroma(
                collection_name="knowledge_base",
                embedding_function=self.embeddings,
                persist_directory=self.chroma_db_path
            )
            
            print("✅ Langchain components initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing Langchain components: {str(e)}")
            self.embeddings = None
            self.text_splitter = None
            self.vector_store = None
    
    def debug_vector_store_status(self):
        """
        Debug function để kiểm tra trạng thái vector store
        """
        try:
            if not self.vector_store:
                print("❌ Vector store is None")
                return False
            
            # Thử lấy tổng số documents
            collection = self.vector_store._collection
            count = collection.count()
            print(f"📊 Vector store status:")
            print(f"   - Collection name: {collection.name}")
            print(f"   - Total documents: {count}")
            
            if count > 0:
                # Lấy một vài documents mẫu
                sample = collection.peek(limit=3)
                print(f"   - Sample document IDs: {sample.get('ids', [])[:3]}")
                
                # Test search
                test_docs = self.vector_store.similarity_search("test", k=1)
                print(f"   - Test search returned: {len(test_docs)} documents")
                
            return True
            
        except Exception as e:
            print(f"❌ Error checking vector store status: {str(e)}")
            return False
    
    def is_allowed_file(self, filename):
        """
        Kiểm tra file có được phép upload không
        
        Args:
            filename: Tên file
            
        Returns:
            bool: True nếu file được phép upload
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def validate_file_size(self, file):
        """
        Kiểm tra kích thước file
        
        Args:
            file: File object từ request
            
        Returns:
            tuple: (is_valid, file_size, error_message)
        """
        try:
            file.seek(0, 2)  # Seek to end of file
            file_size = file.tell()
            file.seek(0)  # Reset to beginning
            
            if file_size > self.max_file_size:
                return False, file_size, f"File size must be less than {self.max_file_size // (1024*1024)}MB"
            
            return True, file_size, None
            
        except Exception as e:
            return False, 0, f"Error checking file size: {str(e)}"
    
    def extract_text_from_pdf(self, file_path):
        """
        Trích xuất text từ file PDF
        
        Args:
            file_path: Đường dẫn đến file PDF
            
        Returns:
            tuple: (success, text, pages_count, error_message)
        """
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                pages_count = len(pdf_reader.pages)
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            return True, text, pages_count, None
            
        except Exception as e:
            return False, "", 0, f"Error extracting text from PDF: {str(e)}"
    
    def calculate_file_hash(self, file_path):
        """
        Tính hash MD5 của file
        
        Args:
            file_path: Đường dẫn đến file
            
        Returns:
            str: Hash MD5 của file
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def generate_unique_filename(self, filename):
        """
        Tạo tên file unique với timestamp
        
        Args:
            filename: Tên file gốc
            
        Returns:
            tuple: (unique_filename, timestamp)
        """
        secure_name = secure_filename(filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{secure_name}"
        return unique_filename, timestamp
    
    def save_file_metadata(self, file_id, metadata):
        """
        Lưu metadata của file
        
        Args:
            file_id: ID của file
            metadata: Dictionary chứa metadata
            
        Returns:
            tuple: (success, metadata_path, error_message)
        """
        try:
            metadata_path = os.path.join(self.upload_folder, f"{file_id}_metadata.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            return True, metadata_path, None
            
        except Exception as e:
            return False, "", f"Error saving metadata: {str(e)}"
    
    def save_extracted_text(self, file_id, text):
        """
        Lưu text đã trích xuất vào file riêng
        
        Args:
            file_id: ID của file
            text: Text đã trích xuất
            
        Returns:
            tuple: (success, text_path, error_message)
        """
        try:
            text_path = os.path.join(self.upload_folder, f"{file_id}_text.txt")
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            return True, text_path, None
            
        except Exception as e:
            return False, "", f"Error saving extracted text: {str(e)}"
    
    def _init_chroma_db(self):
        """
        Deprecated - được thay thế bởi _init_langchain_components
        """
        print("⚠️ _init_chroma_db is deprecated, using Langchain components instead")
    
    def _split_text_into_chunks(self, text, chunk_size=1000, overlap=200):
        """
        Chia text thành chunks sử dụng Langchain TextSplitter
        
        Args:
            text: Text cần chia
            chunk_size: Kích thước mỗi chunk
            overlap: Overlap giữa các chunks
            
        Returns:
            List[str]: Danh sách các text chunks
        """
        try:
            if not self.text_splitter:
                # Fallback to basic splitting if text_splitter not available
                return self._basic_text_split(text, chunk_size, overlap)
            
            # Sử dụng Langchain RecursiveCharacterTextSplitter
            documents = [Document(page_content=text)]
            split_docs = self.text_splitter.split_documents(documents)
            
            return [doc.page_content for doc in split_docs]
            
        except Exception as e:
            print(f"❌ Error splitting text with Langchain: {str(e)}")
            # Fallback to basic splitting
            return self._basic_text_split(text, chunk_size, overlap)
    
    def _basic_text_split(self, text, chunk_size=1000, overlap=200):
        """
        Phương thức split text cơ bản làm fallback
        """
        # Làm sạch text
        cleaned_text = re.sub(r'\n+', '\n', text.strip())
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        if len(cleaned_text) <= chunk_size:
            return [cleaned_text]
        
        chunks = []
        start = 0
        
        while start < len(cleaned_text):
            end = start + chunk_size
            
            if end < len(cleaned_text):
                break_chars = ['. ', '\n', '! ', '? ', '; ', ': ', '.\n', '!\n', '?\n']
                best_break = -1
                for break_char in break_chars:
                    break_pos = cleaned_text.rfind(break_char, start, end)
                    if break_pos != -1:
                        best_break = break_pos + len(break_char)
                        break
                
                if best_break == -1:
                    space_pos = cleaned_text.rfind(' ', start, end)
                    if space_pos != -1 and space_pos > start + chunk_size * 0.7:
                        best_break = space_pos + 1
                
                if best_break != -1:
                    end = best_break
            
            chunk = cleaned_text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = max(start + 1, end - overlap)
            
            if start >= len(cleaned_text):
                break
        
        return chunks
    
    def save_to_vector_db(self, file_id, title, description, extracted_text, metadata):
        """
        Lưu text vào Langchain ChromaDB vector store
        
        Args:
            file_id: UUID của file
            title: Tiêu đề tài liệu
            description: Mô tả tài liệu  
            extracted_text: Text đã trích xuất từ PDF
            metadata: Metadata của file
            
        Returns:
            tuple: (success, chunks_count, error_message)
        """
        try:
            if not self.vector_store:
                return False, 0, "Vector store not initialized"
            
            # Chia text thành chunks sử dụng Langchain
            text_chunks = self._split_text_into_chunks(extracted_text)
            
            if not text_chunks:
                return False, 0, "No text chunks to save"
            
            # Tạo Langchain Documents
            documents = []
            for i, chunk in enumerate(text_chunks):
                # Phát hiện ngôn ngữ và chuẩn hóa
                language = self._detect_language(chunk)
                normalized_chunk = self._normalize_vietnamese_text(chunk)
                
                # Metadata cho mỗi document
                doc_metadata = {
                    "file_id": file_id,
                    "chunk_index": i,
                    "title": title,
                    "description": description,
                    "filename": metadata.get("original_filename", ""),
                    "filename_uuid": file_id,
                    "upload_time": metadata.get("upload_time", ""),
                    "file_size": metadata.get("file_size", 0),
                    "pages_count": metadata.get("pages_count", 0),
                    "chunk_length": len(chunk),
                    "language": language,
                    "normalized_content": normalized_chunk
                }
                
                # Tạo Langchain Document
                doc = Document(
                    page_content=chunk,
                    metadata=doc_metadata
                )
                documents.append(doc)
            
            # Tạo unique IDs cho các documents
            doc_ids = [f"{file_id}_chunk_{i}" for i in range(len(documents))]
            
            # Lưu vào Langchain ChromaDB vector store
            self.vector_store.add_documents(documents, ids=doc_ids)
            
            print(f"✅ Saved {len(documents)} documents to Langchain ChromaDB for file: {title}")
            return True, len(documents), None
            
        except Exception as e:
            error_msg = f"Error saving to Langchain vector store: {str(e)}"
            print(f"❌ {error_msg}")
            return False, 0, error_msg
    
    def search_in_vector_db(self, query: str, n_results: int = 5, file_id: Optional[str] = None) -> tuple:
        """
        Tìm kiếm trong Langchain vector store
        
        Args:
            query: Câu hỏi/từ khóa tìm kiếm
            n_results: Số kết quả trả về
            file_id: Tìm kiếm trong file cụ thể (optional)
            
        Returns:
            tuple: (success, results, error_message)
        """
        try:
            if not self.vector_store:
                return False, [], "Vector store not initialized"
            
            # Kiểm tra xem có documents nào trong vector store không
            try:
                # Test query để kiểm tra vector store có hoạt động không
                test_docs = self.vector_store.similarity_search("test", k=1)
                print(f"🔍 Vector store test: Found {len(test_docs)} documents total")
            except Exception as test_e:
                print(f"⚠️ Vector store test failed: {str(test_e)}")
            
            # Thực hiện similarity search với đúng syntax của Langchain ChromaDB
            if file_id:
                # Tìm kiếm với filter
                docs = self.vector_store.similarity_search(
                    query, 
                    k=n_results,
                    filter={"file_id": file_id}
                )
            else:
                # Tìm kiếm toàn bộ
                docs = self.vector_store.similarity_search(query, k=n_results)
            
            print(f"🔍 Search query: '{query}' - Found {len(docs)} documents")
            
            # Format kết quả
            formatted_results = []
            for i, doc in enumerate(docs):
                result_item = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": 0.8 - (i * 0.1)  # Điểm giảm dần theo thứ tự
                }
                formatted_results.append(result_item)
                print(f"📄 Result {i+1}: {doc.page_content[:100]}...")
            
            return True, formatted_results, None
            
        except Exception as e:
            error_msg = f"Error searching Langchain vector store: {str(e)}"
            print(f"❌ Search error: {error_msg}")
            return False, [], error_msg
    
    def search_with_scores(self, query: str, n_results: int = 5, file_id: Optional[str] = None) -> tuple:
        """
        Tìm kiếm với similarity scores
        
        Args:
            query: Câu hỏi/từ khóa tìm kiếm
            n_results: Số kết quả trả về
            file_id: Tìm kiếm trong file cụ thể (optional)
            
        Returns:
            tuple: (success, results, error_message)
        """
        try:
            if not self.vector_store:
                return False, [], "Vector store not initialized"
            
            # Sử dụng similarity_search_with_score với đúng syntax
            if file_id:
                # Tìm kiếm với filter
                docs_with_scores = self.vector_store.similarity_search_with_score(
                    query, 
                    k=n_results,
                    filter={"file_id": file_id}
                )
            else:
                # Tìm kiếm toàn bộ
                docs_with_scores = self.vector_store.similarity_search_with_score(query, k=n_results)
            
            print(f"🔍 Search with scores: '{query}' - Found {len(docs_with_scores)} documents")
            
            # Format kết quả với scores thực tế
            formatted_results = []
            for i, (doc, score) in enumerate(docs_with_scores):
                # ChromaDB trả về distance (0 = identical, higher = less similar)
                # Chuyển đổi thành similarity score (0-1, higher = more similar)
                similarity_score = max(0, 1 - score)
                
                result_item = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": round(similarity_score, 4)
                }
                formatted_results.append(result_item)
                print(f"📄 Result {i+1} (score: {similarity_score:.4f}): {doc.page_content[:100]}...")
            
            return True, formatted_results, None
            
        except Exception as e:
            error_msg = f"Error searching with scores: {str(e)}"
            print(f"❌ Search with scores error: {error_msg}")
            return False, [], error_msg
    
    def delete_from_vector_db(self, file_id):
        """
        Xóa documents khỏi Langchain vector store
        
        Args:
            file_id: UUID của file cần xóa
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            if not self.vector_store:
                return False, "Vector store not initialized"
            
            # Tìm tất cả documents của file này
            docs = self.vector_store.get(where={"file_id": file_id})
            
            if docs and docs.get("ids"):
                # Xóa documents theo IDs
                self.vector_store.delete(ids=docs["ids"])
                print(f"✅ Deleted {len(docs['ids'])} documents from Langchain ChromaDB for file: {file_id}")
            
            return True, None
            
        except Exception as e:
            error_msg = f"Error deleting from Langchain vector store: {str(e)}"
            return False, error_msg
    
    def get_vector_store_as_retriever(self, search_kwargs: Optional[Dict] = None):
        """
        Lấy vector store dưới dạng Langchain Retriever
        
        Args:
            search_kwargs: Tham số cho retriever
            
        Returns:
            Langchain Retriever hoặc None
        """
        try:
            if not self.vector_store:
                return None
            
            if search_kwargs is None:
                search_kwargs = {"k": 3}
            
            return self.vector_store.as_retriever(search_kwargs=search_kwargs)
            
        except Exception as e:
            print(f"❌ Error creating retriever: {str(e)}")
            return None
    
    def add_documents_to_vector_store(self, documents: List[Document]):
        """
        Thêm Langchain Documents vào vector store
        
        Args:
            documents: List of Langchain Document objects
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            if not self.vector_store:
                return False, "Vector store not initialized"
            
            self.vector_store.add_documents(documents)
            return True, None
            
        except Exception as e:
            error_msg = f"Error adding documents to vector store: {str(e)}"
            return False, error_msg
    
    def process_uploaded_file(self, file, title, description):
        """
        Xử lý file upload hoàn chỉnh
        
        Args:
            file: File object từ request
            title: Tiêu đề tài liệu
            description: Mô tả tài liệu
            
        Returns:
            tuple: (success, result_data, error_message, status_code)
        """
        try:
            # Validate file
            if not file or not file.filename:
                return False, None, "No file selected", 400
            
            if not self.is_allowed_file(file.filename):
                return False, None, "Only PDF files are allowed", 400
            
            # Validate file size
            is_valid_size, file_size, size_error = self.validate_file_size(file)
            if not is_valid_size:
                return False, None, size_error, 413
            
            # Generate unique filename
            unique_filename, timestamp = self.generate_unique_filename(file.filename)
            file_path = os.path.join(self.upload_folder, unique_filename)
            
            # Save file
            file.save(file_path)
            
            # Extract text from PDF
            extract_success, extracted_text, pages_count, extract_error = self.extract_text_from_pdf(file_path)
            if not extract_success:
                # Clean up file if extraction failed
                if os.path.exists(file_path):
                    os.remove(file_path)
                return False, None, extract_error, 500
            
            # Calculate file hash
            file_hash = self.calculate_file_hash(file_path)
            
            # Generate UUID for file_id
            file_id = str(uuid.uuid4())
            
            # Create metadata
            metadata = {
                "file_id": file_id,
                "original_filename": file.filename,
                "title": title,
                "stored_filename": unique_filename,
                "file_path": file_path,
                "file_size": file_size,
                "file_hash": file_hash,
                "pages_count": pages_count,
                "text_length": len(extracted_text),
                "upload_time": datetime.now().isoformat(),
                "description": description,
                "extracted_text": extracted_text
            }
            
            # Save metadata
            metadata_success, metadata_path, metadata_error = self.save_file_metadata(file_id, metadata)
            if not metadata_success:
                # Clean up file if metadata saving failed
                if os.path.exists(file_path):
                    os.remove(file_path)
                return False, None, metadata_error, 500
            
            # Save extracted text
            text_success, text_path, text_error = self.save_extracted_text(file_id, extracted_text)
            if not text_success:
                # Clean up files if text saving failed
                if os.path.exists(file_path):
                    os.remove(file_path)
                if os.path.exists(metadata_path):
                    os.remove(metadata_path)
                return False, None, text_error, 500
            
            # Lưu vào ChromaDB vector database
            # Chức năng này cho phép tìm kiếm semantic trong nội dung PDF
            vector_success, chunks_count, vector_error = self.save_to_vector_db(
                file_id, title, description, extracted_text, metadata
            )
            
            # Ghi log nhưng không fail nếu vector DB có lỗi
            if not vector_success:
                print(f"⚠️ Warning: Could not save to vector DB: {vector_error}")
                # Không return error vì file đã được lưu thành công
            else:
                print(f"✅ Successfully saved {chunks_count} text chunks to vector database")
            
            # Prepare response data (exclude sensitive info)
            response_data = {
                key: value for key, value in metadata.items() 
                if key not in ['extracted_text', 'file_path', 'stored_filename']
            }
            
            # Thêm thông tin về vector DB vào response
            response_data['vector_chunks_count'] = chunks_count if vector_success else 0
            response_data['vector_db_status'] = 'success' if vector_success else 'warning'
            
            return True, response_data, "File uploaded and processed successfully", 200
            
        except Exception as e:
            return False, None, f"Failed to process file: {str(e)}", 500
    
    def get_uploaded_files(self):
        """
        Lấy danh sách các file đã upload
        
        Returns:
            tuple: (success, files_data, error_message)
        """
        try:
            files_list = []
            
            # Kiểm tra thư mục upload tồn tại
            if not os.path.exists(self.upload_folder):
                return True, {"files": [], "total_files": 0}, None
            
            # Duyệt qua các file metadata
            for filename in os.listdir(self.upload_folder):
                if filename.endswith('_metadata.json'):
                    metadata_path = os.path.join(self.upload_folder, filename)
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        # Chỉ lấy thông tin cần thiết
                        file_info = {
                            'file_id': metadata.get('file_id'),
                            'filename': metadata.get('original_filename'),
                            'title': metadata.get('title'),
                            'file_size': metadata.get('file_size'),
                            'pages_count': metadata.get('pages_count'),
                            'text_length': metadata.get('text_length'),
                            'upload_time': metadata.get('upload_time'),
                            'description': metadata.get('description', '')
                        }
                        files_list.append(file_info)
                        
                    except Exception as e:
                        # Skip files with invalid metadata
                        continue
            
            # Sắp xếp theo thời gian upload (mới nhất trước)
            files_list.sort(key=lambda x: x.get('upload_time', ''), reverse=True)
            
            result_data = {
                "files": files_list,
                "total_files": len(files_list)
            }
            
            return True, result_data, None
            
        except Exception as e:
            return False, None, f"Failed to list files: {str(e)}"
    
    def get_file_by_id(self, file_id):
        """
        Lấy thông tin chi tiết của một file theo ID
        
        Args:
            file_id: ID của file
            
        Returns:
            tuple: (success, file_data, error_message)
        """
        try:
            metadata_path = os.path.join(self.upload_folder, f"{file_id}_metadata.json")
            
            if not os.path.exists(metadata_path):
                return False, None, "File not found"
            
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Exclude sensitive information
            file_data = {
                key: value for key, value in metadata.items() 
                if key not in ['file_path', 'stored_filename']
            }
            
            return True, file_data, None
            
        except Exception as e:
            return False, None, f"Error retrieving file: {str(e)}"
    
    def delete_file(self, file_id):
        """
        Xóa file và metadata
        
        Args:
            file_id: ID của file
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            # Paths to delete
            metadata_path = os.path.join(self.upload_folder, f"{file_id}_metadata.json")
            text_path = os.path.join(self.upload_folder, f"{file_id}_text.txt")
            
            # Get file path from metadata
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    file_path = metadata.get('file_path')
            else:
                return False, "File not found"
            
            # Xóa khỏi vector database trước
            # Điều này đảm bảo không còn tham chiếu đến file trong vector DB
            vector_success, vector_error = self.delete_from_vector_db(file_id)
            if not vector_success:
                print(f"⚠️ Warning: Could not delete from vector DB: {vector_error}")
                # Tiếp tục xóa file dù vector DB có lỗi
            
            # Delete files from filesystem
            files_to_delete = [metadata_path, text_path]
            if file_path and os.path.exists(file_path):
                files_to_delete.append(file_path)
            
            for file_to_delete in files_to_delete:
                if os.path.exists(file_to_delete):
                    os.remove(file_to_delete)
            
            print(f"✅ Successfully deleted file {file_id} and all associated data")
            return True, None
            
        except Exception as e:
            return False, f"Error deleting file: {str(e)}"
    
    def search_knowledge_base(self, query, max_results=5, file_id=None):
        """
        Tìm kiếm trong knowledge base sử dụng vector similarity
        
        Args:
            query: Câu hỏi hoặc từ khóa tìm kiếm
            max_results: Số kết quả tối đa trả về
            file_id: Tìm kiếm trong file cụ thể (optional)
            
        Returns:
            tuple: (success, search_results, error_message)
        """
        try:
            print(f"🔍 Searching knowledge base for: '{query}' (max_results: {max_results})")
            
            # Sử dụng hàm search_with_scores để có điểm similarity thực tế
            vector_success, vector_results, vector_error = self.search_with_scores(
                query, max_results, file_id
            )
            
            if not vector_success:
                print(f"❌ Vector search failed: {vector_error}")
                return False, [], f"Vector search failed: {vector_error}"
            
            print(f"✅ Vector search successful: Found {len(vector_results)} results")
            
            # Format kết quả cho API response
            formatted_results = []
            for result in vector_results:
                formatted_result = {
                    "content": result["content"],
                    "similarity_score": result["similarity_score"],
                    "source": {
                        "file_id": result["metadata"].get("file_id"),
                        "title": result["metadata"].get("title"),
                        "filename": result["metadata"].get("filename"),
                        "filename_uuid": result["metadata"].get("filename_uuid"),
                        "chunk_index": result["metadata"].get("chunk_index"),
                        "chunk_length": len(result["content"])
                    }
                }
                formatted_results.append(formatted_result)
            
            return True, formatted_results, None
            
        except Exception as e:
            error_msg = f"Search failed: {str(e)}"
            print(f"❌ Knowledge base search error: {error_msg}")
            return False, [], error_msg
    
    def get_vector_db_stats(self):
        """
        Lấy thống kê về vector database
        
        Returns:
            tuple: (success, stats, error_message)
        """
        try:
            if not self.collection:
                return False, {}, "ChromaDB not initialized"
            
            # Lấy số lượng documents trong collection
            count = self.collection.count()
            
            # Lấy thông tin về collection
            stats = {
                "total_chunks": count,
                "collection_name": self.collection.name,
                "db_path": self.chroma_db_path
            }
            
            return True, stats, None
            
        except Exception as e:
            return False, {}, f"Error getting stats: {str(e)}"
    
    # =============================================================================
    # TRUY XUẤT DỮ LIỆU TỪ CHROMADB
    # =============================================================================
    
    def get_all_chunks(self, limit=None):
        """
        Lấy tất cả chunks từ ChromaDB (không cần search query)
        
        Args:
            limit: Giới hạn số lượng chunks trả về (optional)
            
        Returns:
            tuple: (success, chunks_data, error_message)
        """
        try:
            if not self.collection:
                return False, [], "ChromaDB not initialized"
            
            # Lấy tất cả documents trong collection
            results = self.collection.get(
                limit=limit,
                include=["documents", "metadatas"]
            )
            
            # Format kết quả
            chunks_data = []
            if results["documents"]:
                for i, doc in enumerate(results["documents"]):
                    chunk_info = {
                        "id": results["ids"][i],
                        "content": doc,
                        "metadata": results["metadatas"][i] if results["metadatas"] else {}
                    }
                    chunks_data.append(chunk_info)
            
            return True, chunks_data, None
            
        except Exception as e:
            return False, [], f"Error getting all chunks: {str(e)}"
    
    def get_chunks_by_file_id(self, file_id):
        """
        Lấy tất cả chunks của một file cụ thể
        
        Args:
            file_id: UUID của file
            
        Returns:
            tuple: (success, chunks_data, error_message)
        """
        try:
            if not self.collection:
                return False, [], "ChromaDB not initialized"
            
            # Tìm tất cả chunks có file_id cụ thể
            results = self.collection.get(
                where={"file_id": file_id},
                include=["documents", "metadatas"]
            )
            
            # Sắp xếp theo chunk_index
            chunks_data = []
            if results["documents"]:
                for i, doc in enumerate(results["documents"]):
                    chunk_info = {
                        "id": results["ids"][i],
                        "content": doc,
                        "metadata": results["metadatas"][i] if results["metadatas"] else {},
                        "chunk_index": results["metadatas"][i].get("chunk_index", 0) if results["metadatas"] else 0
                    }
                    chunks_data.append(chunk_info)
                
                # Sắp xếp theo chunk_index
                chunks_data.sort(key=lambda x: x["chunk_index"])
            
            return True, chunks_data, None
            
        except Exception as e:
            return False, [], f"Error getting chunks by file ID: {str(e)}"
    
    def get_chunks_by_title(self, title):
        """
        Lấy chunks theo title của document
        
        Args:
            title: Tiêu đề document
            
        Returns:
            tuple: (success, chunks_data, error_message)
        """
        try:
            if not self.collection:
                return False, [], "ChromaDB not initialized"
            
            # Tìm chunks có title cụ thể
            results = self.collection.get(
                where={"title": title},
                include=["documents", "metadatas"]
            )
            
            chunks_data = []
            if results["documents"]:
                for i, doc in enumerate(results["documents"]):
                    chunk_info = {
                        "id": results["ids"][i],
                        "content": doc,
                        "metadata": results["metadatas"][i] if results["metadatas"] else {}
                    }
                    chunks_data.append(chunk_info)
            
            return True, chunks_data, None
            
        except Exception as e:
            return False, [], f"Error getting chunks by title: {str(e)}"
    
    def get_chunk_by_id(self, chunk_id):
        """
        Lấy một chunk cụ thể theo ID
        
        Args:
            chunk_id: ID của chunk (format: file_id_chunk_index)
            
        Returns:
            tuple: (success, chunk_data, error_message)
        """
        try:
            if not self.collection:
                return False, None, "ChromaDB not initialized"
            
            # Lấy chunk theo ID
            results = self.collection.get(
                ids=[chunk_id],
                include=["documents", "metadatas"]
            )
            
            if results["documents"] and len(results["documents"]) > 0:
                chunk_data = {
                    "id": chunk_id,
                    "content": results["documents"][0],
                    "metadata": results["metadatas"][0] if results["metadatas"] else {}
                }
                return True, chunk_data, None
            else:
                return False, None, "Chunk not found"
            
        except Exception as e:
            return False, None, f"Error getting chunk by ID: {str(e)}"
    
    def filter_chunks_by_metadata(self, filters, limit=None):
        """
        Lọc chunks theo metadata
        
        Args:
            filters: Dictionary chứa điều kiện lọc
                    Ví dụ: {"file_size": {"$gte": 1000}, "pages_count": {"$lte": 10}}
            limit: Giới hạn số kết quả
            
        Returns:
            tuple: (success, chunks_data, error_message)
        """
        try:
            if not self.collection:
                return False, [], "ChromaDB not initialized"
            
            # Lọc chunks theo metadata
            results = self.collection.get(
                where=filters,
                limit=limit,
                include=["documents", "metadatas"]
            )
            
            chunks_data = []
            if results["documents"]:
                for i, doc in enumerate(results["documents"]):
                    chunk_info = {
                        "id": results["ids"][i],
                        "content": doc,
                        "metadata": results["metadatas"][i] if results["metadatas"] else {}
                    }
                    chunks_data.append(chunk_info)
            
            return True, chunks_data, None
            
        except Exception as e:
            return False, [], f"Error filtering chunks: {str(e)}"
    
    def get_files_summary_from_chunks(self):
        """
        Lấy tóm tắt thông tin các file từ chunks trong ChromaDB
        
        Returns:
            tuple: (success, files_summary, error_message)
        """
        try:
            if not self.collection:
                return False, [], "ChromaDB not initialized"
            
            # Lấy tất cả chunks
            results = self.collection.get(include=["metadatas"])
            
            if not results["metadatas"]:
                return True, [], None
            
            # Nhóm chunks theo file_id
            files_dict = {}
            for metadata in results["metadatas"]:
                file_id = metadata.get("file_id")
                if file_id not in files_dict:
                    files_dict[file_id] = {
                        "file_id": file_id,
                        "title": metadata.get("title", ""),
                        "filename": metadata.get("filename", ""),
                        "upload_time": metadata.get("upload_time", ""),
                        "file_size": metadata.get("file_size", 0),
                        "pages_count": metadata.get("pages_count", 0),
                        "chunks_count": 0,
                        "total_chunk_length": 0
                    }
                
                # Cập nhật thống kê
                files_dict[file_id]["chunks_count"] += 1
                files_dict[file_id]["total_chunk_length"] += metadata.get("chunk_length", 0)
            
            # Chuyển thành list và sắp xếp
            files_summary = list(files_dict.values())
            files_summary.sort(key=lambda x: x["upload_time"], reverse=True)
            
            return True, files_summary, None
            
        except Exception as e:
            return False, [], f"Error getting files summary: {str(e)}"
    
    def search_chunks_with_filters(self, query, filters=None, n_results=5):
        """
        Tìm kiếm vector similarity với filters metadata
        
        Args:
            query: Câu hỏi tìm kiếm
            filters: Điều kiện lọc metadata (optional)
            n_results: Số kết quả trả về
            
        Returns:
            tuple: (success, results, error_message)
        """
        try:
            if not self.collection:
                return False, [], "ChromaDB not initialized"
            
            # Thực hiện tìm kiếm với filters
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filters,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format kết quả
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    result_item = {
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "similarity_score": 1 - results["distances"][0][i] if results["distances"] else 0
                    }
                    formatted_results.append(result_item)
            
            return True, formatted_results, None
            
        except Exception as e:
            return False, [], f"Error searching with filters: {str(e)}"

    def _detect_language(self, text):
        """
        Phát hiện ngôn ngữ chính của text (tiếng Việt hoặc tiếng Anh)
        Giữ lại method này vì vẫn cần thiết cho metadata
        """
        if not text or len(text.strip()) < 10:
            return 'unknown'
        
        vietnamese_chars = 'àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ'
        vietnamese_count = 0
        total_chars = 0
        
        for char in text.lower():
            if char.isalpha():
                total_chars += 1
                if char in vietnamese_chars:
                    vietnamese_count += 1
        
        if total_chars == 0:
            return 'unknown'
        
        vietnamese_ratio = vietnamese_count / total_chars
        
        if vietnamese_ratio > 0.05:
            return 'vi'
        elif vietnamese_ratio > 0.01:
            return 'mixed'
        else:
            return 'en'
    
    def _normalize_vietnamese_text(self, text):
        """
        Chuẩn hóa text tiếng Việt để tìm kiếm tốt hơn
        Giữ lại method này vì vẫn cần thiết cho text processing
        """
        if not text:
            return text
        
        normalized = text.lower()
        normalized = re.sub(r'[^\w\sàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    # ========================================
    # LEGACY METHODS - Deprecated với Langchain
    # ========================================
    
    def search_in_multiple_files(self, query, filename_uuids, max_results=5):
        """
        DEPRECATED: Sử dụng Langchain vector store search thay thế
        Tìm kiếm trong nhiều files cụ thể dựa trên list filename_uuid
        """
        print("⚠️ search_in_multiple_files is deprecated, using Langchain search instead")
        
        # Delegate to Langchain search with file filter
        return self.search_with_scores(query, max_results, file_id=filename_uuids[0] if filename_uuids else None)
    
    def reset_chromadb(self, confirm_reset=False):
        """
        Reset ChromaDB - Xóa tất cả chunks và tạo lại collection mới
        
        Args:
            confirm_reset: Xác nhận reset (bảo vệ khỏi xóa nhầm)
            
        Returns:
            tuple: (success, reset_info, error_message)
        """
        try:
            if not confirm_reset:
                return False, {}, "Please set confirm_reset=True to confirm reset operation"
            
            if not self.chroma_client:
                return False, {}, "ChromaDB client not initialized"
            
            # Lấy thông tin trước khi reset
            old_collection_info = {}
            if self.collection:
                try:
                    old_data = self.collection.get(include=["documents", "metadatas"])
                    old_collection_info = {
                        "total_chunks_deleted": len(old_data["documents"]) if old_data["documents"] else 0,
                        "collection_name": "knowledge_base"
                    }
                except:
                    old_collection_info = {"total_chunks_deleted": "unknown", "collection_name": "knowledge_base"}
            
            # Xóa collection cũ
            try:
                self.chroma_client.delete_collection(name="knowledge_base")
                print("✅ Deleted old collection 'knowledge_base'")
            except Exception as e:
                print(f"⚠️ Could not delete old collection (might not exist): {str(e)}")
            
            # Tạo collection mới
            self.collection = self.chroma_client.get_or_create_collection(
                name="knowledge_base",
                metadata={"description": "PDF document knowledge base with text chunks - Reset on " + datetime.now().isoformat()}
            )
            
            reset_info = {
                "reset_timestamp": datetime.now().isoformat(),
                "old_collection_info": old_collection_info,
                "new_collection_created": True,
                "db_path": self.chroma_db_path
            }
            
            print(f"🔄 ChromaDB reset completed successfully")
            print(f"📊 Deleted {old_collection_info.get('total_chunks_deleted', 0)} chunks")
            
            return True, reset_info, "ChromaDB reset completed successfully"
            
        except Exception as e:
            return False, {}, f"Error resetting ChromaDB: {str(e)}"
    
    def clear_all_chunks(self):
        """
        Xóa tất cả chunks nhưng giữ nguyên collection
        (Phương thức nhẹ hơn reset_chromadb)
        
        Returns:
            tuple: (success, clear_info, error_message)
        """
        try:
            if not self.collection:
                return False, {}, "ChromaDB collection not initialized"
            
            # Lấy tất cả IDs
            all_data = self.collection.get(include=["documents"])
            total_chunks = len(all_data["ids"]) if all_data["ids"] else 0
            
            if total_chunks == 0:
                return True, {"chunks_cleared": 0, "message": "No chunks to clear"}, "No chunks found"
            
            # Xóa tất cả chunks
            self.collection.delete(ids=all_data["ids"])
            
            clear_info = {
                "chunks_cleared": total_chunks,
                "clear_timestamp": datetime.now().isoformat(),
                "collection_name": "knowledge_base"
            }
            
            print(f"🗑️ Cleared {total_chunks} chunks from ChromaDB")
            
            return True, clear_info, f"Cleared {total_chunks} chunks successfully"
            
        except Exception as e:
            return False, {}, f"Error clearing chunks: {str(e)}"
