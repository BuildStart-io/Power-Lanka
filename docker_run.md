# Docker Operation Guide for PowerLanka Server

This guide details all necessary commands to build, run, and manage the PowerLanka server using Docker.

## 1. Prerequisites

- **Docker** and **Docker Compose** installed on the server.
- **Git** (to pull the latest code).
- **.env file** configured (see below).

## 2. Initial Setup

### 2.1 Clone/Pull Repository

```bash
git pull origin main
```

### 2.2 Configure Environment

Ensure your `.env` file exists in the project root (`PL_Server/`).

```bash
# Copy example if not exists
cp .env.example .env

# Edit .env with your actual keys
nano .env
```

**Required Variables in `.env`:**

- `OPENROUTER_API_KEY` (For AI features)
- `QDRANT_URL` & `QDRANT_API_KEY` (Vector DB)
- `WASENDER_TOKEN` & `WASENDER_API_URL` (WhatsApp Integration)

## 3. Main Commands

### 3.1 Build and Start (Detached Mode)

The standard command to start the server in the background.

```bash
docker compose up -d --build
```

- `--build`: Forces a rebuild of images (useful after code changes).
- `-d`: Detached mode (runs in background).

### 3.2 Stop All Services

Stops running containers.

```bash
docker compose down
```

### 3.3 View Logs

Monitor the output of all services.

```bash
docker compose logs -f
```

- `-f`: Follow log output.

**View specific service logs:**

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

### 3.4 Restart Services

Restart to apply config changes.

```bash
docker compose restart
```

## 4. Advanced & Utility Commands

### 4.1 CLI Chat Tool (Interactive)

**Option A: Run inside Docker (Recommended)**
No setup required.

```bash
docker compose exec backend python cli_chat.py
```

**Option B: Run Locally**
If you have Python installed on your machine:

1. Ensure dependencies are installed: `pip install requests`
2. Run the script:

```bash
python3 utilities/dev_tools/cli_chat.py
```

*Note: The backend server must be running (`docker compose up`) for this to work.*

### 4.2 Database Maintenance (Shell Access)

Access the running backend container's shell.

```bash
docker compose exec backend bash
```

*Inside the container, you can run Python scripts or inspect the `data/` folder.*

### 4.3 Rebuild Single Service

If you only modified the backend code:

```bash
docker compose up -d --build backend
```

### 4.4 Prune Docker System

Clean up unused images, networks, and build cache (frees up space).

```bash
docker system prune -a
```

## 5. Troubleshooting

**Check container status:**

```bash
docker ps -a
```

**Check service health:**
The containers have health checks configured.

- `healthy`: Service is running and responding.
- `unhealthy`: Service failed its health check.

**Rebuild from scratch (Clean Slate):**

```bash
docker compose down
docker system prune -f
docker compose build --no-cache
docker compose up -d
```
