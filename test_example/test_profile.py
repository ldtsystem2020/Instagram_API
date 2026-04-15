"""Profile editing test: name, bio, profile picture."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Instagram_API import InstagramAPI


def main():
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    totp_secret = input("TOTP secret (leave empty to skip): ").strip() or None
    proxy = input("Proxy URL (leave empty to skip): ").strip() or None

    api = InstagramAPI(proxy=proxy)
    result = api.login(username, password, totp_secret=totp_secret)

    if not api.user_id:
        print("Login failed")
        sys.exit(1)
    print(f"Logged in (user_id={api.user_id})\n")

    # Show current profile
    current = api.current_user()
    u = current.user
    print(f"Current profile:")
    print(f"  Username: @{u.username}")
    print(f"  Name: {u.full_name}")
    print(f"  Bio: {u.biography}")
    print(f"  Website: {u.external_url}")
    print()

    print("Select test:")
    print("  1. Change name")
    print("  2. Change biography")
    print("  3. Change profile picture")
    print("  4. Remove profile picture")
    print("  5. Edit all (name + bio)")
    choice = input("Choice: ").strip()

    if choice == "1":
        new_name = input("New name: ").strip()
        r = api.edit_profile(full_name=new_name)
        print(f"Status: {r.status}")
        if r.user:
            print(f"Updated name: {r.user.full_name}")

    elif choice == "2":
        new_bio = input("New biography: ").strip()
        r = api.set_biography(new_bio)
        print(f"Status: {r.status}")

    elif choice == "3":
        path = input("Image path: ").strip()
        with open(path, "rb") as f:
            image_data = f.read()
        r = api.change_profile_picture(image_data)
        print(f"Status: {r.status}")
        if r.user:
            print(f"New pic: {r.user.profile_pic_url[:80]}...")

    elif choice == "4":
        confirm = input("Remove profile picture? (yes/no): ").strip()
        if confirm.lower() == "yes":
            r = api.remove_profile_picture()
            print(f"Status: {r.status}")

    elif choice == "5":
        new_name = input("New name: ").strip()
        new_bio = input("New biography: ").strip()
        r = api.edit_profile(full_name=new_name, biography=new_bio)
        print(f"Status: {r.status}")
        if r.user:
            print(f"Updated: name={r.user.full_name}")

    else:
        print("Invalid choice")

    # Verify
    print("\nVerifying...")
    c = api.current_user()
    print(f"  Name: {c.user.full_name}")
    print(f"  Bio: {c.user.biography}")


if __name__ == "__main__":
    main()
