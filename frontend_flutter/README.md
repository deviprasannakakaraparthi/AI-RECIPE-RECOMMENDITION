# Recipe AI Flutter Frontend

A premium, AI-powered recipe recommendation mobile application built with Flutter.

## Features
- **AI Ingredient Scanner**: Uses the camera to detect ingredients in your fridge.
- **Master Chef Intelligence**: Connects to a Python backend to generate professional recipes.
- **Premium UI**: Dark mode, glassmorphism, and smooth transitions.
- **Personalized Recommendations**: Choose cuisine, meal type, and spice level.

## Getting Started

1. **Prerequisites**:
   - Flutter SDK installed on your machine.
   - VS Code or Android Studio.

2. **Installation**:
   ```bash
   cd frontend_flutter
   flutter pub get
   ```

3. **Backend Connection**:
   - Ensure the Python backend is running (`bash start.sh` in the `/backend` folder).
   - If using a physical device, update `lib/api/api_service.dart` with your machine's local IP address.
   - If using an Android Emulator, it will work out of the box with `10.0.2.2`.

4. **Run the App**:
   ```bash
   flutter run
   ```

## Backend API Endpoints Used
- `POST /analyze`: Multipart request with image file.
- `POST /recipes/generate`: JSON request with ingredient list and preferences.
