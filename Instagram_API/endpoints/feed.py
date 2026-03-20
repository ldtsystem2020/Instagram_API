"""Feed endpoints — timeline, stories."""
from urllib.parse import urlencode

from ..constants import (
    PATH_FEED_TIMELINE, PATH_FEED_REELS_TRAY, PATH_FEED_REELS_MEDIA,
    PATH_USER_FEED, PATH_USER_STORY, PATH_LATEST_REEL_MEDIA,
)
from ..models import FeedTimelineResponse, ReelsTrayResponse, UserFeedResponse, Response


class FeedMixin:
    """Feed-related endpoints."""

    def feed_timeline(self, reason: str = "cold_start_fetch",
                      max_id: str | None = None) -> FeedTimelineResponse:
        """Fetch home feed timeline."""
        data = {
            "feed_view_info": "[]",
            "phone_id": self.device.phone_id,
            "reason": reason,
            "battery_level": 100,
            "timezone_offset": "28800",
            "_uuid": self.device.device_id,
            "is_charging": 1,
            "will_sound_on": 0,
            "is_on_screen": True,
            "is_async_ads_in_headload_enabled": 1,
            "is_async_ads_double_request": 0,
            "is_async_ads_rti": 1,
            "rti_delivery_backend": 0,
        }
        if max_id:
            data["max_id"] = max_id
        resp = self._post(PATH_FEED_TIMELINE, data=urlencode(data))
        return FeedTimelineResponse(self._json(resp))

    def feed_reels_tray(self) -> ReelsTrayResponse:
        """Fetch stories tray (list of available stories)."""
        data = {
            "supported_capabilities_new": "[]",
            "reason": "cold_start",
            "source": "feed_timeline",
            "_uuid": self.device.device_id,
        }
        resp = self._post(PATH_FEED_REELS_TRAY, data=urlencode(data))
        return ReelsTrayResponse(self._json(resp))

    def feed_reels_media(self, reel_ids: list[str]) -> Response:
        """Fetch stories media for given reel IDs."""
        data = self._signed_body({
            "supported_capabilities_new": [],
            "source": "feed_timeline",
            "reel_ids": reel_ids,
            "_uuid": self.device.device_id,
        })
        resp = self._post(PATH_FEED_REELS_MEDIA, data=data)
        return self._json(resp)

    def user_feed(self, user_id: str, max_id: str | None = None,
                  count: int = 12) -> UserFeedResponse:
        """Fetch a user's posts (paginated).

        Args:
            user_id: Target user ID
            max_id: Pagination cursor from previous response
            count: Number of posts per page (default 12)
        """
        path = PATH_USER_FEED.format(user_id=user_id)
        params = {"count": str(count)}
        if max_id:
            params["max_id"] = max_id
        resp = self._get(path, params=params)
        return UserFeedResponse(self._json(resp))

    def user_story(self, user_id: str) -> Response:
        """Fetch a specific user's current story."""
        path = PATH_USER_STORY.format(user_id=user_id)
        resp = self._get(path)
        return self._json(resp)

    def get_latest_reel_media(self, user_ids: list[str]) -> Response:
        """Fetch latest reel/story media for given user IDs."""
        data = urlencode({
            "user_ids": f'[{",".join(f"{uid!r}" for uid in user_ids)}]',
            "_uuid": self.device.device_id,
        })
        resp = self._post(PATH_LATEST_REEL_MEDIA, data=data)
        return self._json(resp)
