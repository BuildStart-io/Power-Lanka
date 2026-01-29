# Power Lanka - AI WhatsApp Sales Agent

An intelligent WhatsApp-based sales assistant for Power Lanka Home Care Solutions. Features AI-powered product recommendations, order management, and an admin dashboard.

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     WASender    │────▶│    Backend      │────▶│    Qdrant       │
│    (External)   │     │    (FastAPI)    │     │    (Vector DB)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        ▲                       │
        │                       ▼
        │               ┌─────────────────┐
        │               │   Dashboard     │
        └───────────────│    (Vue.js)     │
                        └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker (optional)

### Manual Setup

**1. Backend (FastAPI)**

```bash
cd backend
pip install -r requirements.txt
python3 main.py
```

**3. Frontend Dashboard**

```bash
cd frontend
npm install
npm run dev
```

### Docker Setup

```bash
docker compose up -d
```

## 🔧 Environment Variables

Create a `.env` file in the root directory:

```env
# AI Model
GEMINI_API_KEY=your_gemini_api_key
OPENROUTER_API_KEY=your_openrouter_api_key

# Vector Database
QDRANT_URL=https://your-qdrant-instance.cloud
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION_NAME=power-lanka

# WhatsApp
BACKEND_URL=http://localhost:8000
```

## 📁 Project Structure

```
├── backend/           # FastAPI server + AI agent
│   ├── app/
│   │   ├── agent/     # AI tools and processing
│   │   ├── database/  # SQLite models
│   │   ├── prompts/   # YAML prompt templates
│   │   ├── routers/   # API endpoints
│   │   └── services/  # RAG, embeddings, vector store
│   └── data/          # SQLite database (rag_agent.db)
├── frontend/          # Vue.js admin dashboard
├── utilities/         # Maintenance scripts
│   ├── admin_management/    # User creation scripts
│   ├── database_maintenance/ # Schema checks & migrations
│   ├── vector_db/           # Qdrant management
│   ├── data_scripts/        # Seeding products/data
│   └── testing_verification/ # Testing tools
└── docker-compose.yml
```

## 🛠️ Features

- **AI Sales Assistant**: Natural language product discovery and ordering
- **Multi-language Support**: Sinhala (default) and English
- **Order Management**: Cart, shipping, payment (COD/Bank Transfer)
- **Admin Dashboard**:
  - 📊 Real-time Sales Stats
  - 📝 Manual Order Creation
  - 📥 CSV Export for Reporting
  - 🛍️ Product Management
- **Vector Search**: Semantic product search via Qdrant

## 🧰 Maintenance

You can run maintenance scripts directly from the `utilities` folder:

```bash
cd utilities
python3 admin_management/create_admin_user.py
python3 database_maintenance/check_schema.py
python3 dev_tools/cli_chat.py
```

## 📝 License

MIT
