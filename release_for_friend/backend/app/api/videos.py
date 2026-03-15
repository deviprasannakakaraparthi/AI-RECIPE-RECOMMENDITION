from fastapi import APIRouter
from googleapiclient.discovery import build
import os

router = APIRouter()

# You should replace this with your actual API key or set it in environment variables
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "YOUR_YOUTUBE_API_KEY")

@router.get("/search")
def search_video(query: str):
    if YOUTUBE_API_KEY == "YOUR_YOUTUBE_API_KEY":
        return {"video_url": None, "error": "YouTube API Key not set"}

    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        request = youtube.search().list(q=query, part="snippet", type="video", maxResults=1)
        response = request.execute()
        if response["items"]:
            video_id = response["items"][0]["id"]["videoId"]
            url = f"https://www.youtube.com/watch?v={video_id}"
            return {"video_url": url}
        return {"video_url": None}
    except Exception as e:
        print(f"Error searching video: {e}")
        return {"video_url": None, "error": str(e)}
