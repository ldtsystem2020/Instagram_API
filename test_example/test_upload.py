"""Upload integration test: photo, video, carousel, story, delete."""
import sys
import os
import time

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

    print("Select test:")
    print("  1. Publish photo")
    print("  2. Publish video")
    print("  3. Publish carousel (2 photos)")
    print("  4. Publish story photo")
    print("  5. Publish story video")
    print("  6. Delete media")
    print("  7. Archive media")
    choice = input("Choice: ").strip()

    if choice == "1":
        path = input("Photo path: ").strip()
        caption = input("Caption (optional): ").strip()
        r = api.publish_photo(path, caption=caption)
        print(f"Status: {r.status}")
        if r.media:
            print(f"Media PK: {r.media.pk}")

    elif choice == "2":
        path = input("Video path: ").strip()
        caption = input("Caption (optional): ").strip()
        duration = float(input("Duration (seconds): ").strip())
        r = api.publish_video(path, caption=caption, duration=duration)
        print(f"Status: {r.status}")
        if r.media:
            print(f"Media PK: {r.media.pk}")

    elif choice == "3":
        path1 = input("Photo 1 path: ").strip()
        path2 = input("Photo 2 path: ").strip()
        caption = input("Caption (optional): ").strip()
        with open(path1, "rb") as f:
            r1 = api.upload_photo(f.read())
        print(f"Upload 1: {r1.status} (upload_id={r1.upload_id})")
        with open(path2, "rb") as f:
            r2 = api.upload_photo(f.read())
        print(f"Upload 2: {r2.status} (upload_id={r2.upload_id})")
        children = [
            {"upload_id": r1.upload_id},
            {"upload_id": r2.upload_id},
        ]
        r = api.configure_sidecar(children, caption=caption)
        print(f"Sidecar status: {r.status}")
        if r.media:
            print(f"Media PK: {r.media.pk}")

    elif choice == "4":
        path = input("Story photo path: ").strip()
        r = api.publish_story_photo(path)
        print(f"Status: {r.status}")
        if r.media:
            print(f"Media PK: {r.media.pk}")

    elif choice == "5":
        path = input("Story video path: ").strip()
        duration = int(input("Duration (ms): ").strip())
        r = api.publish_story_video(path, duration_ms=duration)
        print(f"Status: {r.status}")
        if r.media:
            print(f"Media PK: {r.media.pk}")

    elif choice == "6":
        media_id = input("Media ID to delete: ").strip()
        r = api.media_delete(media_id)
        print(f"Status: {r.status} did_delete={r.did_delete}")

    elif choice == "7":
        media_id = input("Media ID to archive: ").strip()
        r = api.media_archive(media_id)
        print(f"Status: {r.status}")

    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
