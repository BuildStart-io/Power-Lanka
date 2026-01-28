#!/bin/bash
# view_logs.sh - Tail logs from all services with formatting

echo "🔍 Tailing logs for Power Lanka RAG System..."
echo "Use Ctrl+C to exit."
echo "---------------------------------------------------"

# simple docker compose logs command
docker compose logs -f --tail=100
