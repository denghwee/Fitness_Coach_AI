# Fitness Coach AI

Hệ thống AI Coach thể dục thông minh sử dụng LLM (Large Language Model) và RAG (Retrieval Augmented Generation) để cung cấp kế hoạch tập luyện và dinh dưỡng cá nhân hóa cho người dùng.

## 🚀 Tính năng

- **Chat với AI Coach**: Tương tác trực tiếp với AI để nhận tư vấn về thể dục và dinh dưỡng
- **Tạo kế hoạch tập luyện**: Tự động tạo kế hoạch tập luyện cá nhân hóa dựa trên hồ sơ người dùng
- **Tạo kế hoạch dinh dưỡng**: Tạo thực đơn phù hợp với mục tiêu và chế độ ăn của người dùng
- **RAG (Retrieval Augmented Generation)**: Sử dụng vector database để truy xuất thông tin từ tài liệu PDF về thể dục và dinh dưỡng
- **Quản lý bộ nhớ**: Lưu trữ lịch sử chat và kế hoạch của người dùng
- **Hỗ trợ nhiều LLM**: OpenAI và Ollama

## 📋 Yêu cầu hệ thống

- Python 3.11+
- MySQL 5.7+ hoặc 8.0+
- ChromaDB (được cài đặt tự động qua requirements.txt)

## 🛠️ Cài đặt

### 1. Clone repository

```bash
git clone <repository-url>
cd Fitness_Coach_AI
```

### 2. Tạo môi trường ảo

```bash
python -m venv venv
source venv/bin/activate  # Trên Windows: venv\Scripts\activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình môi trường

Tạo file `.env` trong thư mục gốc với nội dung:

```env
# App Configuration
FLASK_ENV=development
FLASK_PORT=5003

# Database Configuration
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=fitness_coach_db

# LLM Configuration
LLM_PROVIDER=openai  # hoặc "ollama"
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-5-mini-2025-08-07

# Ollama Configuration (nếu sử dụng Ollama)
OLLAMA_MODEL=llama3.1
OLLAMA_BASE_URL=http://localhost:11434

# RAG Configuration
DB_TYPE=chroma
EMBEDDING_PROVIDER=openai

# Agent Settings
DEFAULT_TEMPERATURE=0.3
```

### 5. Khởi tạo database

```bash
# Chạy migrations
flask db upgrade
```

### 6. Chuẩn bị dữ liệu RAG

Đảm bảo các file PDF trong thư mục `data/PDF/` đã được ingest vào ChromaDB. Nếu chưa, chạy script ingest:

```python
from app.rag.ingest import ingest_documents
ingest_documents()
```

## 🏃 Chạy ứng dụng

### Development mode

```bash
python run.py
```

Ứng dụng sẽ chạy tại `http://localhost:5003`

### Docker

```bash
docker build -t fitness-coach-ai .
docker run -p 5003:5003 --env-file .env fitness-coach-ai
```

## 📡 API Endpoints

Tất cả endpoints yêu cầu JWT authentication trong header:
```
Authorization: Bearer <token>
```

### Chat với AI

```
POST /api/v3/agent/chat
```

Body:
```json
{
  "message": "Tôi muốn giảm cân, bạn có thể giúp tôi không?"
}
```

### Kế hoạch tập luyện

**Tạo kế hoạch:**
```
POST /api/v3/agent/workout-plan
```

**Lấy kế hoạch:**
```
GET /api/v3/agent/workout-plan
```

**CRUD operations:**
```
GET /api/v3/agent/workout-plan/db
POST /api/v3/agent/workout-plan/db
PUT /api/v3/agent/workout-plan/db
DELETE /api/v3/agent/workout-plan/db
```

### Kế hoạch dinh dưỡng

**Tạo kế hoạch:**
```
POST /api/v3/agent/meal-plan
```

**Lấy kế hoạch:**
```
GET /api/v3/agent/meal-plan
```

**CRUD operations:**
```
GET /api/v3/agent/meal-plan/db
POST /api/v3/agent/meal-plan/db
PUT /api/v3/agent/meal-plan/db
DELETE /api/v3/agent/meal-plan/db
```

## 📁 Cấu trúc dự án

```
Fitness_Coach_AI/
├── app/
│   ├── agent/              # Core AI agent logic
│   │   ├── core.py         # Main agent handler
│   │   ├── planner.py      # Planning logic
│   │   ├── prompts.py      # System prompts
│   │   ├── safety.py       # Safety checks
│   │   └── validator.py    # JSON validation
│   ├── clients/            # External API clients
│   ├── controllers/        # Request handlers
│   ├── dto/                # Data Transfer Objects
│   ├── llm/                # LLM providers (OpenAI, Ollama)
│   ├── memory/             # Session memory management
│   ├── models/             # Database models
│   ├── rag/                # RAG implementation
│   │   ├── ingest.py       # Document ingestion
│   │   ├── qa.py           # Question answering
│   │   └── retriever.py    # Vector retrieval
│   ├── routes/             # API routes
│   ├── services/           # Business logic
│   └── utils/              # Utility functions
├── data/
│   ├── chroma_db/          # ChromaDB vector store
│   ├── PDF/                # Source PDF documents
│   │   ├── meal/           # Nutrition PDFs
│   │   └── workout/        # Workout PDFs
│   └── profile/            # User profiles
├── migrations/             # Database migrations
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point
└── Dockerfile             # Docker configuration
```

## 🔧 Công nghệ sử dụng

- **Backend Framework**: Flask 3.1.2
- **Database**: MySQL (SQLAlchemy)
- **Vector Database**: ChromaDB
- **LLM**: OpenAI GPT / Ollama
- **Authentication**: Flask-JWT-Extended
- **RAG**: LangChain
- **Migration**: Flask-Migrate (Alembic)

## 📝 Ghi chú

- Dữ liệu RAG được lưu trữ trong `data/chroma_db/`
- Session memory được lưu trong `data/memory_store.json`
- User profiles được lưu trong `data/profile/`
- Logs LLM failures được ghi vào `data/llm_failures.log`

## 🔒 Bảo mật

- Sử dụng JWT để xác thực người dùng
- CORS được cấu hình cho các endpoint agent
- API keys được quản lý qua biến môi trường