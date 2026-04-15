"""TOTP verification test: generate codes and compare with authenticator app."""
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Instagram_API import generate_totp


def main():
    secret = input("TOTP secret key: ").strip()
    if not secret:
        print("No secret provided")
        sys.exit(1)

    print(f"\nGenerating TOTP codes for: {secret}")
    print("Compare with your authenticator app.\n")

    try:
        while True:
            code = generate_totp(secret)
            remaining = 30 - (int(time.time()) % 30)
            print(f"  Code: {code}  (expires in {remaining:2d}s)", end="\r")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopped.")


if __name__ == "__main__":
    main()
