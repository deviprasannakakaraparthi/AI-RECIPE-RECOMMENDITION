from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import HTMLResponse
from youtubesearchpython import VideosSearch
import os
import json
from app.models.video_maker import create_recipe_video_sync

router = APIRouter()

@router.get("/view/{recipe_id}")
def view_generated_video(recipe_id: str):
    """HTML page that checks if video is ready and plays it"""
    video_path = f"static/videos/{recipe_id}.mp4"
    if os.path.exists(video_path):
        return HTMLResponse(content=f'''
        <html><body style="margin:0; background:black; display:flex; justify-content:center; align-items:center; height:100vh;">
            <video width="100%" height="100%" controls autoplay>
              <source src="/{video_path}" type="video/mp4">
            </video>
        </body></html>
        ''')
    else:
        return HTMLResponse(content='''
        <html><head><meta http-equiv="refresh" content="3"></head>
        <body style="margin:0; background:black; color:white; display:flex; justify-content:center; align-items:center; height:100vh; font-family:sans-serif;">
            <div><h3>Chef AI is cooking your video... 🍳</h3><p>Please wait few seconds...</p></div>
        </body></html>
        ''')

@router.get("/search")
def search_video(query: str):
    try:
        videos_search = VideosSearch(query, limit = 1)
        results = videos_search.result()
        
        if results and "result" in results and len(results["result"]) > 0:
            url = results["result"][0]["link"]
            return {"video_url": url}
        return {"video_url": f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"}
    except Exception as e:
        print(f"Error searching video: {e}")
        return {"video_url": f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}", "error": str(e)}
