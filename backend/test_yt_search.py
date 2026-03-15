import urllib.request
import urllib.parse
import re

query = "paneer butter masala recipe"
safe_query = urllib.parse.quote_plus(query)
url = f"https://www.youtube.com/results?search_query={safe_query}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    html = urllib.request.urlopen(req, timeout=5).read().decode()
    video_ids = re.findall(r"watch\?v=([a-zA-Z0-9_-]{11})", html)
    print(video_ids)
except Exception as e:
    print("Error:", e)
