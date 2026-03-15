# Deployment Guide (Railway / Production)

Follow these steps to deploy your application to a permanent cloud host like **Railway**, **Render**, or **DigitalOcean**.

## 1. Prerequisites
- A GitHub account.
- A Railway account (free tier works great).

## 2. Setup your GitHub Repository
1. Initialize a git repository in your project root:
   ```bash
   git init
   git add .
   git commit -m "Prepare for production"
   ```
2. Create a new PRIVATE repository on GitHub and push your code there.

## 3. Deploy to Railway
1. Go to [Railway.app](https://railway.app) and log in.
2. Click **"New Project"** -> **"Deploy from GitHub repo"**.
3. Select your repository.

## 4. Configure Environment Variables
In the Railway dashboard, go to the **Variables** tab for your service and add:
- `GOOGLE_API_KEY`: Your Gemini API key.
- `PORT`: 8000 (Railway usually sets this automatically).

## 5. What this setup does:
I have configured a **multi-stage Docker build** in the root:
- **Phase 1**: It automatically installs the Flutter SDK and builds your Web App.
- **Phase 2**: It sets up the Python backend, installs AI models, and configures ImageMagick for video generation.
- **Phase 3**: It bundles both together. The backend will serve the frontend on the same URL!

### Benefits:
- **Permanent URL**: No more localtunnel links that expire.
- **Stability**: Cloud servers have much more bandwidth than a local tunnel.
- **Unified**: You only have ONE link for both the website and the API.

---
**Note**: The first deployment might take 5-10 minutes because building the Flutter web app and downloading AI models takes time. Once ready, you will get a permanent `xxx.up.railway.app` link!
