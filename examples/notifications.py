"""Example: View notifications and activity inbox."""
from _common import get_api

api = get_api()

# Activity inbox
news = api.news_inbox()
new_stories = news.new_stories or []
old_stories = news.old_stories or []
print(f"New notifications: {len(new_stories)}")
print(f"Old notifications: {len(old_stories)}")

for item in new_stories[:5]:
    print(f"  [{item.story_type}] {(item.args.text or '')[:80]}")

# Badge counts
badge = api.notifications_badge()
print(f"\nBadge: {badge}")

# Notification settings
settings = api.notification_settings("notifications")
print(f"Settings status: {settings.status}")
