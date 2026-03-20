"""Example: Upload a story (photo or video)."""
from _common import get_api

api = get_api()

media_type = input("Type (photo/video): ").strip().lower()
path = input("File path: ").strip()

if media_type == "video":
    duration_ms = int(input("Duration in ms (e.g. 15000): ").strip() or "0")
    result = api.publish_story_video(path, duration_ms=duration_ms)
else:
    result = api.publish_story_photo(path)

if result.media:
    print(f"Story published! pk={result.media.pk} type={result.media.media_type}")
else:
    print(f"Failed: {result.status}")
