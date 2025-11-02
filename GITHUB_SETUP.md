# GitHub Repository Setup Guide

## Step 1: Create a New Repository on GitHub

1. Go to [GitHub](https://github.com) and log in to your account
2. Click the **"+"** icon in the top-right corner
3. Select **"New repository"**
4. Fill in the repository details:
   - **Repository name**: `mmsmanagement` (or your preferred name)
   - **Description**: "Maintenance Management System with Streamlit - Asset tracking, work orders, inspections, and Google Earth integration"
   - **Visibility**: Choose **Public** or **Private** based on your preference
   - **⚠️ IMPORTANT**: Do NOT initialize with README, .gitignore, or license (we already have these locally)
5. Click **"Create repository"**

## Step 2: Connect Your Local Repository to GitHub

After creating the repository, GitHub will show you the URL. Use the commands below to connect your local repository:

### Option A: Using HTTPS (Recommended for most users)

```bash
# Set the main branch name to 'main' (GitHub's default)
git branch -M main

# Add your GitHub repository as the remote origin
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push your code to GitHub
git push -u origin main
```

### Option B: Using SSH (If you have SSH keys configured)

```bash
# Set the main branch name to 'main'
git branch -M main

# Add your GitHub repository as the remote origin
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git

# Push your code to GitHub
git push -u origin main
```

**Note**: Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual GitHub username and repository name.

## Step 3: Verify the Push

After running the push command:
1. Refresh your GitHub repository page
2. You should see all your files uploaded
3. The README.md will be displayed on the repository home page

## Future Updates

After the initial setup, to push changes to GitHub:

```bash
# Stage your changes
git add .

# Commit your changes
git commit -m "Description of your changes"

# Push to GitHub
git push
```

## Useful Git Commands

```bash
# Check status of your files
git status

# View commit history
git log --oneline

# Pull latest changes from GitHub
git pull

# View configured remotes
git remote -v

# Create a new branch
git checkout -b feature-branch-name

# Switch between branches
git checkout branch-name
```

## What's Already Done

✅ Git repository initialized  
✅ .gitignore file created (excludes venv, __pycache__, data, etc.)  
✅ Initial commit created with 37 files  
✅ Ready to push to GitHub

## Repository Contents

Your repository includes:
- Main application (`app.py`)
- All module files (asset management, work orders, inspections, reporting)
- Configuration and settings files
- Docker deployment files
- Documentation (README, guides)
- Requirements.txt

## Files Excluded by .gitignore

The following are NOT pushed to GitHub (as they should be):
- Virtual environment (`venv/`)
- Python cache (`__pycache__/`)
- Database files (`*.db`, `*.sqlite`)
- KML export files
- Temporary files and logs
- Data directory contents

## Security Notes

⚠️ **Before pushing to a public repository**:
- Review `config.ini` for sensitive information
- If it contains passwords, API keys, or sensitive data, add it to `.gitignore`
- Consider using environment variables for sensitive configuration
- Remove any hardcoded credentials from the code

## Need Help?

If you encounter authentication issues:
- For HTTPS: GitHub will prompt for your username and Personal Access Token (PAT)
- To create a PAT: Go to GitHub Settings → Developer settings → Personal access tokens → Generate new token
- For SSH: You'll need to set up SSH keys first

---

**Ready to proceed?** Follow Step 1 to create your GitHub repository, then come back to run the commands in Step 2!

