# How to Run Power Lanka Manually (No Docker)

Follow these steps to run the Backend, Frontend, and WhatsApp service manually in separate terminals.

## Prerequisites

- Python 3.10+
- Node.js 18+
- SQLite (built-in)

---

## 1. Backend (FastAPI)

**Terminal 1:**

```bash
cd backend
# Create/Activate Virtual Environment (Recommended)
python3 -m venv venv
source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt

# Run Server
python3 main.py
```

*Server will run on: `http://localhost:8000`*

---

## 2. WhatsApp Service (Node.js)

**Terminal 2:**

```bash
cd whatsapp-service
# Install Dependencies
npm install

# Run Service
npm start
```

*Service will run on: `http://localhost:4000`*
*(You will see a QR code to scan if not already logged in)*

---

## 3. Frontend (Vue.js)

**Terminal 3:**

```bash
cd frontend
# Install Dependencies
npm install

# Run Dev Server
npm run dev
```

*App will run on: `http://localhost:5173`*

---

## 4. Qdrant (Vector DB)

Since you are running manually, you have two options:

1. **Use Cloud Qdrant:** Ensure your `.env` has `QDRANT_URL` and `QDRANT_API_KEY` set to a cloud instance.
2. **Run Qdrant via Docker (Just DB):**

    ```bash
    docker run -p 6333:6333 qdrant/qdrant
    ```

    Then set `QDRANT_URL=http://localhost:6333` in `.env`.

---

## Troubleshooting

- **Port Conflicts:** Ensure ports 8000, 4000, and 5173 are free.
- **Environment Variables:** Make sure the `.env` file in the root directory is correctly loaded by the backend (it should be automatically).

---

## 5. Running Utility Scripts

All helper scripts are located in categorized subdirectories within `utilities`. You can run them directly:

```bash
cd utilities

# Admin Scripts
# Example: Create an admin user
python3 admin_management/create_admin_user.py

# Database Tools
# Example: Check DB schema
python3 database_maintenance/check_schema.py

# Dev Tools
# Example: Interactive CLI Chat
python3 dev_tools/cli_chat.py
```

**Note:** These scripts have been updated to automatically resolve the backend/app paths regardless of their location.
