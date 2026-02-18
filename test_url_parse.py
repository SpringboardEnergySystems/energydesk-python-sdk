#!/usr/bin/env python3
"""
Quick verification script to test URL parsing
"""
import re

# Your actual URL (note the missing '/' in the original)
url_with_space = "https://login.microsoftonline.com/20d3c681-9982-4395-abd6-7973f7e0f26a oauth2/v2.0/authorize"
url_correct = "https://login.microsoftonline.com/20d3c681-9982-4395-abd6-7973f7e0f26a/oauth2/v2.0/authorize"

print("Testing URL parsing:")
print("=" * 70)

for label, test_url in [("With space (malformed)", url_with_space), ("Correct format", url_correct)]:
    print(f"\n{label}:")
    print(f"  URL: {test_url}")

    if 'login.microsoftonline.com/' in test_url:
        match = re.search(r'login\.microsoftonline\.com/([^/\s]+)', test_url)
        if match:
            tenant = match.group(1)
            print(f"  ✅ Extracted tenant: {tenant}")
        else:
            print(f"  ❌ No match found")
    else:
        print(f"  ❌ Not an Azure URL")

print("\n" + "=" * 70)
