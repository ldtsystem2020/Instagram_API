"""Example: Explore page and user search."""
from _common import get_api

api = get_api()

# Explore page
print("=== Explore ===")
explore = api.discover_explore()
items = explore.sectional_items or []
print(f"Sections: {len(items)}")

# User search
query = input("\nSearch users (or skip): ").strip()
if query:
    result = api.user_search(query)
    users = result.users or []
    print(f"\nFound {len(users)} users:")
    for u in users[:10]:
        print(f"  @{u.username} (id={u.pk}) - {u.full_name}")
        print(f"    followers={u.follower_count} private={u.is_private}")

# Suggested accounts (chaining)
target = input("\nSee suggested accounts for username (or skip): ").strip()
if target:
    info = api.user_info_by_username(target)
    if info.user and info.user.pk:
        chaining = api.discover_chaining(str(info.user.pk), target)
        for u in (chaining.users or [])[:10]:
            print(f"  @{u.username} - {u.full_name}")
