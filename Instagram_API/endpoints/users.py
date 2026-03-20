"""User and profile endpoints."""
from urllib.parse import urlencode

from ..constants import (
    PATH_USER_INFO, PATH_USER_INFO_STREAM, PATH_HIGHLIGHTS_TRAY,
    PATH_CREATOR_INFO, PATH_USER_WEB_PROFILE, PATH_USER_SEARCH,
)
from ..models import UserInfoResponse, UserSearchResponse, Response


class UsersMixin:
    """User / profile endpoints."""

    def user_info(self, user_id: str) -> UserInfoResponse:
        """Fetch user profile info by user ID."""
        path = PATH_USER_INFO.format(user_id=user_id)
        resp = self._get(path)
        return UserInfoResponse(self._json(resp))

    def user_info_stream(self, user_id: str, module: str = "reel_feed_timeline") -> UserInfoResponse:
        """Fetch user profile info via info_stream (used when viewing profile)."""
        path = PATH_USER_INFO_STREAM.format(user_id=user_id)
        data = urlencode({
            "module": module,
            "entry_point": "reel_viewer_go_to_profile",
            "_uuid": self.device.device_id,
        })
        resp = self._post(path, data=data)
        return UserInfoResponse(self._json(resp))

    def user_info_by_username(self, username: str) -> UserInfoResponse:
        """Fetch user profile info by username (username -> user_id).

        Usage:
            info = api.user_info_by_username("instagram")
            print(info.user.pk)       # numeric user ID
            print(info.user.username)  # "instagram"
        """
        params = {"username": username}
        resp = self._get(PATH_USER_WEB_PROFILE, params=params)
        raw = self._json(resp)
        # web_profile_info wraps user data under "data.user"
        if raw.data and raw.data.user:
            user = dict(raw.data.user)
            # Normalize web API fields to mobile API format:
            # web uses "id" instead of "pk"
            if "id" in user and "pk" not in user:
                user["pk"] = user["id"]
                user["pk_id"] = str(user["id"])
            # web uses edge_followed_by/edge_follow instead of follower_count/following_count
            if "edge_followed_by" in user:
                user["follower_count"] = user["edge_followed_by"].get("count", 0)
            if "edge_follow" in user:
                user["following_count"] = user["edge_follow"].get("count", 0)
            if "edge_owner_to_timeline_media" in user:
                user["media_count"] = user["edge_owner_to_timeline_media"].get("count", 0)
            return UserInfoResponse({"user": user, "status": "ok"})
        return UserInfoResponse(raw)

    def user_search(self, query: str, count: int = 30) -> UserSearchResponse:
        """Search for users by keyword.

        Returns a list of matching users.
        Usage:
            result = api.user_search("instagram")
            for u in result.users:
                print(u.pk, u.username)
        """
        params = {
            "q": query,
            "count": str(count),
            "search_surface": "user_search_page",
        }
        resp = self._get(PATH_USER_SEARCH, params=params)
        return UserSearchResponse(self._json(resp))

    def highlights_tray(self, user_id: str) -> Response:
        """Fetch highlights tray for a user."""
        path = PATH_HIGHLIGHTS_TRAY.format(user_id=user_id)
        params = {"supported_tabs": "[]"}
        resp = self._get(path, params=params)
        return self._json(resp)

    def creator_info(self, user_id: str) -> Response:
        """Fetch creator info for a user."""
        params = {
            "entry_point": "self_profile",
            "supported_tabs": "[]",
        }
        resp = self._get(PATH_CREATOR_INFO, params=params)
        return self._json(resp)
