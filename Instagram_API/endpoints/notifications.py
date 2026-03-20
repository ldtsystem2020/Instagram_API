"""Notifications and news inbox."""
from urllib.parse import urlencode

from ..constants import PATH_NEWS_INBOX, PATH_NOTIFICATIONS_BADGE, PATH_NOTIFICATION_SETTINGS
from ..models import NewsInboxResponse, Response


class NotificationsMixin:
    """Notification-related endpoints."""

    def news_inbox(self) -> NewsInboxResponse:
        """Fetch activity/notifications inbox."""
        params = {
            "could_truncate_feed": "true",
            "should_skip_prefetch_if_pending": "false",
        }
        resp = self._get(PATH_NEWS_INBOX, params=params)
        return NewsInboxResponse(self._json(resp))

    def notifications_badge(self) -> Response:
        """Fetch notification badge counts."""
        data = {
            "phone_id": self.device.phone_id,
            "trigger": "app_start",
            "is_onboarded_in_current_session": "false",
            "_uuid": self.device.device_id,
            "user_ids": self.user_id or "",
        }
        resp = self._post(PATH_NOTIFICATIONS_BADGE, data=urlencode(data))
        return self._json(resp)

    def notification_settings(self, content_type: str = "notifications") -> Response:
        """Fetch notification settings.

        Args:
            content_type: "notifications" or "instagram_direct"
        """
        params = {
            "enable_ig_new_settings": "false",
            "content_type": content_type,
        }
        resp = self._get(PATH_NOTIFICATION_SETTINGS, params=params)
        return self._json(resp)
