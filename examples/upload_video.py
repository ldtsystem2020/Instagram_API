"""Example: Upload and publish a video post."""
from _common import get_api

api = get_api()

path = input("Video path (MP4): ").strip()
caption = input("Caption (optional): ").strip()
duration = float(input("Duration in seconds (e.g. 10.0): ").strip() or "0")

result = api.publish_video(path, caption=caption, duration=duration)
if result.media:
    print(f"Published! pk={result.media.pk}")
    print(f"URL: https://www.instagram.com/p/{result.media.code}/")
else:
    print(f"Failed: {result.status}")
