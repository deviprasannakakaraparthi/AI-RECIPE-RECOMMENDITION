import os
import asyncio
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
import urllib.request
from urllib.parse import quote
import ssl
import tempfile

ssl._create_default_https_context = ssl._create_unverified_context

async def _g_audio(text, out):
    try:
        c = edge_tts.Communicate(text, "en-US-JennyNeural")
        await c.save(out)
    except Exception as e:
        print(f"TTS Error: {e}")

def create_recipe_video_sync(title: str, ingredients: list, instructions: list, output_filename: str):
    """Generates an animated recipe video to the given output filename"""
    print(f"Generating video for {title}...")
    
    # ensure output directory exists
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    clips = []
    
    # Use a solid color clip for background instead of downloading to make it robust and fast
    def make_clip(txt, dur):
        from moviepy.editor import ColorClip
        bg = ColorClip(size=(720, 1280), color=(30, 30, 30)).set_duration(dur)
        tc = TextClip(txt, fontsize=50, color='white', bg_color='rgba(0,0,0,0.6)', 
                      size=(650, None), method='caption', align='center')
        tc = tc.set_position('center').set_duration(dur)
        return CompositeVideoClip([bg, tc])

    # Get a cross-platform temporary directory
    temp_dir = tempfile.gettempdir()

    # 1. Add Title Slide
    title_text = f"How to make\n{title}"
    title_audio_path = os.path.join(temp_dir, f"{title.replace(' ', '_')}_title.mp3")
    asyncio.run(_g_audio(title_text.replace('\n', ' '), title_audio_path))
    
    dur = 3.0
    if os.path.exists(title_audio_path):
        title_audio = AudioFileClip(title_audio_path)
        dur = title_audio.duration
        title_clip = make_clip(title_text, dur).set_audio(title_audio)
    else:
        title_clip = make_clip(title_text, dur)
    clips.append(title_clip)
    
    # 2. Add Ingredients Slide
    ing_text = "Ingredients:\n\n" + "\n".join([f"• {i}" for i in ingredients[:5]]) 
    if len(ingredients) > 5:
        ing_text += "\n..."
        
    ing_audio_text = "You will need: " + ", ".join(ingredients[:5])
    ing_audio_path = os.path.join(temp_dir, f"{title.replace(' ', '_')}_ing.mp3")
    asyncio.run(_g_audio(ing_audio_text, ing_audio_path))
    
    adur = 4.0
    if os.path.exists(ing_audio_path):
        ing_audio = AudioFileClip(ing_audio_path)
        adur = max(4.0, ing_audio.duration)
        ing_clip = make_clip(ing_text, adur).set_audio(ing_audio)
    else:
        ing_clip = make_clip(ing_text, adur)
    clips.append(ing_clip)
    
    # 3. Add Instruction Slides
    for i, step in enumerate(instructions):
        step_audio_path = os.path.join(temp_dir, f"{title.replace(' ', '_')}_step_{i}.mp3")
        asyncio.run(_g_audio(step, step_audio_path))
        
        sdur = 3.0
        if os.path.exists(step_audio_path):
            step_audio = AudioFileClip(step_audio_path)
            sdur = max(3.0, step_audio.duration)
            step_clip = make_clip(f"Step {i+1}:\n\n{step}", sdur).set_audio(step_audio)
        else:
            step_clip = make_clip(f"Step {i+1}:\n\n{step}", sdur)
        clips.append(step_clip)
        
    final_video = concatenate_videoclips(clips)
    
    # Write fast without logger to prevent terminal clutter
    final_video.write_videofile(
        output_filename, 
        fps=24, 
        codec="libx264", 
        audio_codec="aac",
        logger=None
    )
    print(f"Video {output_filename} generated successfully!")
    return output_filename
