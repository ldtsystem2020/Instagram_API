"""Bloks request/response helpers."""
import json
from urllib.parse import urlencode, quote

from .constants import BLOKS_VERSION_ID


def build_bloks_body(
    client_input_params: dict,
    server_params: dict,
    bloks_version: str = BLOKS_VERSION_ID,
) -> str:
    """Build URL-encoded body for bloks async_action requests.

    Returns the form-encoded string:
        params=<url_encoded_json>&bk_client_context=<url_encoded_json>&bloks_versioning_id=<hash>
    """
    params_json = json.dumps({
        "client_input_params": client_input_params,
        "server_params": server_params,
    }, separators=(",", ":"))

    bk_client_context = json.dumps({
        "bloks_version": bloks_version,
        "styles_id": "instagram",
        "theme_params": [{"value": ["three_neutral_gray"], "design_system_name": "XMDS"}],
    }, separators=(",", ":"))

    return urlencode({
        "params": params_json,
        "bk_client_context": bk_client_context,
        "bloks_versioning_id": bloks_version,
    }, quote_via=quote)


def parse_bloks_response(data: dict) -> dict:
    """Extract useful info from a bloks response JSON."""
    result = {"status": data.get("status"), "raw": data}
    layout = data.get("layout", {})
    payload = layout.get("bloks_payload", {})
    if payload:
        result["action"] = payload.get("action", "")
        result["data"] = payload.get("data", [])
        result["props"] = payload.get("props", [])
        result["error_attribution"] = payload.get("error_attribution", {})
    return result
