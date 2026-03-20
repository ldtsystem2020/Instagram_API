"""Friendship / relationship endpoints."""
from urllib.parse import urlencode

from ..constants import (
    PATH_FRIENDSHIP_SHOW, PATH_FRIENDSHIP_SHOW_MANY,
    PATH_FRIENDSHIP_CREATE, PATH_FRIENDSHIP_DESTROY,
    PATH_FOLLOWERS, PATH_FOLLOWING,
)
from ..models import FollowersResponse, FriendshipResponse, Response


class FriendshipsMixin:
    """Friendship-related endpoints."""

    def friendship_show(self, user_id: str) -> FriendshipResponse:
        """Check friendship status with a user."""
        path = PATH_FRIENDSHIP_SHOW.format(user_id=user_id)
        resp = self._get(path)
        return FriendshipResponse(self._json(resp))

    def friendship_show_many(self, user_ids: list[str]) -> Response:
        """Check friendship status with multiple users at once."""
        data = urlencode({
            "include_followed_by": "true",
            "user_ids": ", ".join(user_ids),
            "_uuid": self.device.device_id,
        })
        resp = self._post(PATH_FRIENDSHIP_SHOW_MANY, data=data)
        return self._json(resp)

    def friendship_create(self, user_id: str) -> FriendshipResponse:
        """Follow a user."""
        path = PATH_FRIENDSHIP_CREATE.format(user_id=user_id)
        data = self._signed_body({
            "user_id": user_id,
            "_uid": self.user_id or "",
            "_uuid": self.device.device_id,
            "container_module": "profile",
        })
        resp = self._post(path, data=data)
        result = self._json(resp)
        fs = result.get("friendship_status", result)
        fs["status"] = result.get("status", "ok")
        return FriendshipResponse(fs)

    def friendship_destroy(self, user_id: str) -> FriendshipResponse:
        """Unfollow a user."""
        path = PATH_FRIENDSHIP_DESTROY.format(user_id=user_id)
        data = self._signed_body({
            "user_id": user_id,
            "_uid": self.user_id or "",
            "_uuid": self.device.device_id,
            "container_module": "profile",
        })
        resp = self._post(path, data=data)
        result = self._json(resp)
        fs = result.get("friendship_status", result)
        fs["status"] = result.get("status", "ok")
        return FriendshipResponse(fs)

    def _fetch_user_list(self, path: str, count: int) -> FollowersResponse:
        """Internal: fetch a paginated user list up to count."""
        all_users = []
        max_id = None
        per_page = min(count, 100)

        while len(all_users) < count:
            params = {"count": str(per_page)}
            if max_id:
                params["max_id"] = max_id
            resp = self._get(path, params=params)
            result = FollowersResponse(self._json(resp))

            if result.users:
                all_users.extend(result.users)
            if not result.has_more or not result.next_max_id:
                break
            max_id = result.next_max_id

        result["users"] = all_users[:count]
        return result

    def followers(self, user_id: str, count: int = 50) -> FollowersResponse:
        """Get a user's followers list.

        Args:
            user_id: Target user ID
            count: Total number of followers to fetch (auto-paginates)
        """
        path = PATH_FOLLOWERS.format(user_id=user_id)
        return self._fetch_user_list(path, count)

    def following(self, user_id: str, count: int = 50) -> FollowersResponse:
        """Get a user's following list.

        Args:
            user_id: Target user ID
            count: Total number of following to fetch (auto-paginates)
        """
        path = PATH_FOLLOWING.format(user_id=user_id)
        return self._fetch_user_list(path, count)
