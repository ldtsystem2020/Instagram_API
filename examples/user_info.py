"""Example: Lookup user by username and display profile info."""
from _common import get_api

api = get_api()

target = input("Enter username to lookup: ").strip()
info = api.user_info_by_username(target)

if info.user:
    u = info.user
    print(f"\n{'='*40}")
    print(f"  Username:    {u.username}")
    print(f"  User ID:     {u.pk}")
    print(f"  Full name:   {u.full_name}")
    print(f"  Bio:         {u.biography}")
    print(f"  Followers:   {u.follower_count}")
    print(f"  Following:   {u.following_count}")
    print(f"  Posts:        {u.media_count}")
    print(f"  Private:     {u.is_private}")
    print(f"  Verified:    {u.is_verified}")
    print(f"{'='*40}")
else:
    print(f"User '{target}' not found")
