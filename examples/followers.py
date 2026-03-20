"""Example: Get followers/following list for a user."""
from _common import get_api

api = get_api()

username = input("Target username: ").strip()
user = api.user_info_by_username(username).user
if not user:
    print("User not found")
    exit(1)

print(f"@{user.username} - {user.follower_count} followers, {user.following_count} following")

list_type = input("List (followers/following): ").strip().lower()
count = int(input("How many (default 50): ").strip() or "50")

if list_type == "following":
    result = api.following(user.pk_id, count=count)
else:
    result = api.followers(user.pk_id, count=count)

print(f"\nGot {len(result.users)} users:")
for u in result.users:
    private = " [private]" if u.is_private else ""
    print(f"  @{u.username} ({u.full_name}){private}")
