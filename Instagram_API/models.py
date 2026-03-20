"""Response models for attribute-style access with IDE type hints."""
from __future__ import annotations


class Response(dict):
    """Dict subclass that supports attribute access recursively.

    Usage:
        resp = Response({"user": {"username": "foo", "follower_count": 100}})
        resp.user.username       # "foo"
        resp.user.follower_count # 100
        resp["user"]["username"] # still works
        resp.get("missing")      # returns None
    """

    # Dict keys take priority over dict methods (e.g. "items", "keys")
    # so that resp.items returns the API field, not dict.items().
    _DICT_ATTRS = frozenset(dir(dict))

    def __getattribute__(self, key: str) -> Response:
        # Internal/dunder attrs and our own methods use normal lookup
        if key.startswith("_") or key not in Response._DICT_ATTRS:
            return super().__getattribute__(key)
        # For names that collide with dict methods, prefer dict key if present
        if key in self:
            return Response._wrap(self[key])
        return super().__getattribute__(key)

    def __getattr__(self, key: str) -> Response:
        try:
            value = self[key]
        except KeyError:
            return None  # type: ignore[return-value]
        return self._wrap(value)

    def __setattr__(self, key: str, value):
        self[key] = value

    def __delattr__(self, key: str):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key)

    @classmethod
    def _wrap(cls, value):
        if isinstance(value, dict) and not isinstance(value, cls):
            return cls(value)
        if isinstance(value, list):
            return [cls._wrap(item) for item in value]
        return value

    def __repr__(self):
        return f"Response({dict.__repr__(self)})"


# ── Typed response models for IDE autocomplete ──────────────


class User(Response):
    """Instagram user profile fields."""
    pk: int
    pk_id: str
    username: str
    full_name: str
    biography: str
    profile_pic_url: str
    follower_count: int
    following_count: int
    media_count: int
    is_private: bool
    is_verified: bool
    is_business: bool
    category: str
    account_type: int
    has_anonymous_profile_picture: bool
    is_threads_only_user: bool


class UserInfoResponse(Response):
    """Response from user_info() endpoint."""
    user: User
    status: str


class TimelineMedia(Response):
    """A single media item in the feed."""
    pk: int
    id: str
    code: str
    media_type: int
    caption: Response
    image_versions2: Response
    user: User
    like_count: int
    comment_count: int
    taken_at: int


class FeedItem(Response):
    """A single item in the feed timeline."""
    media_or_ad: TimelineMedia | None
    explore_story: Response | None
    end_of_feed_demarcator: Response | None


class FeedTimelineResponse(Response):
    """Response from feed_timeline() endpoint."""
    feed_items: list[FeedItem]
    num_results: int
    more_available: bool
    next_max_id: str
    status: str


class UserFeedResponse(Response):
    """Response from user_feed() endpoint."""
    items: list[TimelineMedia]
    num_results: int
    more_available: bool
    next_max_id: str
    status: str


class ReelItem(Response):
    """A single reel/story tray item."""
    id: int
    user: User
    items: list[Response]
    media_count: int
    prefetch_count: int
    has_besties_media: bool
    latest_reel_media: int
    seen: int


class ReelsTrayResponse(Response):
    """Response from feed_reels_tray() endpoint."""
    tray: list[ReelItem]
    status: str


class DirectThread(Response):
    """A DM thread."""
    thread_id: str
    thread_title: str
    users: list[User]
    items: list[Response]
    last_activity_at: int
    is_group: bool
    read_state: int
    named: bool


class DirectInbox(Response):
    """DM inbox container."""
    threads: list[DirectThread]
    has_older: bool
    unseen_count: int
    unseen_count_ts: int
    blended_inbox_enabled: bool


class DirectInboxResponse(Response):
    """Response from direct_inbox() endpoint."""
    inbox: DirectInbox
    pending_requests_total: int
    status: str


class Comment(Response):
    """A single comment on a media post."""
    pk: int
    text: str
    user: User
    created_at: int
    content_type: str
    status: str


class CommentResponse(Response):
    """Response from media_comment() endpoint."""
    comment: Comment
    comment_creation_key: str
    status: str


class NoteResponse(Response):
    """Response from create_note() endpoint."""
    id: int
    media_id: int
    user_id: int
    text: str
    note_style: int
    audience: int
    created_at: int
    expires_at: int
    user: User
    status: str


class NewsStory(Response):
    """A single notification story."""
    type: int
    story_type: int
    args: Response
    counts: Response
    pk: str


class NewsInboxResponse(Response):
    """Response from news_inbox() endpoint."""
    counts: Response
    new_stories: list[NewsStory]
    old_stories: list[NewsStory]
    status: str


class ExploreSection(Response):
    """A single section in the explore feed."""
    layout_type: str
    feed_type: str
    layout_content: Response
    explore_item_info: Response


class ExploreResponse(Response):
    """Response from discover_explore() endpoint."""
    sectional_items: list[ExploreSection]
    rank_token: str
    more_available: bool
    next_max_id: str
    status: str


class FollowersResponse(Response):
    """Response from followers() / following() endpoint."""
    users: list[User]
    big_list: bool
    page_size: int
    has_more: bool
    next_max_id: str
    status: str


class MediaInfoResponse(Response):
    """Response from media_info() endpoint."""
    items: list[TimelineMedia]
    num_results: int
    more_available: bool
    status: str


class MediaLikersResponse(Response):
    """Response from media_likers() endpoint."""
    users: list[User]
    user_count: int
    status: str


class MediaCommentsResponse(Response):
    """Response from media_comments() endpoint."""
    comments: list[Comment]
    comment_count: int
    has_more_comments: bool
    has_more_headload_comments: bool
    next_min_id: str
    status: str


class MediaConfigureResponse(Response):
    """Response from media configure (publish) endpoints."""
    media: TimelineMedia
    upload_id: str
    status: str


class FriendshipResponse(Response):
    """Response from friendship_show() endpoint."""
    following: bool
    followed_by: bool
    blocking: bool
    muting: bool
    is_private: bool
    incoming_request: bool
    outgoing_request: bool
    is_bestie: bool
    is_restricted: bool
    is_feed_favorite: bool
    status: str


class UserSearchResponse(Response):
    """Response from user_search() endpoint."""
    users: list[User]
    has_more: bool
    num_results: int
    status: str


class LoginResponse(Response):
    """Response from login() / send_login_request()."""
    status: str
    action: str
    requires_2fa: bool
    _2fa_context: str | None
