# Streamlit Community Cloud Deployment Guide

This guide will help you deploy the Maintenance Management System to Streamlit Community Cloud.

## Prerequisites

✅ Git repository initialized (Done)  
✅ Streamlit configuration files created (Done)  
⚠️ GitHub repository needs to be created  
⚠️ Code needs to be pushed to GitHub  

## Step 1: Create GitHub Repository

Since the repository doesn't exist yet on GitHub, you need to create it first:

1. **Go to GitHub** and log in: [https://github.com/new](https://github.com/new)

2. **Create new repository:**
   - **Repository name**: `mmsmanagement`
   - **Description**: "Maintenance Management System - Streamlit web app for asset tracking, work orders, and inspections"
   - **Visibility**: Choose **Public** (required for free Streamlit Community Cloud)
   - **⚠️ IMPORTANT**: Do NOT initialize with README, .gitignore, or license

3. **Click "Create repository"**

## Step 2: Push Your Code to GitHub

After creating the repository on GitHub, run these commands:

```bash
# Verify your remote is set (should show your GitHub URL)
git remote -v

# Push your code to GitHub
git push -u origin main
```

If you get an authentication error, you'll need a Personal Access Token:
- Go to: [https://github.com/settings/tokens](https://github.com/settings/tokens)
- Click "Generate new token" → "Generate new token (classic)"
- Select scopes: `repo` (full control)
- Copy the token and use it as your password when pushing

## Step 3: Deploy to Streamlit Community Cloud

1. **Go to Streamlit Community Cloud**
   - Visit: [https://share.streamlit.io/](https://share.streamlit.io/)
   - Sign in with your GitHub account

2. **Create New App**
   - Click "New app" button
   - You'll see a form with three fields:

3. **Configure Deployment**
   - **Repository**: Select `SandyMuir/mmsmanagement`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - Click "Deploy!"

4. **Wait for Deployment**
   - Streamlit will install dependencies (takes 2-5 minutes)
   - You'll see the build logs in real-time
   - Once complete, your app will be live!

## Step 4: Your App URL

Your app will be available at:
```
https://[your-app-name]-[random-string].streamlit.app
```

You can customize this URL in the Streamlit Cloud settings.

## Files Configured for Streamlit Cloud

### ✅ `.streamlit/config.toml`
- Theme colors and styling
- Server configuration
- Browser settings

### ✅ `packages.txt`
- System dependencies (build-essential)

### ✅ `requirements.txt`
- Python package dependencies
- All necessary libraries for the app

## Important Notes for Cloud Deployment

### 🗄️ Database
- Streamlit Community Cloud uses **ephemeral storage**
- Your SQLite database will reset when the app restarts/redeploys
- For production, consider:
  - Using a cloud database (PostgreSQL, MySQL)
  - Or accepting that data is temporary

### 📁 File Storage
- Document uploads will also be ephemeral
- Consider using cloud storage (AWS S3, Google Cloud Storage) for production

### 🔒 Secrets Management
If you need to store sensitive information (API keys, passwords):

1. In Streamlit Cloud dashboard, go to your app settings
2. Click "Secrets" in the left menu
3. Add secrets in TOML format:

```toml
[database]
connection_string = "postgresql://..."

[api_keys]
google_maps_key = "your-key-here"
```

4. Access in your code:
```python
import streamlit as st
api_key = st.secrets["api_keys"]["google_maps_key"]
```

### 📊 Resource Limits (Free Tier)
- **RAM**: 1 GB
- **CPU**: Shared
- **Bandwidth**: Limited
- Apps sleep after inactivity

## Customization After Deployment

### Change App Name/URL
1. Go to your app settings in Streamlit Cloud
2. Navigate to "General" settings
3. Update the app name

### Update Environment Variables
1. Go to app settings
2. Click "Secrets"
3. Add/modify TOML configuration

### Reboot App
If your app has issues:
1. Go to app settings
2. Click "Reboot app"

## Updating Your App

When you push changes to your GitHub repository:

```bash
git add .
git commit -m "Your changes"
git push
```

Streamlit Cloud will **automatically detect and redeploy** your app!

## Troubleshooting

### Build Fails
- Check the logs in Streamlit Cloud
- Verify all dependencies in `requirements.txt`
- Ensure `packages.txt` includes system dependencies

### App Crashes
- Check "Manage app" → "Logs" in Streamlit Cloud
- Common issues:
  - Missing dependencies
  - File path issues
  - Database connection problems

### Authentication Issues with GitHub
```bash
# Use Personal Access Token instead of password
# Generate at: https://github.com/settings/tokens
```

### App is Slow
- Free tier has limited resources
- Consider upgrading to Streamlit Cloud paid tier
- Or deploy to your own server using Docker

## Alternative Deployment Options

If Streamlit Community Cloud doesn't meet your needs:

### 1. Streamlit Cloud (Paid)
- More resources
- Custom domains
- Better performance
- Pricing: [https://streamlit.io/cloud](https://streamlit.io/cloud)

### 2. Self-Hosted with Docker
- Full control over resources
- Persistent storage
- See `DOCKER_README.md` for instructions

### 3. Other Cloud Platforms
- **Heroku**: Good for production apps
- **AWS EC2/ECS**: Full control
- **Google Cloud Run**: Containerized deployment
- **Azure**: Enterprise solutions

## Monitoring Your App

In Streamlit Cloud dashboard:
- **Analytics**: View usage statistics
- **Logs**: Monitor errors and performance
- **Settings**: Configure app behavior

## Costs

**Streamlit Community Cloud (Free Tier):**
- ✅ Free for public repositories
- ✅ Unlimited public apps
- ⚠️ Limited resources
- ⚠️ Apps sleep after inactivity

**Paid Plans:**
- Private apps
- More resources
- Custom domains
- Priority support

## Next Steps

1. ✅ Create GitHub repository
2. ✅ Push code to GitHub
3. ✅ Deploy to Streamlit Cloud
4. 🔄 Test the deployed app
5. 📊 Monitor usage and performance
6. 🚀 Share the URL with users!

## Support

- **Streamlit Docs**: [https://docs.streamlit.io/](https://docs.streamlit.io/)
- **Community Forum**: [https://discuss.streamlit.io/](https://discuss.streamlit.io/)
- **GitHub Issues**: Report bugs in your repository

---

**Ready to deploy?** Follow the steps above and your app will be live in minutes! 🚀

