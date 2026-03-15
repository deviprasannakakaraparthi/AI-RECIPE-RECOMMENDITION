from moviepy.editor import TextClip
try:
    c = TextClip("Hello", fontsize=70, color='white')
    print("Success")
except Exception as e:
    print(e)
