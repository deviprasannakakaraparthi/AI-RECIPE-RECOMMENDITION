import time
import os
import asyncio
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
import urllib.request
from urllib.parse import quote
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

async def _g_audio(text, out):
    c = edge_tts.Communicate(text, "en-US-JennyNeural")
    await c.save(out)

def test_gen():
    start = time.time()
    title = "Paneer Tikka"
    ings = ["Paneer", "Yogurt", "Spices"]
    ix = ["Cut paneer.", "Mix yogurt.", "Bake it."]
    
    clips = []
    # Create a solid color clip for background instead of downloading
    def make_clip(txt, dur):
        from moviepy.editor import ColorClip
        bg = ColorClip(size=(720, 1280), color=(50, 50, 50)).set_duration(dur)
        tc = TextClip(txt, fontsize=50, color='white', bg_color='rgba(0,0,0,0.6)', size=(600, None), method='caption', align='center').set_position('center').set_duration(dur)
        return CompositeVideoClip([bg, tc])
        
    asyncio.run(_g_audio("How to make " + title, "/tmp/t.mp3"))
    ta = AudioFileClip("/tmp/t.mp3")
    clips.append(make_clip(title, ta.duration).set_audio(ta))
    
    for i, step in enumerate(ix):
        asyncio.run(_g_audio(step, f"/tmp/s{i}.mp3"))
        sa = AudioFileClip(f"/tmp/s{i}.mp3")
        clips.append(make_clip(f"Step {i+1}:\\n{step}", sa.duration).set_audio(sa))
        
    final = concatenate_videoclips(clips)
    final.write_videofile("out.mp4", fps=24, logger=None)
    print("Time taken:", time.time() - start)

if __name__ == "__main__":
    test_gen()
