"""Example: Like, unlike, save, unsave a post."""
from _common import get_api

api = get_api()

media_id = input("Media ID (e.g. 12345_67890): ").strip()

# Check current state
info = api.media_info(media_id)
item = info.items[0] if info.items else None
if not item:
    print("Media not found")
    exit(1)

print(f"Post by @{item.user.username}")
print(f"  has_liked={item.has_liked}  like_count={item.like_count}")

action = input("\nAction (like/unlike/save/unsave): ").strip().lower()

if action == "like":
    result = api.media_like(media_id)
elif action == "unlike":
    result = api.media_unlike(media_id)
elif action == "save":
    result = api.media_save(media_id)
elif action == "unsave":
    result = api.media_unsave(media_id)
else:
    print("Unknown action")
    exit(1)

print(f"Result: {result.status}")
