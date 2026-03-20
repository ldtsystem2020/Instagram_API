"""Example: View a user's posts."""
from _common import get_api

api = get_api()

username = input("Target username: ").strip()
user = api.user_info_by_username(username).user
if not user:
    print("User not found")
    exit(1)

print(f"@{user.username} - {user.media_count} posts\n")

feed = api.user_feed(user.pk_id, count=12)
for post in feed.items:
    caption_text = (post.caption.text[:60] if post.caption else "") or "(no caption)"
    media_type = {1: "Photo", 2: "Video", 8: "Carousel"}.get(post.media_type, "?")
    print(f"  [{media_type}] {caption_text}")
    print(f"    likes={post.like_count} comments={post.comment_count} pk={post.pk}")
    print()

if feed.more_available:
    print(f"More posts available (next_max_id={feed.next_max_id})")
