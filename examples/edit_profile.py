"""Example: Edit profile (name, bio, picture)."""
from _common import get_api

api = get_api()

# View current profile
current = api.current_user()
user = current.user
print(f"Current profile:")
print(f"  Username: @{user.username}")
print(f"  Name: {user.full_name}")
print(f"  Bio: {user.biography}")
print(f"  Website: {user.external_url}")
print()

action = input("Action (name/bio/picture/remove_picture): ").strip().lower()

if action == "name":
    new_name = input("New display name: ").strip()
    result = api.edit_profile(full_name=new_name)
    print(f"Updated name to: {result.user.full_name}")

elif action == "bio":
    new_bio = input("New biography: ").strip()
    result = api.set_biography(new_bio)
    print(f"Result: {result.status}")

elif action == "picture":
    path = input("Image file path: ").strip()
    with open(path, "rb") as f:
        image_data = f.read()
    result = api.change_profile_picture(image_data)
    print(f"Result: {result.status}")

elif action == "remove_picture":
    confirm = input("Remove profile picture? (yes/no): ").strip().lower()
    if confirm == "yes":
        result = api.remove_profile_picture()
        print(f"Result: {result.status}")

else:
    print("Unknown action")
