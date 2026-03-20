"""Account management and configuration endpoints."""
from urllib.parse import urlencode

from ..constants import (
    API_BASE_B,
    PATH_CONTACT_SIGNALS, PATH_LOOM_CONFIG, PATH_ACCOUNT_FAMILY,
    PATH_MOBILECONFIG, PATH_DUAL_TOKENS, PATH_PUSH_REGISTER,
    PATH_BANYAN, PATH_NDX_STEPS, PATH_LIMITED_INTERACTIONS,
    PATH_NOTIFICATIONS_PUSH_PERMS, PATH_RESTRICTED_USERS,
    PATH_EDIT_PROFILE, PATH_CURRENT_USER,
    PATH_CHANGE_PROFILE_PICTURE, PATH_REMOVE_PROFILE_PICTURE,
    PATH_SET_BIOGRAPHY,
)
from ..models import Response, UserInfoResponse


class AccountMixin:
    """Account management and configuration endpoints."""

    def process_contact_point_signals(self) -> Response:
        """Process contact point signals."""
        data = self._signed_body({
            "phone_id": self.device.phone_id,
            "_uuid": self.device.device_id,
            "google_tokens": "[]",
            "device_id": self.device.device_id,
        })
        resp = self._post(PATH_CONTACT_SIGNALS, data=data)
        return self._json(resp)

    def loom_fetch_config(self) -> Response:
        """Fetch loom config."""
        resp = self._get(PATH_LOOM_CONFIG, base=API_BASE_B)
        return self._json(resp)

    def get_account_family(self) -> Response:
        """Fetch account family info."""
        resp = self._get(PATH_ACCOUNT_FAMILY, base=API_BASE_B)
        return self._json(resp)

    def mobileconfig(self) -> Response:
        """Fetch mobile config."""
        data = self._signed_body({
            "unit_type": "2",
            "bool_opt_policy": "1",
            "_uuid": self.device.device_id,
        })
        resp = self._post(PATH_MOBILECONFIG, data=data, base=API_BASE_B)
        return self._json(resp)

    def dual_tokens(self) -> Response:
        """Fetch dual tokens (zero-rating)."""
        data = {
            "device_id": self.device.device_id,
            "_uuid": self.device.device_id,
            "normal_token_hash": "",
        }
        resp = self._post(PATH_DUAL_TOKENS, data=urlencode(data), base=API_BASE_B)
        return self._json(resp)

    def push_register(self, device_token: str = "") -> Response:
        """Register for push notifications."""
        data = {
            "device_type": "android_mqtt",
            "is_main_push_channel": "true",
            "device_token": device_token,
            "_uuid": self.device.device_id,
            "users": self.user_id or "",
        }
        resp = self._post(PATH_PUSH_REGISTER, data=urlencode(data), base=API_BASE_B)
        return self._json(resp)

    def banyan(self) -> Response:
        """Fetch banyan data (share sheet recipients)."""
        params = {
            "is_private_share": "false",
            "views": '["story_share_sheet","reshare_share_sheet","threads_people_picker"]',
        }
        resp = self._get(PATH_BANYAN, params=params)
        return self._json(resp)

    def ndx_ig_steps(self) -> Response:
        """Fetch NDX IG steps."""
        params = {"ndx_request_type": "async_get_ndx_ig_steps"}
        resp = self._get(PATH_NDX_STEPS, params=params)
        return self._json(resp)

    def limited_interactions_reminder(self) -> Response:
        """Check limited interactions reminder."""
        params = {"signed_body": "SIGNATURE.{}"}
        resp = self._get(PATH_LIMITED_INTERACTIONS, params=params)
        return self._json(resp)

    def store_push_permissions(self) -> Response:
        """Store client push permission status."""
        data = {
            "_uuid": self.device.device_id,
            "enabled": "true",
        }
        resp = self._post(PATH_NOTIFICATIONS_PUSH_PERMS, data=urlencode(data))
        return self._json(resp)

    def get_restricted_users(self) -> Response:
        """Fetch list of restricted users."""
        resp = self._get(PATH_RESTRICTED_USERS)
        return self._json(resp)

    def current_user(self) -> UserInfoResponse:
        """Get current logged-in user's full profile info."""
        params = {"edit": "true"}
        resp = self._get(PATH_CURRENT_USER, params=params)
        return UserInfoResponse(self._json(resp))

    def edit_profile(self, full_name: str | None = None,
                     biography: str | None = None,
                     external_url: str | None = None,
                     email: str | None = None,
                     phone_number: str | None = None) -> UserInfoResponse:
        """Edit profile fields. Only provided fields are changed.

        Args:
            full_name: Display name
            biography: Bio text
            external_url: Website link
            email: Email address
            phone_number: Phone number
        """
        current = self.current_user()
        user = current.user

        payload = {
            "username": user.username or self.username or "",
            "first_name": full_name if full_name is not None else (user.full_name or ""),
            "biography": biography if biography is not None else (user.biography or ""),
            "external_url": external_url if external_url is not None else (user.external_url or ""),
            "email": email if email is not None else (user.email or ""),
            "phone_number": phone_number if phone_number is not None else (user.phone_number or ""),
            "_uid": self.user_id or "",
            "_uuid": self.device.device_id,
        }
        data = urlencode(payload)
        resp = self._post(PATH_EDIT_PROFILE, data=data)
        return UserInfoResponse(self._json(resp))

    def set_biography(self, text: str) -> Response:
        """Set biography text (quick method, no need to fetch current profile).

        Args:
            text: New biography text
        """
        data = self._signed_body({
            "raw_text": text,
            "_uid": self.user_id or "",
            "_uuid": self.device.device_id,
            "device_id": self.device.device_id,
        })
        resp = self._post(PATH_SET_BIOGRAPHY, data=data)
        return self._json(resp)

    def change_profile_picture(self, image_data: bytes) -> UserInfoResponse:
        """Change profile picture.

        Uses rupload to upload the image, then sets it as profile picture.

        Args:
            image_data: Raw JPEG/PNG bytes of the new profile picture.
                        PNG is auto-converted to JPEG if Pillow is installed.
        """
        # Convert PNG to JPEG if needed
        if image_data[:8] == b'\x89PNG\r\n\x1a\n':
            from io import BytesIO
            try:
                from PIL import Image
                img = Image.open(BytesIO(image_data))
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                buf = BytesIO()
                img.save(buf, format="JPEG", quality=95)
                image_data = buf.getvalue()
            except ImportError:
                pass  # If no Pillow, try sending PNG as-is

        # Step 1: Upload via rupload
        upload_result = self.upload_photo(image_data)

        # Step 2: Set as profile picture using upload_id
        data = self._signed_body({
            "upload_id": upload_result.upload_id,
            "_uid": self.user_id or "",
            "_uuid": self.device.device_id,
        })
        resp = self._post(PATH_CHANGE_PROFILE_PICTURE, data=data)
        return UserInfoResponse(self._json(resp))

    def remove_profile_picture(self) -> UserInfoResponse:
        """Remove profile picture (reset to default)."""
        data = self._signed_body({
            "_uid": self.user_id or "",
            "_uuid": self.device.device_id,
        })
        resp = self._post(PATH_REMOVE_PROFILE_PICTURE, data=data)
        return UserInfoResponse(self._json(resp))
