# Instagram Private API

<p align="center">
  <img src="banner.svg" alt="Instagram_API Banner" width="100%">
</p>

**[繁體中文](README_zh.md)** | English

Python client for Instagram's private API, reverse-engineered from Android app traffic.

> **For educational/research purposes only.** Not affiliated with Instagram or Meta.

## Features

- **70+ endpoints** across 11 modules — feed, users, media, upload, direct, discover, and more
- **25 typed response models** with full IDE autocompletion via attribute access
- **Auto session management** — login once, sessions persist across restarts
- **2FA support** — handled automatically during login
- **Upload system** — photos, videos, carousels, stories (photo & video)
- **Profile editing** — name, bio, profile picture
- **Auto-pagination** — followers/following lists paginate internally

## Installation

```bash
pip install requests pycryptodome Pillow
```

- Python >= 3.10
- `Pillow` is optional (only needed for auto-generating video cover frames and PNG-to-JPEG conversion)

## Quick Start

```python
from Instagram_API import InstagramAPI

api = InstagramAPI()
api.login("username", "password")  # auto session restore, 2FA handled

# User info
info = api.user_info(api.user_id)
print(info.user.username, info.user.follower_count)

# Timeline
timeline = api.feed_timeline()
for item in timeline.feed_items:
    if item.media_or_ad:
        print(item.media_or_ad.user.username)
```

## Usage Examples

### Media

```python
# Like / unlike / save
api.media_like(media_id)
api.media_unlike(media_id)
api.media_save(media_id)

# Comments
api.media_comment(media_id, "Nice!")
comments = api.media_comments(media_id)
```

### Upload & Publish

```python
# Single photo
api.publish_photo("photo.jpg", caption="Hello!")

# Video (auto-generates cover frame)
api.publish_video("video.mp4", caption="Video!", duration=10.0)

# Story
api.publish_story_photo("story.jpg")
api.publish_story_video("story.mp4", duration_ms=15000)

# Carousel (multi-photo)
r1 = api.upload_photo(open("a.jpg", "rb").read())
r2 = api.upload_photo(open("b.jpg", "rb").read())
api.configure_sidecar([
    {"upload_id": r1.upload_id},
    {"upload_id": r2.upload_id}
], caption="carousel")

# Delete / archive
api.media_delete(media_id)
api.media_archive(media_id)
```

### Social

```python
# Followers (auto-paginated)
fl = api.followers(user_id, count=200)
for u in fl.users:
    print(u.username)

# Follow / unfollow
api.friendship_create(user_id)
api.friendship_destroy(user_id)

# DM by user_id (no thread_id needed)
api.direct_send_text("hello", recipient_users=[user_pk_id])

# DM by thread
api.direct_send_text("hello", thread_ids=[thread_id])
```

### Profile Editing

```python
# Edit name and bio
api.edit_profile(full_name="New Name", biography="New bio")
api.set_biography("Quick bio update")

# Change / remove profile picture
api.change_profile_picture(open("pic.jpg", "rb").read())
api.remove_profile_picture()
```

### Session Management

```python
# Sessions are saved automatically after login
# Next time, login() restores the session without re-authentication
api.login("username", "password")  # instant if session is valid

# Manual save
api.save_session()
```

Sessions are stored in `sessions/_username.json`.

## Endpoints

| Category | Key Methods | Count |
|----------|-------------|-------|
| Auth | `login`, `two_factor_verify` | 6 |
| Users | `user_info`, `user_info_by_username`, `user_search` | 6 |
| Feed | `feed_timeline`, `user_feed`, `feed_reels_tray`, `user_story` | 6 |
| Media | `media_info`, `media_like`, `media_save`, `media_comment`, `create_note` | 13 |
| Upload | `publish_photo`, `publish_video`, `publish_story_photo`, `configure_sidecar`, `media_delete` | 11+ |
| Direct | `direct_inbox`, `direct_send_text`, `direct_send_media_share` | 7 |
| Discover | `discover_explore`, `clips_stream`, `discover_chaining` | 4 |
| Notifications | `news_inbox`, `notifications_badge`, `notification_settings` | 3 |
| Friendships | `friendship_show`, `friendship_create`, `followers`, `following` | 6 |
| Account | `current_user`, `edit_profile`, `set_biography`, `change_profile_picture` | 16 |
| Live | `live_good_time` | 1 |

See [`examples/`](examples/) for complete usage examples of each category.

## Project Structure

```
Instagram_API/
├── client.py          # API client + session management
├── models.py          # 25 typed response models
├── crypto.py          # password encryption (RSA + AES-256-GCM)
├── constants.py       # API endpoints & headers
├── device.py          # device identity generation
├── bloks.py           # bloks protocol handler
└── endpoints/         # 11 mixin modules
    ├── auth.py        # login, 2FA, session
    ├── feed.py        # timeline, stories
    ├── users.py       # user info, search
    ├── media.py       # like, save, comment, notes
    ├── upload.py      # photo/video upload & publish
    ├── direct.py      # DM inbox & messaging
    ├── discover.py    # explore, reels
    ├── notifications.py
    ├── friendships.py # follow, followers list
    ├── account.py     # profile editing, settings
    └── live.py

sessions/              # auto-managed session files
examples/              # usage examples per category
```

## Issues

If you have any questions or run into problems, feel free to open an [Issue](https://github.com/ldtsystem2020/Instagram_API/issues).

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 LDT System
