"""Media interaction endpoints — comments, notes, seen."""
import uuid
from urllib.parse import urlencode

from ..constants import (
    PATH_MEDIA_BLOCKED, PATH_MEDIA_INFO, PATH_MEDIA_LIKERS,
    PATH_MEDIA_LIKE, PATH_MEDIA_UNLIKE,
    PATH_MEDIA_SAVE, PATH_MEDIA_UNSAVE,
    PATH_MEDIA_COMMENTS, PATH_MEDIA_COMMENT,
    PATH_MEDIA_COMMENT_BULK_DELETE, PATH_CHECK_OFFENSIVE_COMMENT,
    PATH_CREATE_NOTE, PATH_DELETE_NOTE, PATH_MEDIA_SEEN,
)
from ..models import (
    CommentResponse, MediaCommentsResponse, MediaInfoResponse,
    MediaLikersResponse, NoteResponse, Response,
)


class MediaMixin:
    """Media-related endpoints."""

    def media_info(self, media_id: str) -> MediaInfoResponse:
        """Get detailed info for a single media post."""
        path = PATH_MEDIA_INFO.format(media_id=media_id)
        resp = self._get(path)
        return MediaInfoResponse(self._json(resp))

    def media_likers(self, media_id: str) -> MediaLikersResponse:
        """Get list of users who liked a media post."""
        path = PATH_MEDIA_LIKERS.format(media_id=media_id)
        resp = self._get(path)
        return MediaLikersResponse(self._json(resp))

    def media_like(self, media_id: str) -> Response:
        """Like a media post."""
        path = PATH_MEDIA_LIKE.format(media_id=media_id)
        data = self._signed_body({
            "media_id": media_id,
            "inventory_source": "media_or_ad",
            "delivery_class": "organic",
            "tap_source": "button",
            "container_module": "feed_timeline",
            "is_carousel_bumped_post": "false",
            "radio_type": "wifi-none",
            "_uid": self.user_id or "",
            "_uuid": self.device.device_id,
            "device_id": self.device.device_id,
        })
        resp = self._post(path, data=data)
        return self._json(resp)

    def media_unlike(self, media_id: str) -> Response:
        """Unlike a media post."""
        path = PATH_MEDIA_UNLIKE.format(media_id=media_id)
        data = self._signed_body({
            "media_id": media_id,
            "inventory_source": "media_or_ad",
            "delivery_class": "organic",
            "tap_source": "button",
            "container_module": "feed_timeline",
            "is_carousel_bumped_post": "false",
            "radio_type": "wifi-none",
            "_uid": self.user_id or "",
            "_uuid": self.device.device_id,
            "device_id": self.device.device_id,
        })
        resp = self._post(path, data=data)
        return self._json(resp)

    def media_save(self, media_id: str) -> Response:
        """Save a media post to collections."""
        path = PATH_MEDIA_SAVE.format(media_id=media_id)
        data = self._signed_body({
            "media_id": media_id,
            "radio_type": "wifi-none",
            "_uid": self.user_id or "",
            "_uuid": self.device.device_id,
            "device_id": self.device.device_id,
        })
        resp = self._post(path, data=data)
        return self._json(resp)

    def media_unsave(self, media_id: str) -> Response:
        """Remove a saved media post."""
        path = PATH_MEDIA_UNSAVE.format(media_id=media_id)
        data = self._signed_body({
            "media_id": media_id,
            "radio_type": "wifi-none",
            "_uid": self.user_id or "",
            "_uuid": self.device.device_id,
            "device_id": self.device.device_id,
        })
        resp = self._post(path, data=data)
        return self._json(resp)

    def media_blocked(self) -> Response:
        """Fetch blocked media list."""
        resp = self._get(PATH_MEDIA_BLOCKED)
        return self._json(resp)

    def media_comments(self, media_id: str) -> MediaCommentsResponse:
        """Fetch comments for a media post."""
        path = PATH_MEDIA_COMMENTS.format(media_id=media_id)
        params = {
            "can_support_threading": "true",
            "is_carousel_bumped_post": "false",
        }
        resp = self._get(path, params=params)
        return MediaCommentsResponse(self._json(resp))

    def media_comment(self, media_id: str, text: str) -> CommentResponse:
        """Post a comment on a media."""
        path = PATH_MEDIA_COMMENT.format(media_id=media_id)
        idempotence = str(uuid.uuid4())
        data = self._signed_body({
            "comment_text": text,
            "idempotence_token": idempotence,
            "comment_creation_key": idempotence,
            "delivery_class": "organic",
            "_uid": self.user_id or "",
            "_uuid": self.device.device_id,
            "carousel_index": "-1",
            "container_module": "comments_v2",
        })
        resp = self._post(path, data=data)
        return CommentResponse(self._json(resp))

    def media_comment_bulk_delete(self, media_id: str, comment_ids: list[str]) -> Response:
        """Delete one or more comments from a media."""
        path = PATH_MEDIA_COMMENT_BULK_DELETE.format(media_id=media_id)
        data = self._signed_body({
            "comment_ids_to_delete": ",".join(comment_ids),
            "_uid": self.user_id or "",
            "_uuid": self.device.device_id,
            "container_module": "comments_v2",
        })
        resp = self._post(path, data=data)
        return self._json(resp)

    def check_offensive_comment(self, media_id: str, text: str) -> Response:
        """Check if a comment text is considered offensive."""
        data = self._signed_body({
            "media_id": media_id,
            "_uid": self.user_id or "",
            "_uuid": self.device.device_id,
            "comment_text": text,
        })
        resp = self._post(PATH_CHECK_OFFENSIVE_COMMENT, data=data)
        return self._json(resp)

    def create_note(self, media_id: str, note_style: int = 13,
                    audience: int = 7, text: str = "") -> NoteResponse:
        """Create a note on a media post."""
        data = urlencode({
            "media_id": media_id,
            "note_style": str(note_style),
            "text": text,
            "_uuid": self.device.device_id,
            "audience": str(audience),
            "event_source": "ufi",
        })
        resp = self._post(PATH_CREATE_NOTE, data=data)
        return NoteResponse(self._json(resp))

    def delete_note(self, note_id: str) -> Response:
        """Delete a note."""
        data = urlencode({
            "_uuid": self.device.device_id,
            "note_id": note_id,
            "event_source": "recs_nux",
        })
        resp = self._post(PATH_DELETE_NOTE, data=data)
        return self._json(resp)

    def media_seen(self, reels: dict) -> Response:
        """Mark stories/reels as seen.

        Args:
            reels: Dict of reel_id -> timestamp pairs,
                   e.g. {"user_id_media_id": "timestamp_timestamp"}
        """
        data = self._signed_body({
            "reels": reels,
            "_uuid": self.device.device_id,
            "_uid": self.user_id or "",
        })
        resp = self._post(PATH_MEDIA_SEEN, data=data,
                          extra_headers={"Content-Encoding": "gzip"})
        return self._json(resp)
