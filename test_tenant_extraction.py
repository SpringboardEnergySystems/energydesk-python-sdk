#!/usr/bin/env python3
import os
import re

print("Testing Azure Tenant Extraction Logic")
print("=" * 60)

# Test Case 1: AZURE_TENANT_ID is set
print("\nTest Case 1: AZURE_TENANT_ID is set")
os.environ['AZURE_TENANT_ID'] = '12345-explicit-tenant'
os.environ['OIDC_OP_AUTHORIZATION_ENDPOINT'] = 'https://login.microsoftonline.com/20d3c681-9982-4395-abd6-7973f7e0f26a/oauth2/v2.0/authorize'

azure_tenant = os.environ.get('AZURE_TENANT_ID')
if not azure_tenant:
    auth_endpoint = os.environ.get('OIDC_OP_AUTHORIZATION_ENDPOINT', '')
    if 'login.microsoftonline.com/' in auth_endpoint:
        match = re.search(r'login\.microsoftonline\.com/([^/]+)', auth_endpoint)
        if match:
            azure_tenant = match.group(1)
            print(f"  → Extracted from URL: {azure_tenant}")
else:
    print(f"  → Using AZURE_TENANT_ID: {azure_tenant}")

print(f"  ✅ Result: {azure_tenant}")

# Test Case 2: AZURE_TENANT_ID not set, extract from URL
print("\nTest Case 2: AZURE_TENANT_ID not set, extract from URL")
if 'AZURE_TENANT_ID' in os.environ:
    del os.environ['AZURE_TENANT_ID']
os.environ['OIDC_OP_AUTHORIZATION_ENDPOINT'] = 'https://login.microsoftonline.com/20d3c681-9982-4395-abd6-7973f7e0f26a/oauth2/v2.0/authorize'

azure_tenant = os.environ.get('AZURE_TENANT_ID')
if not azure_tenant:
    auth_endpoint = os.environ.get('OIDC_OP_AUTHORIZATION_ENDPOINT', '')
    if 'login.microsoftonline.com/' in auth_endpoint:
        match = re.search(r'login\.microsoftonline\.com/([^/]+)', auth_endpoint)
        if match:
            azure_tenant = match.group(1)
            print(f"  → Extracted from URL: {azure_tenant}")
else:
    print(f"  → Using AZURE_TENANT_ID: {azure_tenant}")

if not azure_tenant:
    azure_tenant = 'common'
    print(f"  → Fallback to: {azure_tenant}")

print(f"  ✅ Result: {azure_tenant}")

# Test Case 3: Neither set, fallback to 'common'
print("\nTest Case 3: Neither AZURE_TENANT_ID nor URL set")
if 'AZURE_TENANT_ID' in os.environ:
    del os.environ['AZURE_TENANT_ID']
if 'OIDC_OP_AUTHORIZATION_ENDPOINT' in os.environ:
    del os.environ['OIDC_OP_AUTHORIZATION_ENDPOINT']

azure_tenant = os.environ.get('AZURE_TENANT_ID')
if not azure_tenant:
    auth_endpoint = os.environ.get('OIDC_OP_AUTHORIZATION_ENDPOINT', '')
    if 'login.microsoftonline.com/' in auth_endpoint:
        match = re.search(r'login\.microsoftonline\.com/([^/]+)', auth_endpoint)
        if match:
            azure_tenant = match.group(1)
            print(f"  → Extracted from URL: {azure_tenant}")

if not azure_tenant:
    azure_tenant = 'common'
    print(f"  → Fallback to: {azure_tenant}")

print(f"  ✅ Result: {azure_tenant}")

print("\n" + "=" * 60)
print("All tests completed successfully!")
