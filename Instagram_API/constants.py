"""Instagram API constants extracted from captured traffic."""

API_BASE = "https://i.instagram.com"
API_BASE_B = "https://b.i.instagram.com"
GRAPH_BASE = "https://graph.instagram.com"

BLOKS_VERSION_ID = "2530c58174d063584f25e249151d5bc7c53db138cfc68b554daa78c6cd7356b0"

# Default headers observed in all requests
DEFAULT_HEADERS = {
    "X-Bloks-Version-Id": BLOKS_VERSION_ID,
    "X-Bloks-Prism-Button-Version": "CONTROL",
    "X-Bloks-Prism-Indigo-Link-Version": "0",
    "X-Bloks-Prism-Extended-Palette-Rest-Of-Colors": "false",
    "X-IG-Capabilities": "3brTv10=",
    "X-IG-Connection-Type": "WIFI",
    "X-IG-Is-Foldable": "false",
    "X-IG-WWW-Claim": "0",
    "X-IG-Bandwidth-TotalBytes-B": "0",
    "X-IG-Bandwidth-TotalTime-MS": "0",
    "X-IG-Bandwidth-Speed-KBPS": "4937.000",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Accept-Encoding": "gzip, deflate",
    "User-Agent": "Instagram 389.2.0.43.111 Android (27/8.1.0; 440dpi; 1080x2032; samsung; SM-G950F; dreamlte; samsungexynos8895; en_US; 477988029)",
}

# Bloks action endpoints
BLOKS_APPS = "/api/v1/bloks/apps/"
BLOKS_ASYNC = "/api/v1/bloks/async_action/"

# Login flow bloks identifiers
BLOKS_LOGIN_HOMEPAGE = "com.bloks.www.caa.login.login_homepage"
BLOKS_PHONE_PREFILL = "com.bloks.www.bloks.caa.phone.number.prefill.async.controller"
BLOKS_OAUTH_TOKEN = "com.bloks.www.caa.login.oauth.token.fetch.async"
BLOKS_LOGIN_REQUEST = "com.bloks.www.bloks.caa.login.async.send_login_request"
BLOKS_NOTIF_STATUS = "com.bloks.www.caa.notif_status.async"
BLOKS_2FA_VERIFY = "com.bloks.www.ap.two_step_verification.entrypoint_async"

# Password encryption key endpoint
PATH_QE_SYNC = "/api/v1/qe/sync/"

# Post-login API paths
PATH_FEED_TIMELINE = "/api/v1/feed/timeline/"
PATH_FEED_REELS_TRAY = "/api/v1/feed/reels_tray/"
PATH_FEED_REELS_MEDIA = "/api/v1/feed/reels_media_stream/"
PATH_NEWS_INBOX = "/api/v1/news/inbox/"
PATH_DIRECT_INBOX = "/api/v1/direct_v2/inbox/"
PATH_DIRECT_PENDING = "/api/v1/direct_v2/async_get_pending_requests_preview/"
PATH_DIRECT_PRESENCE = "/api/v1/direct_v2/get_presence/"
PATH_DIRECT_INTEROP = "/api/v1/direct_v2/has_interop_upgraded/"
PATH_PRESENCE_DISABLED = "/api/v1/accounts/get_presence_disabled/"
PATH_NOTIFICATIONS_BADGE = "/api/v1/notifications/badge/"
PATH_NOTIFICATIONS_PUSH_PERMS = "/api/v1/notifications/store_client_push_permissions/"
PATH_DISCOVER_EXPLORE = "/api/v1/discover/topical_explore/"
PATH_CLIPS_STREAM = "/api/v1/clips/discover/stream/"
PATH_CLIPS_FB_CONFIG = "/api/v1/clips/user/share_to_fb_config/"
PATH_USER_INFO = "/api/v1/users/{user_id}/info/"
PATH_HIGHLIGHTS_TRAY = "/api/v1/highlights/{user_id}/highlights_tray/"
PATH_CREATOR_INFO = "/api/v1/creator/creator_info/"
PATH_MEDIA_BLOCKED = "/api/v1/media/blocked/"
PATH_BANYAN = "/api/v1/banyan/banyan/"
PATH_LOOM_CONFIG = "/api/v1/loom/fetch_config/"
PATH_LIMITED_INTERACTIONS = "/api/v1/users/get_limited_interactions_reminder/"
PATH_NDX_STEPS = "/api/v1/devices/ndx/api/async_get_ndx_ig_steps/"
PATH_LIVE_GOOD_TIME = "/api/v1/live/get_good_time_for_live/"
PATH_CONTACT_SIGNALS = "/api/v1/accounts/process_contact_point_signals/"
PATH_PUSH_REGISTER = "/api/v1/push/register/"
PATH_MOBILECONFIG = "/api/v1/launcher/mobileconfig/"
PATH_DUAL_TOKENS = "/api/v1/zr/dual_tokens/"
PATH_ACCOUNT_FAMILY = "/api/v1/multiple_accounts/get_account_family/"

# Friendships
PATH_FRIENDSHIP_SHOW = "/api/v1/friendships/show/{user_id}/"
PATH_FRIENDSHIP_SHOW_MANY = "/api/v1/friendships/show_many/"
PATH_FRIENDSHIP_CREATE = "/api/v1/friendships/create/{user_id}/"
PATH_FRIENDSHIP_DESTROY = "/api/v1/friendships/destroy/{user_id}/"
PATH_FOLLOWERS = "/api/v1/friendships/{user_id}/followers/"
PATH_FOLLOWING = "/api/v1/friendships/{user_id}/following/"

# Users (additional)
PATH_USER_INFO_STREAM = "/api/v1/users/{user_id}/info_stream/"
PATH_USER_WEB_PROFILE = "/api/v1/users/web_profile_info/"
PATH_USER_SEARCH = "/api/v1/users/search/"

# Feed (additional)
PATH_USER_FEED = "/api/v1/feed/user/{user_id}/"
PATH_USER_STORY = "/api/v1/feed/user/{user_id}/story/"
PATH_LATEST_REEL_MEDIA = "/api/v1/feed/get_latest_reel_media/"

# Media interactions
PATH_MEDIA_INFO = "/api/v1/media/{media_id}/info/"
PATH_MEDIA_LIKERS = "/api/v1/media/{media_id}/likers/"
PATH_MEDIA_LIKE = "/api/v1/media/{media_id}/like/"
PATH_MEDIA_UNLIKE = "/api/v1/media/{media_id}/unlike/"
PATH_MEDIA_SAVE = "/api/v1/media/{media_id}/save/"
PATH_MEDIA_UNSAVE = "/api/v1/media/{media_id}/unsave/"
PATH_MEDIA_COMMENTS = "/api/v1/media/{media_id}/stream_comments/"
PATH_MEDIA_COMMENT = "/api/v1/media/{media_id}/comment/"
PATH_MEDIA_COMMENT_BULK_DELETE = "/api/v1/media/{media_id}/comment/bulk_delete/"
PATH_CHECK_OFFENSIVE_COMMENT = "/api/v1/media/comment/check_offensive_comment/"
PATH_CREATE_NOTE = "/api/v1/media/create_note/v2/"
PATH_DELETE_NOTE = "/api/v1/media/delete_note/"
PATH_MEDIA_SEEN = "/api/v2/media/seen/"

# Direct (additional)
PATH_DIRECT_SEND_TEXT = "/api/v1/direct_v2/threads/broadcast/text/"
PATH_DIRECT_SEND_MEDIA_SHARE = "/api/v1/direct_v2/threads/broadcast/media_share/"

# Media upload (rupload)
PATH_RUPLOAD_PHOTO = "/rupload_igphoto/{upload_name}"
PATH_RUPLOAD_VIDEO = "/rupload_igvideo/{upload_name}"

# Media configure (publish)
PATH_MEDIA_CONFIGURE = "/api/v1/media/configure/"
PATH_MEDIA_CONFIGURE_SIDECAR = "/api/v1/media/configure_sidecar/"
PATH_MEDIA_CONFIGURE_STORY = "/api/v1/media/configure_to_story/"

# Media management
PATH_MEDIA_DELETE = "/api/v1/media/{media_id}/delete/"
PATH_MEDIA_ARCHIVE = "/api/v1/media/{media_id}/only_me/"

# Discover (additional)
PATH_DISCOVER_CHAINING = "/api/v1/discover/chaining/"

# Notifications (additional)
PATH_NOTIFICATION_SETTINGS = "/api/v1/notifications/get_notification_settings/"

# Profile
PATH_EDIT_PROFILE = "/api/v1/accounts/edit_profile/"
PATH_CURRENT_USER = "/api/v1/accounts/current_user/"
PATH_CHANGE_PROFILE_PICTURE = "/api/v1/accounts/change_profile_picture/"
PATH_REMOVE_PROFILE_PICTURE = "/api/v1/accounts/remove_profile_picture/"
PATH_SET_BIOGRAPHY = "/api/v1/accounts/set_biography/"

# Restrict
PATH_RESTRICTED_USERS = "/api/v1/restrict_action/get_restricted_users/"
