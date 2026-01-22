---
description: Set up Git version control for the project
---

# Git Setup & Version Control Guide

This workflow will help you initialize Git, track changes, and access old versions of your files.

## Step 1: Initialize Git Repository

```bash
cd /home/lord/Projects/Rag_Agent
git init
```

This creates a `.git` folder that stores all your version history.

## Step 2: Configure Git (First Time Only)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Step 3: Create .gitignore File

This tells Git which files to ignore (secrets, dependencies, temporary files).

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/
.pytest_cache/

# Node.js
node_modules/
npm-debug.log
yarn-error.log

# Environment & Secrets
.env
*.log

# Database
*.db
*.sqlite

# WhatsApp Session Data
.wwebjs_auth/
.wwebjs_cache/

# Uploads & Data
uploads/*
!uploads/.gitkeep
data/*
!data/.gitkeep

# IDE
.vscode/
.idea/
*.swp
*.swo

# Docker
*.log

# OS
.DS_Store
Thumbs.db
EOF
```

## Step 4: Make Your First Commit

```bash
# Add all files (respects .gitignore)
git add .

# Create first commit
git commit -m "Initial commit: RAG Agent project"
```

## Step 5: Daily Workflow - Saving Updates

**When you make changes:**

```bash
# See what files changed
git status

# Add specific files
git add backend/app/services/rag_service.py frontend/src/pages/ChatPage.jsx

# OR add everything
git add .

# Commit with a descriptive message
git commit -m "Add: category image support in chat responses"
```

**Helpful commit message formats:**
- `Add: [new feature]`
- `Fix: [bug description]`
- `Update: [what changed]`
- `Refactor: [code improvement]`

## Step 6: View History & Access Old Files

**See all commits:**
```bash
git log --oneline --graph --all
```

**See what changed in a file:**
```bash
git log -p backend/app/services/rag_service.py
```

**Compare current vs old version:**
```bash
git diff HEAD~5 backend/app/services/rag_service.py
```

**Get a file from 5 commits ago:**
```bash
git show HEAD~5:backend/app/services/rag_service.py > old_version.py
```

**Restore a deleted file:**
```bash
git checkout <commit-hash> -- path/to/deleted/file.py
```

**Go back to a previous commit (temporary):**
```bash
git checkout <commit-hash>
# To return to latest:
git checkout main
```

## Step 7: Create Meaningful Checkpoints (Branches)

Before major changes, create a branch:

```bash
# Create and switch to new branch
git checkout -b feature/new-whatsapp-integration

# Make changes, commit...
git add .
git commit -m "Add: multi-session support"

# Switch back to main
git checkout main

# Merge the feature
git merge feature/new-whatsapp-integration
```

## Quick Reference

| Task | Command |
|------|---------|
| Save changes | `git add . && git commit -m "Message"` |
| View history | `git log` |
| See current changes | `git status` |
| Undo last commit (keep changes) | `git reset --soft HEAD~1` |
| Discard all changes | `git reset --hard HEAD` |
| Search commits | `git log --grep="search term"` |
| Show file at commit | `git show <commit>:path/to/file` |

## Pro Tips

1. **Commit often**: Every feature, bug fix, or significant change should be committed.
2. **Write clear messages**: Future you will thank you.
3. **Don't commit secrets**: Never commit `.env` files with API keys.
4. **Tag releases**: `git tag -a v1.0 -m "First release"`
