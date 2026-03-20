"""Example: Check friendship status with a user."""
from _common import get_api

api = get_api()

target = input("Enter username: ").strip()

# First get user_id from username
info = api.user_info_by_username(target)
if not info.user or not info.user.pk:
    print(f"User '{target}' not found")
    exit(1)

user_id = str(info.user.pk)
print(f"\n@{target} (id={user_id})")

# Check friendship
fs = api.friendship_show(user_id)
print(f"  You follow them:   {fs.following}")
print(f"  They follow you:   {fs.followed_by}")
print(f"  Blocking:          {fs.blocking}")
print(f"  Muting:            {fs.muting}")
print(f"  Is restricted:     {fs.is_restricted}")
print(f"  Outgoing request:  {fs.outgoing_request}")
print(f"  Incoming request:  {fs.incoming_request}")
