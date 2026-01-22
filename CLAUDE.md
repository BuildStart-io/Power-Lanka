# RAG Agent - Project Documentation

## Project Overview
AI-powered RAG (Retrieval Augmented Generation) SaaS platform for **Extension Tools Lanka (Hair Hub)** - a hair extension products company in Sri Lanka. The system provides intelligent product search and recommendation via web chat interface and WhatsApp integration.

**Default Language: Sinhala (සිංහල)** - All responses are in Sinhala unless user explicitly requests English.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.11+ / FastAPI |
| **Frontend** | React 18 + Vite + Tailwind CSS 4 |
| **LLM** | Google Gemini 2.5 Flash (`gemini-2.5-flash-preview-04-17`) |
| **Embeddings** | Google text-embedding-004 (768 dimensions) |
| **Vector DB** | Qdrant Cloud (free tier, 1GB) |
| **Database** | SQLite (conversation history, documents, WhatsApp sessions) |
| **WhatsApp** | whatsapp-web.js (Node.js 20 LTS required) |

---

## Project Structure

```
/home/lord/Projects/Rag_Agent/
├── backend/                    # Python FastAPI backend
│   ├── Dockerfile              # Python 3.11-slim image
│   ├── app/
│   │   ├── main.py             # FastAPI app entry + global exception handler
│   │   ├── config.py           # Pydantic settings
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py      # Pydantic models (Product, Chat, etc.)
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── documents.py    # Upload, list, delete documents
│   │   │   ├── chat.py         # RAG chat endpoints
│   │   │   └── whatsapp.py     # WhatsApp webhook handler
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── document_processor.py  # Excel/PDF/CSV parsing
│   │   │   ├── embedding_service.py   # Gemini embeddings
│   │   │   ├── rag_service.py         # Core RAG pipeline
│   │   │   ├── vector_store.py        # Qdrant operations
│   │   │   └── category_images.py     # Category-to-image mapping
│   │   ├── prompts/                   # YAML prompt templates
│   │   │   ├── __init__.py
│   │   │   ├── prompt_loader.py       # Load & format prompts
│   │   │   ├── categories.yaml        # Product categories
│   │   │   ├── system_prompt.yaml     # AI personality & rules
│   │   │   ├── first_message.yaml     # Welcome instructions (Sinhala default)
│   │   │   ├── returning_customer.yaml # Follow-up instructions
│   │   │   ├── off_topic.yaml         # Off-topic handling
│   │   │   ├── query_expand.yaml      # First message query expansion
│   │   │   └── query_rewrite.yaml     # Context-aware rewriting
│   │   └── database/
│   │       ├── __init__.py
│   │       └── database.py     # SQLite + SQLAlchemy models
│   └── requirements.txt
├── frontend/
│   ├── Dockerfile              # Multi-stage: Node 20 build + Nginx
│   ├── nginx.conf              # SPA routing + gzip + caching
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout.jsx      # Main layout wrapper
│   │   │   └── Sidebar.jsx     # Navigation sidebar
│   │   ├── pages/
│   │   │   ├── ChatPage.jsx    # Main chat interface
│   │   │   ├── DocumentsPage.jsx # Document management
│   │   │   ├── UploadPage.jsx  # File upload (drag-drop)
│   │   │   └── WhatsAppPage.jsx # WhatsApp session management
│   │   ├── services/
│   │   │   └── api.js          # Axios API client
│   │   ├── App.jsx             # Router setup
│   │   └── index.css           # Tailwind imports
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── vite.config.js
│   └── package.json
├── whatsapp-service/           # Node.js WhatsApp integration (Node 20 required!)
│   ├── index.js                # WhatsApp client + Express server
│   ├── Dockerfile              # Node 20 + Puppeteer/Chromium
│   ├── package.json
│   └── .env
├── docker-compose.yml          # Multi-service Docker orchestration
├── .dockerignore               # Docker build exclusions
├── .env.example                # Environment template for Docker
├── media/                      # Category images (9 images)
├── uploads/                    # Uploaded document files
├── data/                       # SQLite database (rag_agent.db)
├── venv/                       # Python virtual environment
├── .env                        # Environment variables
├── products.xlsx               # Original client data (matrix format)
├── products_normalized.xlsx    # Transformed data (134 products)
└── template_products.xlsx      # Excel template for uploads
```

---

## Language Configuration

### Default Language: Sinhala (සිංහල)

The AI assistant responds in **Sinhala Unicode** by default for ALL messages.

| User Input | Agent Response Language |
|------------|------------------------|
| "Hi" | සිංහල (Sinhala) |
| "Hello" | සිංහල (Sinhala) |
| "What products?" | සිංහල (Sinhala) |
| "Mata one beads" | සිංහල (Sinhala) |
| "ආයුබෝවන්" | සිංහල (Sinhala) |
| "Reply in English please" | English ✅ |
| "I can't read Sinhala" | English ✅ |

### Language Rules
- Default: Always respond in Sinhala Unicode (සිංහල)
- Switch to English: Only when user explicitly requests
- Never: Respond in Singlish (romanized Sinhala)
- Product names and prices: Can stay in English (*Keratin Iron*, *RS.4,500*)

---

## API Endpoints

### Documents
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/documents/upload` | POST | Upload Excel/PDF/CSV files |
| `/documents/` | GET | List all documents |
| `/documents/{id}` | GET | Get document details |
| `/documents/{id}` | DELETE | Delete document + vectors |
| `/documents/stats/collection` | GET | Qdrant collection stats |

### Chat
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat/` | POST | RAG chat with session history |
| `/chat/simple` | POST | Quick chat without history |
| `/chat/history/{session_id}` | GET | Get conversation history |
| `/chat/history/{session_id}` | DELETE | Clear history |

### WhatsApp
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/whatsapp/message` | POST | Handle incoming WhatsApp message |
| `/whatsapp/sessions` | GET | List all WhatsApp sessions |
| `/whatsapp/sessions/{phone}` | DELETE | Clear WhatsApp session |

### System
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check with Qdrant status |
| `/media/{filename}` | GET | Static media files |

---

## Database Schema

### SQLite Tables (data/rag_agent.db)

```sql
-- Uploaded documents tracking
Document:
  - id (String, PK)
  - filename, file_type, file_path
  - product_count, status
  - uploaded_at (DateTime)

-- Chat history
ConversationMessage:
  - id (String, PK)
  - session_id (String, indexed)
  - role ('user' | 'assistant')
  - content (Text)
  - created_at (DateTime)

-- WhatsApp sessions
WhatsAppSession:
  - id (String, PK)
  - phone_number (String, unique, indexed)
  - session_id (String)
  - created_at, last_message_at (DateTime)
```

---

## Prompt System

All prompts are stored in YAML files for easy editing without code changes.

### Prompt Files (`backend/app/prompts/`)

| File | Purpose | When Used |
|------|---------|-----------|
| `categories.yaml` | Product categories list | Every request |
| `system_prompt.yaml` | AI personality, rules, language settings | Every request |
| `first_message.yaml` | Welcome instructions (Sinhala default) | First message only |
| `returning_customer.yaml` | Follow-up instructions | 2nd+ messages |
| `off_topic.yaml` | Handle irrelevant questions | When off-topic detected |
| `query_expand.yaml` | Convert greeting to search query | First message only |
| `query_rewrite.yaml` | Add context to follow-up queries | 2nd+ messages |

### System Prompt Sections (`system_prompt.yaml`)

| Section | Description |
|---------|-------------|
| `role` | Sales assistant for Extension Tools Lanka |
| `personality` | Warm, helpful, WhatsApp-style (max 5 emojis) |
| `language_rules` | **Default Sinhala**, switch to English only if asked |
| `formatting` | WhatsApp formatting (*bold*, bullets) |
| `product_accuracy` | Never make up products/prices |
| `sales_techniques` | Cross-selling, order prompts |
| `common_scenarios` | Price objections, quality questions |

### Editing Prompts

To change AI behavior, edit the YAML files:

```yaml
# backend/app/prompts/system_prompt.yaml

language_rules: |
  ## LANGUAGE RULES - CRITICAL:

  **DEFAULT LANGUAGE: SINHALA (සිංහල)**

  - ALWAYS reply in Sinhala Unicode by default
  - ONLY switch to English if user explicitly asks
  ...
```

Restart backend to apply changes.

---

## RAG Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Message                                 │
│                        "Hi"                                      │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. Conversation State Detection                                 │
│     → is_first_message: True/False                               │
│     → message_count: 0, 1, 2...                                  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. Query Preparation                                            │
│     First message: query_expand.yaml → Gemini                    │
│        "Hi" → "popular hair extension products tools"            │
│     Follow-up: query_rewrite.yaml → Gemini                       │
│        "Meka kiyadada?" → "keratin iron price"                   │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. Vector Search (Qdrant)                                       │
│     → Query: expanded/rewritten query                            │
│     → Returns: Top-5 products (score >= 0.45)                    │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. Category Image Selection                                     │
│     → Only if NOT first message                                  │
│     → Only if result score >= 0.50                               │
│     → Most common category wins                                  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. Prompt Assembly (prompt_loader.py)                           │
│     → Load system_prompt.yaml (Sinhala default)                  │
│     → Load first_message.yaml OR returning_customer.yaml         │
│     → Load off_topic.yaml                                        │
│     → Inject: products, categories, history, query               │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. Gemini Generation                                            │
│     → Send assembled prompt                                      │
│     → Receive Sinhala response (default)                         │
│     → Fallback to backup API key on 429 errors                   │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  7. Response (in Sinhala by default)                             │
│     → response: "ආයුබෝවන්! Extension Tools Lanka වෙත..."         │
│     → sources: Retrieved products                                │
│     → category_image: /media/filename.jpeg (if applicable)       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Services Overview

### `rag_service.py` - Core RAG Pipeline
- Conversation state detection (first/returning)
- Query expansion for first messages
- Context-aware query rewriting (Sinhala → English for search)
- Dynamic prompt building from YAML
- Category image selection
- API fallback mechanism

### `vector_store.py` - Qdrant Operations
- Idempotent collection creation
- Batch vector upload (100 at a time)
- Cosine similarity search
- Score threshold filtering (0.45)
- Document deletion

### `embedding_service.py` - Gemini Embeddings
- text-embedding-004 (768 dimensions)
- Task-specific embeddings (document vs query)
- Automatic API fallback on rate limits

### `document_processor.py` - File Processing
- Excel, CSV, PDF, TXT support
- Flexible column mapping
- Price parsing (RS.3000 format)
- PDF/TXT chunking (500 words)

### `category_images.py` - Image Mapping
- Maps categories to product images
- Priority: sub_category > category
- 9 category images in /media/

---

## Environment Variables (.env)

```bash
# Gemini AI
GEMINI_API_KEY=your_api_key

# Qdrant Cloud
QDRANT_URL=https://xxx.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_key
QDRANT_COLLECTION_NAME=rag_products

# Directories
UPLOAD_DIR=uploads
DATA_DIR=data
MAX_FILE_SIZE_MB=5
```

---

## Running the Project

### Terminal 1: Backend (Python)
```bash
cd /home/lord/Projects/Rag_Agent
source venv/bin/activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2: Frontend (React)
```bash
cd /home/lord/Projects/Rag_Agent/frontend
npm run dev -- --host 0.0.0.0
```

### Terminal 3: WhatsApp Service (Node.js 20 Required!)
```bash
cd /home/lord/Projects/Rag_Agent/whatsapp-service
nvm use 20  # IMPORTANT: Must use Node 20, not Node 22
npm start
```

### WhatsApp Service - First Time Setup
```bash
cd /home/lord/Projects/Rag_Agent/whatsapp-service
nvm install 20
nvm use 20
rm -rf node_modules package-lock.json .wwebjs_auth .wwebjs_cache
npm install
npm start
# Scan QR code with WhatsApp
```

### WhatsApp Service - If Crashes
```bash
cd /home/lord/Projects/Rag_Agent/whatsapp-service
rm -rf .wwebjs_auth .wwebjs_cache
nvm use 20
npm start
# Re-scan QR code
```

### Access URLs
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **WhatsApp Health**: http://localhost:3000/health

---

## Docker Deployment

### Docker Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        docker-compose.yml                            │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │   rag-backend   │  │  rag-frontend   │  │  rag-whatsapp   │     │
│  │  Python 3.11    │  │  Nginx:alpine   │  │   Node 20-slim  │     │
│  │  FastAPI        │  │  Static SPA     │  │  Puppeteer      │     │
│  │  Port: 8000     │  │  Port: 80→5173  │  │  Port: 3000     │     │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘     │
│           │                    │                    │               │
│           ▼                    ▼                    ▼               │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      Volumes                                 │   │
│  │  ./data:/app/data  ./uploads:/app/uploads  ./media:/app/media│   │
│  │  whatsapp-auth:/app/.wwebjs_auth  whatsapp-cache:...         │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Docker Files Overview

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Orchestrates all 3 services |
| `backend/Dockerfile` | Python 3.11-slim + FastAPI |
| `frontend/Dockerfile` | Multi-stage: Node 20 build → Nginx |
| `frontend/nginx.conf` | SPA routing, gzip, static caching |
| `whatsapp-service/Dockerfile` | Node 20-slim + Chromium for Puppeteer |
| `.dockerignore` | Excludes venv, node_modules, .git, etc. |
| `.env.example` | Template for Docker environment variables |

### Quick Start with Docker

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env with your API keys
nano .env

# 3. Build and start all services
docker-compose up --build -d

# 4. View logs
docker-compose logs -f

# 5. Stop all services
docker-compose down
```

### Docker Commands Reference

```bash
# Build without starting
docker-compose build

# Start in foreground (see logs)
docker-compose up

# Start in background
docker-compose up -d

# Rebuild specific service
docker-compose up --build backend

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f whatsapp

# Stop and remove containers
docker-compose down

# Stop and remove with volumes (clears WhatsApp auth!)
docker-compose down -v

# Restart specific service
docker-compose restart backend

# Check service status
docker-compose ps

# Execute command in container
docker-compose exec backend bash
docker-compose exec whatsapp sh
```

### Environment Variables for Docker

Create `.env` file from `.env.example`:

```bash
# Gemini AI
GEMINI_API_KEY=your_gemini_api_key_here

# Qdrant Cloud
QDRANT_URL=https://your-cluster.cloud.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_NAME=rag_products

# Application Settings
MAX_FILE_SIZE_MB=5

# Frontend (for production, change to your domain)
VITE_API_URL=http://localhost:8000
```

### Docker Service Details

#### Backend (rag-backend)
- **Image**: Python 3.11-slim
- **Port**: 8000
- **Volumes**: `./data`, `./uploads`, `./media` (read-only)
- **Health check**: `curl http://localhost:8000/health`

#### Frontend (rag-frontend)
- **Image**: Multi-stage (Node 20 → Nginx:alpine)
- **Port**: 80 (mapped to 5173 externally)
- **Features**: Gzip compression, SPA routing, static asset caching
- **Depends on**: backend

#### WhatsApp (rag-whatsapp)
- **Image**: Node 20-slim + Chromium
- **Port**: 3000
- **Volumes**: Named volumes for auth persistence
- **Special**: `SYS_ADMIN` capability + seccomp disabled for Puppeteer
- **Depends on**: backend

### WhatsApp QR Code in Docker

```bash
# View WhatsApp logs to see QR code
docker-compose logs -f whatsapp

# If you need to re-authenticate (clears WhatsApp session)
docker-compose down
docker volume rm rag_agent_whatsapp-auth rag_agent_whatsapp-cache
docker-compose up -d
docker-compose logs -f whatsapp
# Scan new QR code
```

### Production Considerations

1. **Change CORS origins** in `backend/app/main.py` (currently allows all)
2. **Update VITE_API_URL** to your production backend URL
3. **Use secrets management** instead of `.env` for API keys
4. **Add HTTPS** with reverse proxy (Traefik/Caddy/nginx-proxy)
5. **Persistent volumes** for data, uploads, and WhatsApp auth

---

## Product Data Model

### Excel Columns (products_normalized.xlsx)
| Column | Description |
|--------|-------------|
| category | Main category (Extension Tools, Human Hair Bundles) |
| sub_category | Sub-category (Pliers, Irons, etc.) |
| sub_sub_category | Type/variant |
| product_name | Product name |
| variant | Color, size variant |
| size_weight | Size or weight |
| price_lkr | Price in LKR (RS.XXXX) |
| description | Product description |
| available | Yes/No |
| tags | Search tags |

### Client Data
- **Business**: Extension Tools Lanka (Hair Hub)
- **Products**: 134 items
- **Categories**: Extension Tools, Human Hair Bundles, Other
- **Price format**: LKR (RS.XXXX)

---

## Category Images (media/)

| Image | Mapped Categories |
|-------|-------------------|
| micro & nano beads catogary.jpeg | beads, micro, nano, rings |
| Extension pilers Catogary.jpeg | pliers, extension pliers |
| Extension Irons catogary.jpeg | irons, keratin iron, flat iron |
| Extension 6D machine Catogary.jpeg | machines, 6d machine |
| keratun glue catogary.jpeg | glue, keratin glue, adhesive |
| Hair Extension Tools Catogary.jpeg | extension tools (fallback) |
| human hair price.jpeg | human hair, bundles |

---

## Key Design Decisions

1. **No LangChain** - Custom RAG pipeline for simplicity and control
2. **Single LLM Provider** - Gemini for both generation and embeddings
3. **Qdrant Cloud** - Free tier (1GB) vector database
4. **SQLite** - Lightweight, no auth needed for MVP
5. **YAML Prompts** - Easy editing without code changes
6. **Complete History** - Entire conversation stored per session
7. **Score Thresholds** - 0.45 for retrieval, 0.50 for image display
8. **API Fallback** - Automatic backup key on rate limits
9. **First Message Detection** - Welcome + answer on first contact
10. **Off-Topic Handling** - Politely redirect irrelevant questions
11. **Default Sinhala** - All responses in Sinhala unless English requested
12. **Node 20 for WhatsApp** - Required for whatsapp-web.js compatibility

---

## Error Handling

### Backend (main.py)
- Global exception handler catches all unhandled errors
- Returns structured JSON: `{"error": "message", "error_code": "INTERNAL_ERROR"}`
- Logs full traceback with error ID

### RAG Service
- API rate limit fallback to backup key
- Graceful degradation on Gemini failures
- User-friendly error messages

### WhatsApp Service
- Sends error message to user on failures
- Message deduplication (last 100)
- Typing indicator cleanup
- Requires Node.js 20 (Node 22 causes Puppeteer crashes)

---

## Project Phases

- [x] **Phase 1**: Backend + Document Processing + RAG Pipeline
- [x] **Phase 2**: Frontend Dashboard (React + Tailwind)
- [x] **Phase 3**: WhatsApp Integration (whatsapp-web.js)
- [x] **Phase 4**: Docker setup (docker-compose with all 3 services)
- [ ] **Phase 5**: Multi-tenancy features

---

## Code Statistics

- **Python Code**: ~1,700 lines across 18 modules
- **React Code**: ~600 lines across 8 components
- **Node.js Code**: ~200 lines in WhatsApp service
- **YAML Prompts**: 7 template files
- **Docker**: 3 Dockerfiles + docker-compose.yml + nginx.conf
- **Total Files**: 130+ files

---

## Quick Reference

### Add New Product Category
1. Edit `backend/app/prompts/categories.yaml`
2. Add image to `media/` folder
3. Update `backend/app/services/category_images.py`

### Change AI Personality
1. Edit `backend/app/prompts/system_prompt.yaml`
2. Restart backend

### Change Welcome Message
1. Edit `backend/app/prompts/first_message.yaml`
2. Restart backend

### Change Default Language
1. Edit `backend/app/prompts/system_prompt.yaml` → `language_rules`
2. Edit `backend/app/prompts/first_message.yaml`
3. Edit `backend/app/prompts/returning_customer.yaml`
4. Restart backend

### Add Off-Topic Response
1. Edit `backend/app/prompts/off_topic.yaml`
2. Add example response
3. Restart backend

### Fix WhatsApp Crashes
```bash
cd /home/lord/Projects/Rag_Agent/whatsapp-service
rm -rf .wwebjs_auth .wwebjs_cache
nvm use 20
npm start
```
