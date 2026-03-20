"""Example: Upload and publish a carousel (multi-photo) post."""
from _common import get_api

api = get_api()

print("Enter image paths one per line (empty line to finish):")
paths = []
while True:
    p = input(f"  Image {len(paths)+1}: ").strip()
    if not p:
        break
    paths.append(p)

if len(paths) < 2:
    print("Need at least 2 images for a carousel.")
    exit(1)

caption = input("Caption (optional): ").strip()

# Upload all images
children = []
for i, p in enumerate(paths):
    with open(p, "rb") as f:
        result = api.upload_photo(f.read())
    print(f"  Uploaded {i+1}/{len(paths)}: {result.upload_id}")
    children.append({"upload_id": result.upload_id})

# Publish carousel
result = api.configure_sidecar(children, caption=caption)
if result.media:
    print(f"Published carousel! pk={result.media.pk}")
    print(f"URL: https://www.instagram.com/p/{result.media.code}/")
else:
    print(f"Failed: {result.status}")
