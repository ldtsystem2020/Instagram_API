"""Device identity and session generation."""
import uuid
import time
import json


class DeviceIdentity:
    """Represents an Android device's identity for Instagram API calls."""

    def __init__(
        self,
        device_id: str | None = None,
        family_device_id: str | None = None,
        phone_id: str | None = None,
        locale: str = "en_US",
    ):
        self.device_id = device_id or str(uuid.uuid4())
        self.family_device_id = family_device_id or str(uuid.uuid4())
        self.phone_id = phone_id or str(uuid.uuid4())
        self.locale = locale
        self.waterfall_id = str(uuid.uuid4())
        self.pigeon_session_id = f"UFS-{uuid.uuid4()}-0"
        self.aac_jid = str(uuid.uuid4())
        self.aac_init_timestamp = int(time.time())

    def get_locale_headers(self) -> dict:
        return {
            "X-IG-App-Locale": self.locale,
            "X-IG-Device-Locale": self.locale,
            "X-IG-Mapped-Locale": self.locale,
        }

    def get_pigeon_headers(self) -> dict:
        return {
            "X-Pigeon-Session-Id": self.pigeon_session_id,
            "X-Pigeon-Rawclienttime": f"{time.time():.3f}",
        }

    def get_aac(self) -> str:
        return json.dumps({
            "aac_init_timestamp": self.aac_init_timestamp,
            "aacjid": self.aac_jid,
            "aaccs": "",
        })

    def new_waterfall_id(self) -> str:
        self.waterfall_id = str(uuid.uuid4())
        return self.waterfall_id
