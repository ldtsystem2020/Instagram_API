"""Instagram private API client built from reverse-engineered endpoints."""
import json
import os
from urllib.parse import quote

import requests

from .constants import API_BASE, DEFAULT_HEADERS, BLOKS_ASYNC
from .device import DeviceIdentity
from .bloks import build_bloks_body, parse_bloks_response
from .models import Response
from .endpoints import (
    AuthMixin, FeedMixin, NotificationsMixin, DirectMixin,
    DiscoverMixin, UsersMixin, MediaMixin, LiveMixin, AccountMixin,
    FriendshipsMixin, UploadMixin,
)

SESSION_DIR = "sessions"


class InstagramAPI(
    AuthMixin,
    FeedMixin,
    NotificationsMixin,
    DirectMixin,
    DiscoverMixin,
    UsersMixin,
    MediaMixin,
    LiveMixin,
    AccountMixin,
    FriendshipsMixin,
    UploadMixin,
):
    """Instagram private API client.

    Usage:
        api = InstagramAPI()
        api.login("username", "password")
        # Session auto-saved to sessions/_username.json
        # Next time, session auto-restored if still valid

        timeline = api.feed_timeline()
    """

    def __init__(self, device: DeviceIdentity | None = None,
                 proxy: str | None = None,
                 session_dir: str = SESSION_DIR):
        self.device = device or DeviceIdentity()
        self.session = requests.Session()
        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}
        self.session.headers.update(DEFAULT_HEADERS)
        self.session.headers.update(self.device.get_locale_headers())

        # State
        self.user_id: str | None = None
        self.username: str | None = None
        self.ig_www_claim: str = "0"
        self.authorization: str = ""
        self.mid: str = ""

        # Session directory
        self._session_dir = session_dir

    # ─── Session persistence ─────────────────────────────────

    def _session_path(self, username: str) -> str:
        """Get session file path for a username: sessions/_username.json"""
        return os.path.join(self._session_dir, f"_{username}.json")

    def save_session(self) -> None:
        """Save session state to sessions/_username.json."""
        if not self.username:
            return

        data = {
            "user_id": self.user_id,
            "username": self.username,
            "ig_www_claim": self.ig_www_claim,
            "authorization": self.authorization,
            "mid": self.mid,
            "device": {
                "device_id": self.device.device_id,
                "family_device_id": self.device.family_device_id,
                "phone_id": self.device.phone_id,
                "locale": self.device.locale,
                "waterfall_id": self.device.waterfall_id,
                "pigeon_session_id": self.device.pigeon_session_id,
                "aac_jid": self.device.aac_jid,
                "aac_init_timestamp": self.device.aac_init_timestamp,
            },
            "cookies": {
                cookie.name: cookie.value
                for cookie in self.session.cookies
            },
            "extra": {},
        }
        for attr in ("direct_region_hint", "rur", "shbid", "shbts"):
            if hasattr(self, attr):
                data["extra"][attr] = getattr(self, attr)

        path = self._session_path(self.username)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _load_session(self, username: str) -> bool:
        """Load session state from sessions/_username.json.

        Returns True if loaded successfully, False otherwise.
        """
        path = self._session_path(username)
        if not os.path.exists(path):
            return False

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Restore auth state
        self.user_id = data.get("user_id")
        self.username = data.get("username")
        self.ig_www_claim = data.get("ig_www_claim", "0")
        self.authorization = data.get("authorization", "")
        self.mid = data.get("mid", "")

        # Restore device identity
        dev = data.get("device", {})
        if dev:
            self.device = DeviceIdentity(
                device_id=dev.get("device_id"),
                family_device_id=dev.get("family_device_id"),
                phone_id=dev.get("phone_id"),
                locale=dev.get("locale", "en_US"),
            )
            self.device.waterfall_id = dev.get("waterfall_id", self.device.waterfall_id)
            self.device.pigeon_session_id = dev.get("pigeon_session_id", self.device.pigeon_session_id)
            self.device.aac_jid = dev.get("aac_jid", self.device.aac_jid)
            self.device.aac_init_timestamp = dev.get("aac_init_timestamp", self.device.aac_init_timestamp)
            self.session.headers.update(self.device.get_locale_headers())

        # Restore cookies
        for name, value in data.get("cookies", {}).items():
            self.session.cookies.set(name, value)

        # Restore extra state
        for attr, value in data.get("extra", {}).items():
            setattr(self, attr, value)

        return True

    def _validate_session(self) -> bool:
        """Check if the loaded session is still valid by calling user_info."""
        if not self.user_id or not self.authorization:
            return False
        try:
            resp = self.user_info(self.user_id)
            return resp.user is not None and resp.user.username is not None
        except Exception:
            return False

    # ─── Internal helpers ────────────────────────────────────────

    def _headers(self, extra: dict | None = None) -> dict:
        """Build full request headers with session state."""
        h = {}
        h.update(self.device.get_pigeon_headers())
        h["X-IG-WWW-Claim"] = self.ig_www_claim
        if self.authorization:
            h["Authorization"] = self.authorization
        if self.mid:
            h["X-MID"] = self.mid
        if extra:
            h.update(extra)
        return h

    def _update_state_from_response(self, resp: requests.Response):
        """Extract session tokens from response headers."""
        if "ig-set-ig-u-ig-direct-region-hint" in resp.headers:
            val = resp.headers.get("ig-set-ig-u-ig-direct-region-hint", "")
            if val:
                self.direct_region_hint = val
        if "ig-set-ig-u-ds-user-id" in resp.headers:
            val = resp.headers.get("ig-set-ig-u-ds-user-id", "")
            if val:
                self.user_id = val
        if "ig-set-ig-u-rur" in resp.headers:
            val = resp.headers.get("ig-set-ig-u-rur", "")
            if val:
                self.rur = val
        if "ig-set-ig-u-shbid" in resp.headers:
            val = resp.headers.get("ig-set-ig-u-shbid", "")
            if val:
                self.shbid = val
        if "ig-set-ig-u-shbts" in resp.headers:
            val = resp.headers.get("ig-set-ig-u-shbts", "")
            if val:
                self.shbts = val
        if "x-ig-set-www-claim" in resp.headers:
            val = resp.headers.get("x-ig-set-www-claim", "")
            if val:
                self.ig_www_claim = val
        if "ig-set-authorization" in resp.headers:
            val = resp.headers.get("ig-set-authorization", "")
            if val:
                self.authorization = val
        if "ig-set-x-mid" in resp.headers:
            val = resp.headers.get("ig-set-x-mid", "")
            if val:
                self.mid = val

    def _post(self, path: str, data: str | dict | None = None,
              base: str = API_BASE, extra_headers: dict | None = None) -> requests.Response:
        url = f"{base}{path}"
        resp = self.session.post(url, data=data, headers=self._headers(extra_headers))
        self._update_state_from_response(resp)
        return resp

    def _upload_raw(self, path: str, data: bytes,
                    extra_headers: dict | None = None,
                    base: str = API_BASE) -> requests.Response:
        """POST raw binary data (for rupload endpoints)."""
        url = f"{base}{path}"
        headers = self._headers(extra_headers)
        headers["Content-Type"] = "application/octet-stream"
        resp = self.session.post(url, data=data, headers=headers)
        self._update_state_from_response(resp)
        return resp

    def _get(self, path: str, params: dict | None = None,
             base: str = API_BASE, extra_headers: dict | None = None) -> requests.Response:
        url = f"{base}{path}"
        resp = self.session.get(url, params=params, headers=self._headers(extra_headers))
        self._update_state_from_response(resp)
        return resp

    @staticmethod
    def _json(resp: requests.Response) -> Response:
        """Safely parse JSON response into a Response object."""
        try:
            return Response(resp.json())
        except Exception:
            return Response({"_error": resp.status_code, "_body": resp.text[:500]})

    def _signed_body(self, data: dict) -> str:
        """Build signed_body=SIGNATURE.json_payload format."""
        payload = json.dumps(data, separators=(",", ":"))
        return f"signed_body=SIGNATURE.{quote(payload)}"

    def _bloks_post(self, bloks_id: str, client_input_params: dict,
                    server_params: dict) -> Response:
        """POST to bloks async_action endpoint and return parsed response."""
        path = f"{BLOKS_ASYNC}{bloks_id}/"
        body = build_bloks_body(client_input_params, server_params)
        resp = self._post(path, data=body)
        try:
            return Response(parse_bloks_response(resp.json()))
        except Exception:
            return Response({"status": resp.status_code, "text": resp.text[:500]})

    def _common_server_params(self, **overrides) -> dict:
        """Server params shared across login flow requests."""
        params = {
            "is_from_logged_out": 0,
            "layered_homepage_experiment_group": "Deploy: Not in Experiment",
            "device_id": self.device.device_id,
            "waterfall_id": self.device.waterfall_id,
            "is_platform_login": 0,
            "family_device_id": self.device.family_device_id,
            "offline_experiment_group": "caa_iteration_v3_perf_ig_4",
            "access_flow_version": "pre_mt_behavior",
            "is_from_logged_in_switcher": 0,
            "qe_device_id": self.device.device_id,
        }
        params.update(overrides)
        return params
