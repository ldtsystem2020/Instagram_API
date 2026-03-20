"""Direct Messages (DM) endpoints."""
import uuid
from urllib.parse import urlencode

from ..constants import (
    PATH_DIRECT_INBOX, PATH_DIRECT_PENDING,
    PATH_DIRECT_PRESENCE, PATH_DIRECT_INTEROP, PATH_PRESENCE_DISABLED,
    PATH_DIRECT_SEND_TEXT, PATH_DIRECT_SEND_MEDIA_SHARE,
)
from ..models import DirectInboxResponse, Response


class DirectMixin:
    """Direct messaging endpoints."""

    def direct_inbox(self) -> DirectInboxResponse:
        """Fetch DM inbox."""
        params = {
            "include_old_mrs": "false",
            "visual_message_return_type": "unseen",
            "thread_message_limit": "10",
            "persistentBadging": "true",
            "limit": "20",
            "fetch_reason": "initial_snapshot",
        }
        resp = self._get(PATH_DIRECT_INBOX, params=params)
        return DirectInboxResponse(self._json(resp))

    def direct_pending_requests(self) -> Response:
        """Fetch pending DM requests preview."""
        params = {"pending_request_count_only": "true"}
        resp = self._get(PATH_DIRECT_PENDING, params=params)
        return self._json(resp)

    def direct_presence(self) -> Response:
        """Fetch online presence for DM contacts."""
        params = {"suggested_followers_limit": "0"}
        resp = self._get(PATH_DIRECT_PRESENCE, params=params)
        return self._json(resp)

    def direct_has_interop_upgraded(self) -> Response:
        """Check DM interop upgrade status."""
        resp = self._get(PATH_DIRECT_INTEROP)
        return self._json(resp)

    def get_presence_disabled(self) -> Response:
        """Check if presence (online status) is disabled."""
        params = {"signed_body": "SIGNATURE.{}"}
        resp = self._get(PATH_PRESENCE_DISABLED, params=params)
        return self._json(resp)

    def direct_send_media_share(self, media_id: str, text: str = "",
                                thread_ids: list[str] | None = None,
                                recipient_users: list[str] | None = None) -> Response:
        """Share/forward a media post to a DM thread or directly to user(s).

        Provide either thread_ids OR recipient_users (user pk_id).

        Args:
            media_id: Media ID to share (e.g. "12345_67890")
            text: Optional text message with the share
            thread_ids: List of thread IDs to share to
            recipient_users: List of user IDs (pk_id) to share to directly
        """
        import json as _json
        mutation_token = str(uuid.uuid4().int)[:19]
        payload = {
            "action": "send_item",
            "media_id": media_id,
            "text": text,
            "send_silently": "false",
            "client_context": mutation_token,
            "mutation_token": mutation_token,
            "offline_threading_id": mutation_token,
            "device_id": f"android-{self.device.device_id[:16]}",
            "_uuid": self.device.device_id,
            "send_attribution": "feed_timeline",
        }
        if thread_ids:
            payload["thread_ids"] = _json.dumps(thread_ids)
        if recipient_users:
            payload["recipient_users"] = _json.dumps([int(u) for u in recipient_users])
        data = urlencode(payload)
        resp = self._post(PATH_DIRECT_SEND_MEDIA_SHARE, data=data)
        return self._json(resp)

    def direct_send_text(self, text: str,
                         thread_ids: list[str] | None = None,
                         recipient_users: list[str] | None = None) -> Response:
        """Send a text message to a DM thread or directly to user(s).

        Provide either thread_ids OR recipient_users (user pk_id).

        Args:
            text: Message text content
            thread_ids: List of thread IDs to send to
            recipient_users: List of user IDs (pk_id) to send to directly
        """
        import json as _json
        mutation_token = str(uuid.uuid4().int)[:19]
        payload = {
            "action": "send_item",
            "text": text,
            "send_silently": "false",
            "client_context": mutation_token,
            "mutation_token": mutation_token,
            "offline_threading_id": mutation_token,
            "device_id": f"android-{self.device.device_id[:16]}",
            "_uuid": self.device.device_id,
            "send_attribution": "inbox",
            "is_x_transport_forward": "false",
        }
        if thread_ids:
            payload["thread_ids"] = _json.dumps(thread_ids)
        if recipient_users:
            payload["recipient_users"] = _json.dumps([int(u) for u in recipient_users])
        data = urlencode(payload)
        resp = self._post(PATH_DIRECT_SEND_TEXT, data=data)
        return self._json(resp)
