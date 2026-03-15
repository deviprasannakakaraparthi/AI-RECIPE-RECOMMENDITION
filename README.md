# Recipe Recommender App

This project consists of a Python FastAPI backend and an Android Kotlin application.

## 1. Backend Setup (Python)

The backend uses YOLOv8 for ingredient detection, Sentence Transformers for matching, and Flan-T5 for generating instructions.

### Prerequisites
- Python 3.9+
- pip

### Installation & Running
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a clean virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   # Unset PYTHONPATH to ensure no conflict with global version
   unset PYTHONPATH
   pip install -r requirements.txt
   ```
4. Run the server:
   ```bash
   unset PYTHONPATH
   python3 main.py
   ```
   *The server will start at `http://0.0.0.0:8000`. On the first run, it will download necessary AI models.*

### 🚀 What's New
- **Zero-Shot Ingredient Detection**: Using OpenAI's CLIP, the app can now identify 60+ specific ingredients, including many Indian vegetables like Paneer, Brinjal, and Bitter Gourd.
- **40,000 Recipe Database**: We've switched from weak AI generation to a massive database of real, high-quality recipes. Your instructions will always be detailed and authentic.
- **Semantic Search**: Using Sentence-Transformers, the app finds recipes that truly match your ingredients and cuisine preference.

## 🛠️ Configuration
To get even BETTER ingredient identification (human-level), you can use Google's Gemini AI:
1. Get an API Key from [Google AI Studio](https://aistudio.google.com/).
2. Create a `.env` file in the `backend/` directory:
   ```env
   GOOGLE_API_KEY=your_key_here
   ```
3. The app will automatically switch to Gemini for "Perfect" detection.

## 2. Android App Setup

### Prerequisites
- Android Studio Iguana or later
- Android SDK API 34+

### Running the App
1. Open the `android` folder in Android Studio.
2. Sync Gradle files.
3. Run the app on an **Android Emulator**.
   - The app is configured to connect to `http://10.0.2.2:8000` (localhost for emulator).
   - Ensure the Python backend is running before testing the app.

### Testing on Physical Device
To run on a real phone, use `ngrok` to expose your local server:
1. Start the backend.
2. Run ngrok: `ngrok http 8000`
3. Copy the HTTPS URL (e.g., `https://xyz.ngrok-free.app`).
4. Update `android/app/src/main/java/com/antigravity/food/api/RetrofitClient.kt`:
   ```kotlin
   private const val BASE_URL = "https://your-ngrok-url.app/"
   ```
5. Rebuild and run on your device.
