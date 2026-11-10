# GitHub Setup Guide

Follow these steps to push your project to GitHub under `lulhannes2` account.

---

## Step 1: Create Repository on GitHub

1. Go to https://github.com/new
2. Login with `lulhannes2@github`
3. **Repository name**: `gemma-performance-test`
4. **Description**: "Gemma 2 LLM performance testing on DGX A100"
5. **Visibility**: Private (for now, can make public later)
6. **Don't initialize** with README (we have one already)
7. Click **Create repository**

---

## Step 2: Setup Git Locally

On `dgx43019`:

```bash
# Enter project directory
cd /path/to/gemma-performance-test

# Initialize git (if not already done)
git init

# Configure git
git config user.name "lulhannes2"
git config user.email "your-email@example.com"

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: Gemma inference server & performance testing framework"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/lulhannes2/gemma-performance-test.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## Step 3: SSH Setup (Optional, Recommended)

For password-less push/pull:

```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "lulhannes2@github"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub:
# 1. Go to https://github.com/settings/keys
# 2. Click "New SSH key"
# 3. Paste the content
# 4. Click "Add SSH key"

# Test connection
ssh -T git@github.com

# Update remote to use SSH (optional)
git remote set-url origin git@github.com:lulhannes2/gemma-performance-test.git
```

---

## Step 4: Verify Setup

```bash
# Check remote
git remote -v
# Should show: origin  https://github.com/lulhannes2/gemma-performance-test.git

# Check status
git status
# Should show: On branch main, nothing to commit

# View logs
git log --oneline
# Should show your initial commit
```

---

## Step 5: Daily Workflow

### Before starting work:
```bash
git pull origin main
```

### After making changes:
```bash
# Add changes
git add .

# Commit
git commit -m "Descriptive message of what changed"

# Push
git push origin main
```

---

## Step 6: Branching (Optional, Advanced)

For collaborative work:

```bash
# Create feature branch
git checkout -b feature/us-001-model-deployment

# Work on branch...
git add .
git commit -m "US-001: Add Gemma 26B model loading"

# Push branch
git push origin feature/us-001-model-deployment

# On GitHub: Create Pull Request
# After review: Merge to main

# Update main locally
git checkout main
git pull origin main
```

---

## Troubleshooting

### "fatal: No url found for remote"
```bash
# Fix
git remote add origin https://github.com/lulhannes2/gemma-performance-test.git
```

### "Permission denied (publickey)"
```bash
# Use HTTPS instead of SSH
git remote set-url origin https://github.com/lulhannes2/gemma-performance-test.git
```

### "refused to merge unrelated histories"
```bash
git pull origin main --allow-unrelated-histories
```

---

## Files that Will Be Ignored

Due to `.gitignore`:
- `logs/` - Too large, generated per-run
- `huggingface_cache/` - Model files (100GB+)
- `.venv/` - Virtual environment
- `*.log` - Log files
- `.env` - Secrets

You can fetch these from other sources or regenerate them locally.

---

## Working Remotely from Laptop

Once pushed to GitHub, you can clone on your laptop:

```bash
# Clone
git clone https://github.com/lulhannes2/gemma-performance-test.git

# Pull latest changes
cd gemma-performance-test
git pull origin main

# Push your changes
git add .
git commit -m "Your change"
git push origin main
```

---

## Protected Branches (Optional)

To prevent accidental pushes to main:

1. Go to GitHub repo → Settings → Branches
2. Add rule for `main`
3. Require pull request reviews before merge

---

**Ready to push?** ☕ Enjoy your coffee, then run:

```bash
git add .
git commit -m "Initial commit: Gemma inference server & perf testing"
git push -u origin main
```

✅ Done!
