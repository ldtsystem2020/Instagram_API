"""Login / authentication flow."""
import base64
import json
import re
import time
from urllib.parse import urlencode

from ..constants import (
    BLOKS_APPS, BLOKS_LOGIN_HOMEPAGE, BLOKS_OAUTH_TOKEN,
    BLOKS_LOGIN_REQUEST, BLOKS_NOTIF_STATUS, BLOKS_2FA_VERIFY,
    PATH_QE_SYNC,
)
from ..bloks import build_bloks_body
from ..crypto import encrypt_password
from ..models import LoginResponse, Response


def _extract_login_data(action: str) -> dict | None:
    """Extract user info and session tokens directly from bloks action string.

    The bloks action contains deeply escaped JSON that's hard to parse
    structurally, so we use regex to pull key values from the raw text.
    """
    result = {}

    # User ID: (ds4 "40657972276") or "pk":40657972276
    m = re.search(r'\(ds4\s+"(\d+)"\)', action)
    if m:
        result["user_id"] = m.group(1)
    else:
        m = re.search(r'"pk"\\*:(\d+)', action)
        if m:
            result["user_id"] = m.group(1)

    # Username
    m = re.search(r'"username"\\*:\\*"([^"\\]+)"', action)
    if m:
        result["username"] = m.group(1)

    # Authorization token: Bearer IGT:2:base64...
    m = re.search(r'IG-Set-Authorization["\\\s:]+Bearer\s+(IGT:\d+:[A-Za-z0-9+/=]+)', action)
    if m:
        result["authorization"] = f"Bearer {m.group(1)}"

    # WWW claim: hmac.AR0...
    m = re.search(r'x-ig-set-www-claim["\\\s:]+(hmac\.[A-Za-z0-9_]+)', action)
    if m:
        result["www_claim"] = m.group(1)

    return result if result else None


def _extract_2fa_context(action: str) -> str | None:
    """Extract context_data from bloks 2FA redirect action."""
    match = re.search(
        r'"com\.bloks\.www\.ap\.two_step_verification\.entrypoint_async"'
        r'\s*\(f4i\s*\(dkc\s*"context_data"[^)]*\)\s*\(dkc\s*"([^"]+)"',
        action,
    )
    if match:
        return match.group(1)
    # Fallback: look for the long base64-like context blob before |aplc
    match = re.search(r'"([\w_-]{100,}\|aplc)"', action)
    if match:
        return match.group(1)
    return None


class AuthMixin:
    """Login and authentication endpoints."""

    def _fetch_encryption_key(self):
        """Fetch password encryption public key via qe/sync."""
        data = {
            "id": self.device.device_id,
            "experiments": "ig_android_fci_onboarding_friend_search,"
                           "ig_android_device_detection_info_upload,"
                           "ig_android_account_linking_upsell_universe,"
                           "ig_android_direct_main_tab_universe_v2,"
                           "ig_android_sign_in_help_only_one_account_family_universe,"
                           "ig_android_sms_retriever_backtest_universe,"
                           "ig_android_direct_add_direct_to_android_native_photo_share_sheet,"
                           "ig_android_spatial_account_switch_universe",
        }
        resp = self._post(PATH_QE_SYNC, data=urlencode(data))
        self._encryption_key_id = resp.headers.get("ig-set-password-encryption-key-id")
        self._encryption_pub_key = resp.headers.get("ig-set-password-encryption-pub-key")

    def login(self, username: str, password: str,
              two_factor_code: str | None = None,
              two_factor_handler=None) -> LoginResponse:
        """Full login flow with automatic session management.

        1. Check if sessions/_username.json exists
        2. If yes, load it and validate (call user_info)
        3. If session is valid, return immediately (skip login)
        4. If session is expired or missing, do full login flow
        5. Save session after successful login

        Args:
            username: Instagram username
            password: Plain text password (will be encrypted automatically)
            two_factor_code: 2FA code to use directly (skip prompt)
            two_factor_handler: Callable that returns a 2FA code string.
                                Defaults to input() prompt if not provided.

        Returns:
            LoginResponse with login result
        """
        # Try loading existing session
        if self._load_session(username):
            if self._validate_session():
                self.save_session()
                return LoginResponse({"status": "ok", "session": "restored"})

            # Session expired, reset state for fresh login
            self.session.cookies.clear()
            self.user_id = None
            self.authorization = ""
            self.ig_www_claim = "0"
            self.mid = ""

        # Full login flow
        self.username = username
        self.device.new_waterfall_id()

        self.login_homepage()
        self._fetch_encryption_key()
        self.oauth_token_fetch(username)

        if self._encryption_key_id and self._encryption_pub_key:
            pem = base64.b64decode(self._encryption_pub_key).decode()
            enc_password = encrypt_password(
                password, int(self._encryption_key_id), pem
            )
        else:
            enc_password = password

        result = self.send_login_request(username, enc_password)

        # Handle 2FA if required
        action = result.action or ""
        if "two_step_verification" in action:
            context_data = _extract_2fa_context(action)
            self._2fa_context = context_data

            code = two_factor_code
            if not code and context_data:
                if two_factor_handler:
                    code = two_factor_handler()
                else:
                    code = input("Enter 2FA code: ").strip()

            if code and context_data:
                result = self.two_factor_verify(code, context_data)
                action = result.action or ""

        # Extract session data from bloks response
        self._apply_login_data(action)

        # Auto-save session after successful login
        if self.user_id:
            self.save_session()

        return LoginResponse(result)

    def _apply_login_data(self, action: str):
        """Parse bloks action to extract session tokens and user info."""
        data = _extract_login_data(action)
        if not data:
            return

        if "user_id" in data:
            self.user_id = data["user_id"]
        if "username" in data:
            self.username = data["username"]
        if "authorization" in data:
            self.authorization = data["authorization"]
        if "www_claim" in data:
            self.ig_www_claim = data["www_claim"]

    def two_factor_verify(self, code: str, context_data: str | None = None) -> LoginResponse:
        """Submit 2FA verification code.

        Args:
            code: The 6-digit verification code (from SMS, authenticator app, etc.)
            context_data: 2FA context from login response. If None, uses stored context.

        Returns:
            dict with verification result
        """
        ctx = context_data or getattr(self, "_2fa_context", None)
        if not ctx:
            return LoginResponse({"error": "No 2FA context available. Call login() first."})

        client_params = {
            "verification_code": code,
            "context_data": ctx,
            "device_id": self.device.device_id,
            "use_open_instead_of_push": False,
            "use_close_instead_of_back": False,
        }
        server_params = self._common_server_params(
            INTERNAL__latency_qpl_marker_id=36707139,
            INTERNAL__latency_qpl_instance_id=int(time.time() * 10000),
        )
        return self._bloks_post(BLOKS_2FA_VERIFY, client_params, server_params)

    def login_homepage(self) -> Response:
        """Load login homepage (first request in login flow)."""
        path = f"{BLOKS_APPS}{BLOKS_LOGIN_HOMEPAGE}/"
        client_params = {
            "lois_settings": {"lois_token": ""},
            "sim_phone_numbers": [],
        }
        server_params = self._common_server_params(
            is_from_lid_welcome_screen=1,
            is_caa_perf_enabled=1,
            INTERNAL_INFRA_screen_id="",
            left_nav_button_action="BACK",
            show_internal_settings=False,
            flow_source="lid_landing_screen",
            should_use_caa_reg_experience=0,
            aac=self.device.get_aac(),
        )
        body = build_bloks_body(client_params, server_params)
        resp = self._post(path, data=body)
        return self._json(resp)

    def oauth_token_fetch(self, username: str) -> Response:
        """Fetch OAuth token for the given username."""
        client_params = {
            "username_input": username,
            "aac": self.device.get_aac(),
            "lois_settings": {"lois_token": ""},
            "cloud_trust_token": None,
            "zero_balance_state": "",
            "network_bssid": None,
        }
        server_params = self._common_server_params(
            login_surface="login_home",
            INTERNAL__latency_qpl_instance_id=int(time.time() * 10000),
            INTERNAL__latency_qpl_marker_id=36707139,
        )
        return self._bloks_post(BLOKS_OAUTH_TOKEN, client_params, server_params)

    def send_login_request(self, username: str, password: str) -> Response:
        """Send the actual login request with credentials."""
        client_params = {
            "aac": self.device.get_aac(),
            "sim_phones": [],
            "aymh_accounts": [],
            "network_bssid": None,
            "secure_family_device_id": "",
            "has_granted_read_contacts_permissions": 0,
            "auth_secure_device_id": "",
            "has_whatsapp_installed": 0,
            "password": password,
            "sso_token_map_json_string": "",
            "block_store_machine_id": "",
            "ig_vetted_device_nonces": "{}",
            "cloud_trust_token": None,
            "event_flow": "login_manual",
            "password_contains_non_ascii": "false",
            "client_known_key_hash": "",
            "sso_accounts_auth_data": [],
            "encrypted_msisdn": "",
            "has_granted_read_phone_permissions": 0,
            "app_manager_id": "",
            "contact_point": username,
            "has_fb_installed": 0,
            "login_attempt_count": 1,
            "try_num": 1,
            "device_emails": [],
            "machine_id": "",
            "has_granted_notification_permission": 0,
            "flash_call_permission_status": "denied",
            "lois_settings": {"lois_token": ""},
            "zero_balance_state": "",
        }
        server_params = self._common_server_params(
            login_surface="login_home",
            should_trigger_override_login_success_action=0,
            login_credential_type="none",
            server_login_source="login",
            two_step_login_type="one_step_login",
            login_source="Login",
            INTERNAL__latency_qpl_marker_id=36707139,
            INTERNAL__latency_qpl_instance_id=int(time.time() * 10000),
            is_from_aymh=0,
            is_from_landing_page=0,
            left_nav_button_action="BACK",
            password_text_input_id="",
            is_from_empty_password=0,
            is_from_msplit_fallback=0,
            ar_event_source="login_home_page",
            username_text_input_id="",
            is_caa_perf_enabled=1,
            credential_type="password",
            is_from_password_entry_page=0,
            caller="gslr",
            is_from_assistive_id=0,
            reg_flow_source="lid_landing_screen",
        )
        return self._bloks_post(BLOKS_LOGIN_REQUEST, client_params, server_params)

    def notification_status(self) -> Response:
        """Check notification status (called during login flow)."""
        client_params = {
            "aac": self.device.get_aac(),
            "lois_settings": {"lois_token": ""},
            "cloud_trust_token": None,
            "network_bssid": None,
        }
        server_params = self._common_server_params(
            login_surface="login_home",
            source="login",
            INTERNAL__latency_qpl_instance_id=int(time.time() * 10000),
            INTERNAL__latency_qpl_marker_id=36707139,
        )
        return self._bloks_post(BLOKS_NOTIF_STATUS, client_params, server_params)
