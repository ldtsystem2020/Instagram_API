"""Example: View, post, and delete comments on a media."""
from _common import get_api

api = get_api()

media_id = input("Enter media_id (e.g. 3856391626629954283_8746461377): ").strip()

# Fetch comments
comments = api.media_comments(media_id)
print(f"\nComments (status={comments.status}):")

for c in (comments.comments or [])[:10]:
    print(f"  @{c.user.username}: {c.text}")
    print(f"    comment_id={c.pk}")

# Post a comment
text = input("\nPost a comment (or skip): ").strip()
if text:
    # Optional: check if offensive first
    check = api.check_offensive_comment(media_id, text)
    print(f"  Offensive check: {check.is_offensive}")

    result = api.media_comment(media_id, text)
    comment_pk = result.comment.pk if result.comment else None
    print(f"  Posted! comment_id={comment_pk}")

    # Delete it?
    if comment_pk and input("  Delete this comment? (y/n): ").strip().lower() == "y":
        api.media_comment_bulk_delete(media_id, [str(comment_pk)])
        print("  Deleted!")
