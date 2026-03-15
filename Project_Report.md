# Camera-Based Recipe Recommendation System using Deep Learning

## 1. System Architecture

The system follows a Client-Server architecture designed for high performance and scalability.

- **Frontend (Android Application)**:
  - **CameraX**: High-level camera API for capturing ingredient images.
  - **Retrofit & OkHttp**: Networking layer to transmit image bytes to the backend.
  - **Jetpack Compose**: Modern UI toolkit for a premium user experience (Glassmorphism, smooth transitions).
  
- **Backend (Python FastAPI)**:
  - **FastAPI**: Asynchronous web framework for high-throughput ingredient detection and recipe processing.
  - **YOLOv8 Engine**: State-of-the-art object detection for real-time ingredient identification.
  - **Hugging Face Transformers**:
    - **DistilBERT**: Efficient Transformer for ingredient-to-recipe sequence classification / retrieval.
    - **T5 (Text-to-Text Transfer Transformer)**: Generative model for creating structured cooking steps.
  - **Uvicorn**: ASGI server for deployment.

- **Deployment**:
  - **Docker**: Containerization for environment parity.
  - **Cloud (AWS/GCP)**: Hosting the FastAPI container with optional GPU support.

## 2. Model Selection Justification

### A. Ingredient Detection: YOLOv8
- **Why YOLOv8?** YOLO (You Only Look Once) is renowned for its speed and accuracy. Version 8 improves upon previous versions with better feature extraction and a simpler head architecture. It handles multiple overlapping objects (e.g., a pile of vegetables) better than standard CNNs.

### B. Recipe Recommendation: DistilBERT
- **Why DistilBERT?** It is a smaller, faster, cheaper version of BERT that retains 97% of its performance. In a recipe system, we need to map a *set* of ingredients to a *recipe title*. DistilBERT's attention mechanism excels at understanding relationships between ingredient tokens regardless of their order.

### C. Recipe Steps Generation: T5
- **Why T5?** T5 treats every NLP task as a text-to-text problem. By providing "Ingredients: X, Y, Z" as a prompt, T5 can generate structured instructions. It is more robust than simple template-based systems as it understands the culinary context of the inputs.

## 3. Dataset Usage Explanation

- **Food-101**: Used for initial classification and fine-tuning the vision backbone.
- **Open Images (Food Subset)**: Provides bounding box annotations for common vegetables, fruits, and meats, essential for training YOLOv8.
- **Recipe1M+**: A massive dataset containing over 1 million recipes, used to train the Recommendation (DistilBERT) and Generation (T5) models. It provides the ground truth mapping between ingredients and cooking instructions.

## 4. API Flow (Sequence)

1. **Capture**: Android user takes a photo of ingredients.
2. **Upload**: Image is sent via `POST /detect-ingredients` to FastAPI.
3. **Detection**: YOLOv8 processes the image and returns a list of detected items (e.g., `["Tomato", "Onion", "Garlic"]`).
4. **Recommendation**: Detected items are sent to `POST /recommend-recipe`. DistilBERT predicts the most relevant recipe title.
5. **Generation**: The recipe title and ingredients are fed into T5 via `POST /generate-steps` to produce detailed instructions.
6. **Display**: Android app renders the result with a premium UI.

## 5. Output Format
The final project deliverables include:
- `backend/`: Python source code, model loading scripts, and Dockerfile.
- `android/`: Kotlin source code with Jetpack Compose and CameraX.
- `models/`: Pre-trained weight paths or export scripts.
- `Project_Report.md`: Full documentation for academic submission.
