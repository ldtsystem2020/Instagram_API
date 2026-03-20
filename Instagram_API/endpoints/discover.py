"""Discover, Explore, and Clips (Reels) endpoints."""
from urllib.parse import urlencode

from ..constants import PATH_DISCOVER_EXPLORE, PATH_CLIPS_STREAM, PATH_CLIPS_FB_CONFIG, PATH_DISCOVER_CHAINING
from ..models import ExploreResponse, Response


class DiscoverMixin:
    """Discover / Explore / Clips endpoints."""

    def discover_explore(self, is_prefetch: bool = False) -> ExploreResponse:
        """Fetch explore page content."""
        params = {
            "is_prefetch": str(is_prefetch).lower(),
            "is_auto_paginate": "false",
            "omit_cover_media": "false",
            "module": "explore_popular",
            "reels_configuration": "default",
            "use_sectional_payload": "true",
            "timezone_offset": "28800",
        }
        resp = self._get(PATH_DISCOVER_EXPLORE, params=params)
        return ExploreResponse(self._json(resp))

    def clips_stream(self) -> Response:
        """Fetch reels/clips discover stream."""
        data = {
            "seen_reels": "{}",
            "enable_mixed_media_chaining": "true",
            "should_refetch_chaining_media": "false",
            "_uuid": self.device.device_id,
        }
        resp = self._post(PATH_CLIPS_STREAM, data=urlencode(data))
        return self._json(resp)

    def clips_share_to_fb_config(self) -> Response:
        """Get clips share-to-Facebook config."""
        resp = self._get(PATH_CLIPS_FB_CONFIG)
        return self._json(resp)

    def discover_chaining(self, target_id: str, target_username: str = "") -> Response:
        """Fetch suggested/similar accounts for a given user."""
        params = {
            "module": "profile",
            "target_id": target_id,
            "target_username": target_username,
            "profile_chaining_check": "true",
        }
        resp = self._get(PATH_DISCOVER_CHAINING, params=params)
        return self._json(resp)
