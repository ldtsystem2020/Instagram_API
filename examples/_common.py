"""Shared helper: login or restore session."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Instagram_API import InstagramAPI


def get_api() -> InstagramAPI:
    """Return an authenticated InstagramAPI instance.

    Prompts for username and password.
    Automatically restores session if available, re-logins if expired.
    """
    api = InstagramAPI()

    username = input("Username: ").strip()
    password = input("Password: ").strip()
    result = api.login(username, password)

    if api.user_id:
        source = "session" if result.session == "restored" else "login"
        print(f"OK via {source} (user_id={api.user_id})")
    else:
        print("Login failed")
        sys.exit(1)

    return api
