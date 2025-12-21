## Sơ đồ kiến trúc RAG cho tính năng tạo lịch tập & meal-plan

Dưới đây là sơ đồ tổng quan (Mermaid) mô tả luồng dữ liệu và các thành phần chính khi triển khai RAG cho việc sinh lịch tập và meal-plan.

```mermaid
graph LR
  UI[User UI / Web App]
  API[API Server\n(Flask / FastAPI)]
  Agent[Agent / Planner]
  Retriever[Retriever]
  VectorDB[Vector DB\n(Chroma / FAISS / Milvus)]
  Embedding[Embedding Service\n(sentence-transformers / OpenAI)]
  Ingest[Ingest Worker]
  LLM[LLM\n(OpenAI / Ollama)]
  Validator[Validator / Safety Checks]
  Storage[User Profiles & Memory\n(data/...)]
  Scheduler[Scheduler / Re-index]
  Monitoring[Monitoring / Logging]

  UI -->|HTTP / WebSocket| API
  API -->|calls| Agent
  Agent -->|retrieval request| Retriever
  Retriever -->|k-NN| VectorDB
  VectorDB -->|metadata + vectors| Retriever
  Agent -->|generation request| LLM
  LLM -->|generated plan| Agent
  Agent -->|validate plan| Validator
  Validator -->|ok / issues| Agent
  Agent -->|response| API --> UI

  Ingest -->|documents| Embedding
  Embedding -->|vectors| VectorDB
  Scheduler -->|periodic jobs| Ingest
  Storage -->|profiles & history| Agent

  Monitoring --> API
  Monitoring --> VectorDB
  Monitoring --> LLM
```

**Luồng chung (step-by-step)**
- Người dùng gửi yêu cầu tạo lịch (UI → `API`).
- `API` chuyển yêu cầu tới `Agent/Planner` kèm `user_profile` và các constraint.
- `Agent` gọi `Retriever` để lấy các chunk có liên quan từ `Vector DB` (kết quả từ `Ingest` + `Embedding`).
- `Agent` ghép context truy xuất, prompt template và gọi `LLM` để sinh kế hoạch.
- Kết quả được kiểm tra bởi `Validator` (an toàn, calorie, allergies, equipment).
- Nếu hợp lệ, `Agent` trả kết quả (có `sources` dẫn chứng) về `API` và hiển thị cho user; nếu không, yêu cầu sửa/clarify.

**Mô tả thành phần & gợi ý kỹ thuật**
- **UI / API**: Web UI hoặc frontend gọi API (gợi ý: tích hợp vào `app/routes/routes.py`).
- **Agent / Planner**: Điều phối retrieval + generation + validation (gợi ý file: `app/agent/planner.py`).
- **Retriever**: wrapper cho tìm kiếm vector + re-rank theo tags (tạo `rag/retriever.py`).
- **Vector DB**: lưu vectors + metadata. Dev: `chromadb` hoặc `faiss-cpu`; Prod: `milvus` / `weaviate`.
- **Embedding Service**: `sentence-transformers` (dev offline) hoặc OpenAI embeddings (cloud). Tạo pipeline ingest ở `rag/ingest.py`.
- **Ingest Worker**: xử lý chunking metadata, upsert vectors vào Vector DB (tự động hoặc batch).
- **LLM**: dùng client hiện có `llm/openai_client.py` hoặc `llm/ollama_client.py` (gọi qua `llm/factory.py`).
- **Validator / Safety**: tái sử dụng `app/agent/validator.py` để kiểm tra dietary constraints, exercise safety, calorie targets.
- **Storage**: user data và lịch sử: `data/profile/user_profile.json`, `data/memory_store.json`, `data/profile/training_state.json`.
- **Scheduler / Monitoring**: cron jobs để re-index, logging cho truy vấn/retrieval/LLM latency và validation failures.

**Đầu việc tiếp theo gợi ý (quick wins)**
- Tạo `rag/ingest.py` để index toàn bộ `data/` vào Chroma/FAISS.
- Tạo `rag/retriever.py` + `rag/qa.py` để Agent dễ gọi RAG.
- Viết prompt template trả về JSON có field `plan`, `grocery_list`, `daily_calories`, `sources`, `issues`.

---
Tài liệu này là điểm khởi đầu để triển khai RAG trong repo hiện tại; bạn muốn tôi tiếp tục với việc nào (tạo script ingest, retriever, hoặc tích hợp vào `planner`)?
