"""Example: View stories tray and fetch a user's story."""
from _common import get_api

api = get_api()

# Stories tray (list of users who have active stories)
tray = api.feed_reels_tray()
print(f"Stories tray: {len(tray.tray or [])} users")

if tray.tray:
    for i, reel in enumerate(tray.tray[:10]):
        print(f"  [{i+1}] @{reel.user.username} ({reel.media_count} stories)")

# Fetch specific user's story
target_id = input("\nEnter user_id to view story (or skip): ").strip()
if target_id:
    story = api.user_story(target_id)
    if story.reel:
        items = story.reel.items or []
        print(f"\n  Story items: {len(items)}")
        for item in items:
            print(f"    - type={item.media_type} ts={item.taken_at}")
    else:
        print("  No active stories")
