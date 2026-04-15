"""Full integration test: all API endpoints."""
import sys
import os
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Instagram_API import InstagramAPI

TARGET_USERNAME = "__cl__.py"

results = []


def test(name, func):
    """Run a test and record pass/fail."""
    try:
        result = func()
        results.append(("PASS", name, result))
        print(f"  [PASS] {name}")
        return result
    except Exception as e:
        results.append(("FAIL", name, str(e)))
        print(f"  [FAIL] {name}: {e}")
        traceback.print_exc()
        return None


# ══════════════════════════════════════════════
# 0. Setup
# ══════════════════════════════════════════════
print("=== SETUP ===")

username = input("Username: ").strip()
password = input("Password: ").strip()
totp_secret = input("TOTP secret (leave empty to skip): ").strip() or None
proxy = input("Proxy URL (leave empty to skip): ").strip() or None

api = InstagramAPI(proxy=proxy)
result = api.login(username, password, totp_secret=totp_secret)

if api.user_id:
    source = "session" if result.session == "restored" else "login"
    print(f"  OK via {source} (user_id={api.user_id})")
else:
    print(f"  Login failed: {result}")
    sys.exit(1)

MY_USER_ID = api.user_id

# ══════════════════════════════════════════════
# 1. User endpoints
# ══════════════════════════════════════════════
print("\n=== 1. USER ENDPOINTS ===")

my_info = test("user_info (self)", lambda: api.user_info(MY_USER_ID))
if my_info:
    print(f"       username={my_info.user.username} followers={my_info.user.follower_count}")

target_info = test("user_info_by_username", lambda: api.user_info_by_username(TARGET_USERNAME))
TARGET_ID = None
if target_info and target_info.user:
    TARGET_ID = str(target_info.user.pk)
    print(f"       @{target_info.user.username} id={TARGET_ID}")

if TARGET_ID:
    stream_info = test("user_info_stream", lambda: api.user_info_stream(TARGET_ID))
    if stream_info and stream_info.user:
        print(f"       full_name={stream_info.user.full_name}")

test("user_search", lambda: api.user_search("instagram"))

# ══════════════════════════════════════════════
# 2. Friendship endpoints
# ══════════════════════════════════════════════
print("\n=== 2. FRIENDSHIP ===")

if TARGET_ID:
    fs = test("friendship_show", lambda: api.friendship_show(TARGET_ID))
    if fs:
        print(f"       following={fs.following} followed_by={fs.followed_by}")

    fs_many = test("friendship_show_many", lambda: api.friendship_show_many([TARGET_ID]))
    if fs_many:
        print(f"       statuses={len(fs_many.friendship_statuses or {})}")

    fs_create = test("friendship_create (follow)", lambda: api.friendship_create(TARGET_ID))
    if fs_create:
        print(f"       following={fs_create.following}")

    fs_destroy = test("friendship_destroy (unfollow)", lambda: api.friendship_destroy(TARGET_ID))
    if fs_destroy:
        print(f"       following={fs_destroy.following}")

    fl = test("followers", lambda: api.followers(TARGET_ID, count=5))
    if fl:
        print(f"       users={len(fl.users or [])}")

    fg = test("following", lambda: api.following(TARGET_ID, count=5))
    if fg:
        print(f"       users={len(fg.users or [])}")

# ══════════════════════════════════════════════
# 3. Feed endpoints
# ══════════════════════════════════════════════
print("\n=== 3. FEED ===")

timeline = test("feed_timeline", lambda: api.feed_timeline())
MEDIA_ID = None
if timeline and timeline.feed_items:
    print(f"       items={timeline.num_results} more={timeline.more_available}")
    for item in timeline.feed_items:
        media = item.media_or_ad
        if media and media.pk:
            MEDIA_ID = f"{media.pk}_{media.user.pk}"
            print(f"       first_media: @{media.user.username} id={MEDIA_ID}")
            break

if TARGET_ID:
    uf = test("user_feed", lambda: api.user_feed(TARGET_ID, count=3))
    if uf:
        print(f"       posts={uf.num_results} more={uf.more_available}")
        if uf.items and not MEDIA_ID:
            first = uf.items[0]
            MEDIA_ID = f"{first.pk}_{first.user.pk}"
            print(f"       using media: {MEDIA_ID}")

tray = test("feed_reels_tray", lambda: api.feed_reels_tray())
if tray and tray.tray:
    print(f"       stories_tray: {len(tray.tray)} users")

if TARGET_ID:
    test("user_story", lambda: api.user_story(TARGET_ID))
    test("get_latest_reel_media", lambda: api.get_latest_reel_media([TARGET_ID]))

# ══════════════════════════════════════════════
# 4. Media / Comments / Notes
# ══════════════════════════════════════════════
print("\n=== 4. MEDIA / COMMENTS / NOTES ===")

test("media_blocked", lambda: api.media_blocked())

if MEDIA_ID:
    mi = test("media_info", lambda: api.media_info(MEDIA_ID))
    if mi and mi.items:
        print(f"       media_type={mi.items[0].media_type}")

    test("media_likers", lambda: api.media_likers(MEDIA_ID))
    test("media_like", lambda: api.media_like(MEDIA_ID))
    test("media_unlike", lambda: api.media_unlike(MEDIA_ID))
    test("media_save", lambda: api.media_save(MEDIA_ID))
    test("media_unsave", lambda: api.media_unsave(MEDIA_ID))
    test("media_comments", lambda: api.media_comments(MEDIA_ID))
    test("check_offensive_comment", lambda: api.check_offensive_comment(MEDIA_ID, "test"))

    comment_result = test("media_comment (post '.')", lambda: api.media_comment(MEDIA_ID, "."))
    COMMENT_PK = None
    if comment_result and comment_result.comment:
        COMMENT_PK = str(comment_result.comment.pk)
        print(f"       comment_pk={COMMENT_PK}")

    if COMMENT_PK:
        test("media_comment_bulk_delete", lambda: api.media_comment_bulk_delete(MEDIA_ID, [COMMENT_PK]))

    note_result = test("create_note", lambda: api.create_note(MEDIA_ID))
    NOTE_ID = None
    if note_result and note_result.id:
        NOTE_ID = str(note_result.id)
        print(f"       note_id={NOTE_ID}")

    if NOTE_ID:
        test("delete_note", lambda: api.delete_note(NOTE_ID))
else:
    print("  (skipped — no media_id available)")

# ══════════════════════════════════════════════
# 5. Direct Messages
# ══════════════════════════════════════════════
print("\n=== 5. DIRECT MESSAGES ===")

inbox = test("direct_inbox", lambda: api.direct_inbox())
THREAD_ID = None
if inbox and inbox.inbox and inbox.inbox.threads:
    first = inbox.inbox.threads[0]
    THREAD_ID = first.thread_id
    names = ", ".join(u.username for u in (first.users or []))
    print(f"       first_thread: {names} id={THREAD_ID}")

test("direct_pending_requests", lambda: api.direct_pending_requests())
test("direct_presence", lambda: api.direct_presence())
test("direct_has_interop_upgraded", lambda: api.direct_has_interop_upgraded())
test("get_presence_disabled", lambda: api.get_presence_disabled())

if THREAD_ID:
    test("direct_send_text", lambda: api.direct_send_text("API test", thread_ids=[THREAD_ID]))
    if MEDIA_ID:
        test("direct_send_media_share", lambda: api.direct_send_media_share(MEDIA_ID, thread_ids=[THREAD_ID]))

# ══════════════════════════════════════════════
# 6. Discover / Explore
# ══════════════════════════════════════════════
print("\n=== 6. DISCOVER / EXPLORE ===")

explore = test("discover_explore", lambda: api.discover_explore())
if explore and explore.sectional_items:
    print(f"       sections={len(explore.sectional_items)}")

test("clips_stream", lambda: api.clips_stream())
test("clips_share_to_fb_config", lambda: api.clips_share_to_fb_config())

if TARGET_ID:
    test("discover_chaining", lambda: api.discover_chaining(TARGET_ID, TARGET_USERNAME))

# ══════════════════════════════════════════════
# 7. Notifications
# ══════════════════════════════════════════════
print("\n=== 7. NOTIFICATIONS ===")

news = test("news_inbox", lambda: api.news_inbox())
if news:
    print(f"       new={len(news.new_stories or [])} old={len(news.old_stories or [])}")

test("notifications_badge", lambda: api.notifications_badge())
test("notification_settings (notifications)", lambda: api.notification_settings("notifications"))
test("notification_settings (direct)", lambda: api.notification_settings("instagram_direct"))

# ══════════════════════════════════════════════
# 8. Account / Config
# ══════════════════════════════════════════════
print("\n=== 8. ACCOUNT / CONFIG ===")

test("current_user", lambda: api.current_user())
test("mobileconfig", lambda: api.mobileconfig())
test("loom_fetch_config", lambda: api.loom_fetch_config())
test("get_account_family", lambda: api.get_account_family())
test("dual_tokens", lambda: api.dual_tokens())
test("banyan", lambda: api.banyan())
test("ndx_ig_steps", lambda: api.ndx_ig_steps())
test("limited_interactions_reminder", lambda: api.limited_interactions_reminder())
test("process_contact_point_signals", lambda: api.process_contact_point_signals())
test("store_push_permissions", lambda: api.store_push_permissions())
test("get_restricted_users", lambda: api.get_restricted_users())

# ══════════════════════════════════════════════
# 9. Live
# ══════════════════════════════════════════════
print("\n=== 9. LIVE ===")

test("live_good_time", lambda: api.live_good_time())

# ══════════════════════════════════════════════
# 10. Session save
# ══════════════════════════════════════════════
print("\n=== 10. SESSION SAVE ===")

api.save_session()
print("  Session saved")

# ══════════════════════════════════════════════
# Summary
# ══════════════════════════════════════════════
print(f"\n{'=' * 60}")
print("SUMMARY")
print(f"{'=' * 60}")
passed = [r for r in results if r[0] == "PASS"]
failed = [r for r in results if r[0] == "FAIL"]
print(f"  PASS: {len(passed)}/{len(results)}")
print(f"  FAIL: {len(failed)}/{len(results)}")

if failed:
    print("\n  Failed tests:")
    for _, name, err in failed:
        print(f"    - {name}: {err}")
