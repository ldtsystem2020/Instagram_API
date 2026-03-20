"""Example: Upload and publish a photo post."""
from _common import get_api

api = get_api()

path = input("Image path: ").strip()
caption = input("Caption (optional): ").strip()

result = api.publish_photo(path, caption=caption)
if result.media:
    print(f"Published! pk={result.media.pk}")
    print(f"URL: https://www.instagram.com/p/{result.media.code}/")
else:
    print(f"Failed: {result.status}")
