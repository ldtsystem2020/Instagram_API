"""Example: Login with session persistence.

First run  -> login + save session to session.json
Next runs  -> restore session, no login needed
"""
from _common import get_api

api = get_api()
print(f"\nLogged in as: {api.username} (id={api.user_id})")
