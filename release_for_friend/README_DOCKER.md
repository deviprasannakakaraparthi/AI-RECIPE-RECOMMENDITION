# Running the AI Recipe Backend with Docker

This allows you to run the backend on any machine (Windows, Mac, or Linux) with Docker installed, without manually setting up Python environments.

## Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

## How to Build and Run

1. **Open your terminal** (PowerShell, Command Prompt, or Terminal).
2. **Navigate to the project root folder**.
3. **Build and start the container**:
   ```bash
   docker-compose up --build
   ```

The backend will be available at `http://localhost:8000`.

## Testing the API
You can check if it's running by visiting:
`http://localhost:8000/health`

## Note for Android Development
- **Using Emulator**: Point your Android app to `http://10.0.2.2:8000`.
- **Using Physical Device**: Point your Android app to `http://YOUR_COMPUTER_IP:8000`.

## Environment Variables
If you want to use Google Gemini for premium recipe generation, add your API key to the `backend/.env` file:
```env
GOOGLE_API_KEY=your_key_here
```
