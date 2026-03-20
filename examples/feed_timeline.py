"""Example: Fetch home feed timeline."""
from _common import get_api

api = get_api()

timeline = api.feed_timeline()
print(f"Feed items: {timeline.num_results}")
print(f"More available: {timeline.more_available}")

if timeline.feed_items:
    for i, item in enumerate(timeline.feed_items[:5]):
        media = item.media_or_ad
        if media:
            print(f"\n  [{i+1}] @{media.user.username}")
            print(f"      {(media.caption.text or '')[:80]}")
            print(f"      Likes: {media.like_count}")
