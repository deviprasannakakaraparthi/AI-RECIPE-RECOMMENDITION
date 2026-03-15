import urllib.request
import re
html = urllib.request.urlopen("https://www.youtube.com/results?search_query=paneer+butter+masala+recipe")
video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
print(video_ids[0] if video_ids else "None")
