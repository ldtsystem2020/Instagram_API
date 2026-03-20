"""Basic usage example."""
from Instagram_API import InstagramAPI

api = InstagramAPI()
api.login("your_username", "your_password")

# User info
info = api.user_info(api.user_id)
print(f"Logged in as @{info.user.username} ({info.user.follower_count} followers)")

# Look up another user
target = api.user_info_by_username("instagram")
print(f"@{target.user.username} id={target.user.pk}")

# Timeline
timeline = api.feed_timeline()
for item in timeline.feed_items:
    media = item.media_or_ad
    if media:
        print(f"  @{media.user.username}: {media.pk}")
        break

# Stories tray
tray = api.feed_reels_tray()
print(f"Stories from {len(tray.tray)} users")

# DM inbox
inbox = api.direct_inbox()
for thread in (inbox.inbox.threads or [])[:3]:
    names = ", ".join(u.username for u in (thread.users or []))
    print(f"  DM: {names}")

# Save session
api.save_session()
