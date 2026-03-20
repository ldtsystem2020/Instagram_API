"""Media upload, publish, delete, and archive endpoints."""
import json
import random
import time

from ..constants import (
    PATH_RUPLOAD_PHOTO, PATH_RUPLOAD_VIDEO,
    PATH_MEDIA_CONFIGURE, PATH_MEDIA_CONFIGURE_SIDECAR,
    PATH_MEDIA_CONFIGURE_STORY,
    PATH_MEDIA_DELETE, PATH_MEDIA_ARCHIVE,
)
from ..models import MediaConfigureResponse, Response


class UploadMixin:
    """Media upload and publishing endpoints."""

    @staticmethod
    def _generate_upload_id() -> str:
        """Generate a timestamp-based upload ID."""
        return str(int(time.time()))

    def upload_photo(self, image_data: bytes,
                     upload_id: str | None = None) -> Response:
        """Upload a photo via rupload.

        Args:
            image_data: Raw JPEG/PNG bytes
            upload_id: Optional custom upload ID (auto-generated if omitted)

        Returns:
            Response with upload_id on success.
        """
        upload_id = upload_id or self._generate_upload_id()
        entity_name = f"{upload_id}_0_{random.randint(1000000000, 9999999999)}"

        rupload_params = json.dumps({
            "upload_id": upload_id,
            "media_type": 1,
            "retry_context": json.dumps({
                "num_step_auto_retry": 0,
                "num_reupload": 0,
                "num_step_manual_retry": 0,
            }),
            "image_compression": json.dumps({
                "lib_name": "moz",
                "lib_version": "3.1.m",
                "quality": "80",
            }),
        })

        path = PATH_RUPLOAD_PHOTO.format(upload_name=entity_name)
        headers = {
            "X-Instagram-Rupload-Params": rupload_params,
            "X-Entity-Name": entity_name,
            "X-Entity-Length": str(len(image_data)),
            "Offset": "0",
        }
        resp = self._upload_raw(path, data=image_data, extra_headers=headers)
        result = self._json(resp)
        result["upload_id"] = upload_id
        return result

    def upload_video(self, video_data: bytes,
                     duration_ms: int = 0,
                     width: int = 0, height: int = 0,
                     upload_id: str | None = None,
                     for_story: bool = False) -> Response:
        """Upload a video via rupload (2-step: init + transfer).

        Args:
            video_data: Raw video bytes (MP4)
            duration_ms: Video duration in milliseconds
            width: Video width in pixels
            height: Video height in pixels
            upload_id: Optional custom upload ID
            for_story: Set True when uploading for story (uses media_type=2 + story flags)

        Returns:
            Response with upload_id on success.
        """
        upload_id = upload_id or self._generate_upload_id()
        entity_name = f"{upload_id}_0_{random.randint(1000000000, 9999999999)}"

        params = {
            "upload_id": upload_id,
            "media_type": 2,
            "retry_context": json.dumps({
                "num_step_auto_retry": 0,
                "num_reupload": 0,
                "num_step_manual_retry": 0,
            }),
            "xsharing_user_ids": "[]",
            "upload_media_duration_ms": str(duration_ms),
            "upload_media_width": str(width),
            "upload_media_height": str(height),
        }
        if for_story:
            params["for_album"] = "1"
            params["extract_cover_frame"] = "1"

        rupload_params = json.dumps(params)

        path = PATH_RUPLOAD_VIDEO.format(upload_name=entity_name)
        base_headers = {
            "X-Instagram-Rupload-Params": rupload_params,
            "X-Entity-Name": entity_name,
        }

        # Step 1: Init
        init_headers = {**base_headers, "X-Entity-Length": "0", "Offset": "0"}
        self._upload_raw(path, data=b"", extra_headers=init_headers)

        # Step 2: Transfer
        upload_headers = {
            **base_headers,
            "X-Entity-Length": str(len(video_data)),
            "Offset": "0",
        }
        resp = self._upload_raw(path, data=video_data,
                                extra_headers=upload_headers)
        result = self._json(resp)
        result["upload_id"] = upload_id
        return result

    def configure_photo(self, upload_id: str, caption: str = "",
                        disable_comments: bool = False) -> MediaConfigureResponse:
        """Publish an uploaded photo as a feed post.

        Args:
            upload_id: From upload_photo()
            caption: Post caption text
            disable_comments: Disable comments on the post
        """
        data = self._signed_body({
            "upload_id": upload_id,
            "caption": caption,
            "source_type": "4",
            "media_folder": "Camera",
            "device_id": self.device.device_id,
            "_uid": self.user_id or "",
            "_uuid": self.device.device_id,
            "disable_comments": "1" if disable_comments else "0",
        })
        resp = self._post(PATH_MEDIA_CONFIGURE, data=data)
        return MediaConfigureResponse(self._json(resp))

    def configure_video(self, upload_id: str, caption: str = "",
                        duration: float = 0,
                        disable_comments: bool = False) -> MediaConfigureResponse:
        """Publish an uploaded video as a feed post.

        Requires both upload_video() and upload_photo() (cover) called
        with the same upload_id beforehand.

        Args:
            upload_id: Shared upload ID for video + cover photo
            caption: Post caption text
            duration: Video duration in seconds
            disable_comments: Disable comments on the post
        """
        payload = {
            "upload_id": upload_id,
            "caption": caption,
            "source_type": "4",
            "media_folder": "Camera",
            "device_id": self.device.device_id,
            "_uid": self.user_id or "",
            "_uuid": self.device.device_id,
            "disable_comments": "1" if disable_comments else "0",
            "video_result": "",
            "poster_frame_index": "0",
            "audio_muted": "false",
        }
        if duration > 0:
            payload["length"] = str(duration)
            payload["clips"] = json.dumps([{
                "length": duration,
                "source_type": "4",
            }])
        data = self._signed_body(payload)
        resp = self._post(PATH_MEDIA_CONFIGURE, data=data)
        return MediaConfigureResponse(self._json(resp))

    def configure_sidecar(self, children: list[dict],
                          caption: str = "") -> MediaConfigureResponse:
        """Publish a carousel/sidecar post (multiple photos/videos).

        Args:
            children: List of dicts with keys:
                - "upload_id": str (required)
                - "media_type": int (1=photo, 2=video; default 1)
                - "video_duration": float (seconds, for videos)
            caption: Post caption text
        """
        children_metadata = []
        for child in children:
            meta = {
                "upload_id": child["upload_id"],
                "source_type": "4",
            }
            if child.get("media_type") == 2:
                meta["video_duration"] = child.get("video_duration", 0)
                meta["length"] = child.get("video_duration", 0)
            children_metadata.append(meta)

        data = self._signed_body({
            "caption": caption,
            "client_sidecar_id": self._generate_upload_id(),
            "children_metadata": children_metadata,
            "device_id": self.device.device_id,
            "_uid": self.user_id or "",
            "_uuid": self.device.device_id,
        })
        resp = self._post(PATH_MEDIA_CONFIGURE_SIDECAR, data=data)
        return MediaConfigureResponse(self._json(resp))

    def configure_story(self, upload_id: str,
                        media_type: int = 1) -> MediaConfigureResponse:
        """Publish an uploaded photo/video as a story.

        Args:
            upload_id: From upload_photo() or upload_video()
            media_type: 1 for photo, 2 for video
        """
        payload = {
            "upload_id": upload_id,
            "source_type": "4",
            "configure_mode": "1",
            "media_folder": "Camera",
            "device_id": self.device.device_id,
            "_uid": self.user_id or "",
            "_uuid": self.device.device_id,
        }
        if media_type == 2:
            payload["video_result"] = ""
        data = self._signed_body(payload)
        resp = self._post(PATH_MEDIA_CONFIGURE_STORY, data=data)
        return MediaConfigureResponse(self._json(resp))

    def media_delete(self, media_id: str, media_type: int = 1) -> Response:
        """Delete a media post.

        Args:
            media_id: Media ID (e.g. "12345_67890")
            media_type: 1=photo, 2=video, 8=carousel
        """
        path = PATH_MEDIA_DELETE.format(media_id=media_id)
        data = self._signed_body({
            "media_id": media_id,
            "media_type": str(media_type),
            "_uid": self.user_id or "",
            "_uuid": self.device.device_id,
        })
        resp = self._post(path, data=data)
        return self._json(resp)

    def media_archive(self, media_id: str, media_type: int = 1) -> Response:
        """Archive a media post (move to 'only me').

        Args:
            media_id: Media ID (e.g. "12345_67890")
            media_type: 1=photo, 2=video, 8=carousel
        """
        path = PATH_MEDIA_ARCHIVE.format(media_id=media_id)
        data = self._signed_body({
            "media_id": media_id,
            "media_type": str(media_type),
            "_uid": self.user_id or "",
            "_uuid": self.device.device_id,
        })
        resp = self._post(path, data=data)
        return self._json(resp)

    # ─── High-level convenience methods ───────────────────────

    def publish_photo(self, image_path: str,
                      caption: str = "") -> MediaConfigureResponse:
        """Upload and publish a photo post in one call.

        Args:
            image_path: Path to image file (JPEG/PNG)
            caption: Post caption text
        """
        with open(image_path, "rb") as f:
            image_data = f.read()
        result = self.upload_photo(image_data)
        return self.configure_photo(result.upload_id, caption=caption)

    def publish_video(self, video_path: str, caption: str = "",
                      cover_path: str | None = None,
                      duration: float = 0) -> MediaConfigureResponse:
        """Upload and publish a video post in one call.

        If cover_path is not provided, a black cover frame is generated.

        Args:
            video_path: Path to video file (MP4)
            caption: Post caption text
            cover_path: Optional path to cover image (JPEG/PNG)
            duration: Video duration in seconds
        """
        upload_id = self._generate_upload_id()

        with open(video_path, "rb") as f:
            video_data = f.read()
        self.upload_video(video_data, duration_ms=int(duration * 1000),
                          upload_id=upload_id)

        if cover_path:
            with open(cover_path, "rb") as f:
                cover_data = f.read()
        else:
            # Generate a minimal black JPEG as cover
            import io
            try:
                from PIL import Image
                img = Image.new("RGB", (720, 1280), (0, 0, 0))
                buf = io.BytesIO()
                img.save(buf, "JPEG", quality=70)
                cover_data = buf.getvalue()
            except ImportError:
                raise RuntimeError(
                    "PIL/Pillow required to auto-generate cover. "
                    "Install it or provide cover_path."
                )
        self.upload_photo(cover_data, upload_id=upload_id)

        return self.configure_video(upload_id, caption=caption,
                                    duration=duration)

    def publish_story_photo(self, image_path: str) -> MediaConfigureResponse:
        """Upload and publish a photo story in one call.

        Args:
            image_path: Path to image file
        """
        with open(image_path, "rb") as f:
            image_data = f.read()
        result = self.upload_photo(image_data)
        return self.configure_story(result.upload_id, media_type=1)

    def publish_story_video(self, video_path: str,
                            duration_ms: int = 0) -> MediaConfigureResponse:
        """Upload and publish a video story in one call.

        Args:
            video_path: Path to video file (MP4)
            duration_ms: Video duration in milliseconds
        """
        with open(video_path, "rb") as f:
            video_data = f.read()
        result = self.upload_video(video_data, duration_ms=duration_ms,
                                   for_story=True)
        return self.configure_story(result.upload_id, media_type=2)
