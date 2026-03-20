"""Example: View DM inbox and send a message."""
from _common import get_api

api = get_api()

# Fetch DM inbox
inbox = api.direct_inbox()
threads = inbox.inbox.threads or []
print(f"DM threads: {len(threads)}")

for i, thread in enumerate(threads[:10]):
    names = ", ".join(u.username for u in (thread.users or []))
    last = thread.last_permanent_item
    text = ((last.text or "") if last else "")[:50]
    print(f"  [{i+1}] {names}: {text}")
    print(f"       thread_id={thread.thread_id}")

# Send a message
thread_id = input("\nEnter thread_id to send message (or skip): ").strip()
if thread_id:
    text = input("Message: ").strip()
    if text:
        result = api.direct_send_text(text, thread_ids=[thread_id])
        print(f"Send result: {result.status}")
