# Recipe Recommendation App - Windows Setup Guide

## Requirements
- Python 3.10+
- Android Studio (latest)
- Git (optional)

## 1. Backend Setup

1. Open a terminal (Command Prompt or PowerShell) and navigate to the `backend` folder.
2. Run the provided setup script:
    `start.bat`
   
   This will:
   - Create a virtual environment (`venv`) for you.
   - Install all required Python packages.
   - Start the server on `http://localhost:8000`.

   **Note:** If the script fails, you can do it manually:
   - `python -m venv venv`
   - `venv\Scripts\activate`
   - `pip install -r requirements.txt`
   - `uvicorn app.main:app --reload`

3. **API Key**: If you want advanced AI features (Gemini), open the newly created `.env` file and replace `your_key_here` with your Google Gemini API Key.

## 2. Frontend Setup (Android)

1. Open Android Studio.
2. Choose "Open Project" and select the `android` folder.
3. Wait for Gradle Sync to finish (bottom bar).
4. Connect an Android Emulator (API 30+) or a physical device.

   **For Physical Devices**:
   - Open `android/app/src/main/java/com/antigravity/food/api/RetrofitClient.kt`.
   - Update `BASE_URL` from logic relevant to `10.0.2.2` to your computer's local IP address (e.g., `http://192.168.1.5:8000/`).
   - Re-run the app.

## 3. Usage

- Point the camera at ingredients.
- The app will suggest two recipe styles: Authentic and Restaurant.
- Click "Dessert" in the style dropdown for sweet dishes!
