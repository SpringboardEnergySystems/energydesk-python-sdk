# SDK Changes - auth_django.py URL Prefix Fix

## Problem
The `auth_django.py` module was doubling the `/portal` prefix when generating URLs:

```python
# OLD CODE (WRONG):
script_name = request.META.get('SCRIPT_NAME', '')  # Returns '/portal'
return redirect(f'{script_name}{reverse_func("oidc_login")}')
# Result: /portal + /portal/auth/login/ = /portal/portal/auth/login/ ❌
```

## Root Cause
Django's `reverse()` function **already includes** the `URL_PREFIX` from settings, so prepending `SCRIPT_NAME` causes the prefix to appear twice.

## Changes Made

### Fixed: 5 redirect() calls
Removed `script_name` prefix from redirects to Django URLs:

1. **OIDCAuthMiddleware.__call__()** (line ~771)
2. **logout_view()** (line ~639)  
3. **profile_view()** (line ~648)
4. **require_oidc_auth decorator** (line ~732)
5. **login_view() provider URLs** (line ~175)

**Before:**
```python
return redirect(f'{script_name}{reverse_func("oidc_login")}')
```

**After:**
```python
return redirect(reverse_func("oidc_login"))
```

### Kept: Static file paths in HTML
`script_name` is **still used** for static file paths in HTML templates because they DO need the prefix:

```python
script_name = request.META.get('SCRIPT_NAME', '')  # Needed for static files
html = f'''
    <link rel="stylesheet" href="{script_name}/static/energydesk/app/css/bootstrap.css">
    <img src="{script_name}/static/energydesk/brightimages/edesk2.png">
'''
```

This is correct because static files aren't handled by Django's URL routing.

### Also Kept: Default redirect URLs
```python
next_url = request.session.get('oidc_next', f'{script_name}/')
```

This is correct because when there's no specific URL to redirect to, we need to redirect to the root with the prefix.

## Summary of Changes

| Location | Line | Change | Reason |
|----------|------|--------|--------|
| login_view | ~175 | Removed script_name from provider URLs | reverse() has prefix |
| logout_view | ~639 | Removed script_name from redirect | reverse() has prefix |
| profile_view | ~648 | Removed script_name from redirect | reverse() has prefix |
| require_oidc_auth | ~732 | Removed script_name from redirect | reverse() has prefix |
| OIDCAuthMiddleware | ~771 | Removed script_name from redirect | reverse() has prefix |
| HTML templates | multiple | **KEPT** script_name | Static files need prefix |
| Default URLs | ~622 | **KEPT** script_name | Root redirect needs prefix |

## Result

### Before:
```
User not authenticated
→ Middleware redirects to: /portal + /portal/auth/login/  
→ Final URL: /portal/portal/auth/login/
→ Redirect loop ❌
```

### After:
```
User not authenticated
→ Middleware redirects to: /portal/auth/login/ (from reverse())
→ Final URL: /portal/auth/login/
→ Works correctly ✅
```

## Testing

After deploying this change:

1. **Login redirect should work:**
   - Access protected page → Redirected to `/portal/auth/login/` ✅
   - NOT `/portal/portal/auth/login/` ❌

2. **Static files should still load:**
   - CSS, JS, images load correctly with `/portal/static/...` prefix ✅

3. **Provider selection should work:**
   - Login page shows Azure/Google buttons ✅
   - Clicking button redirects to correct URL ✅

4. **Logout should work:**
   - After logout, redirected to `/portal/auth/login/` ✅

## Deployment

This change is in the **energydesk-python-sdk** project, so you need to:

### Option 1: Install from local SDK
```bash
cd /Users/steinar/PycharmProjects/energydesk-python-sdk
pip install -e .

# Then rebuild portal
cd /Users/steinar/PycharmProjects/energydesk-portal
docker build -t springboardenergysystems/energydesk-portal:SRE_EURONEXT_COMPAT353 .
```

### Option 2: Commit SDK and install from git
```bash
cd /Users/steinar/PycharmProjects/energydesk-python-sdk
git add energydeskapi/auth/auth_django.py
git commit -m "Fix URL prefix doubling in auth redirects"
git push

# Update portal requirements to use latest SDK
cd /Users/steinar/PycharmProjects/energydesk-portal
# Edit buildconfig/requirements.git.txt to point to latest commit
docker build -t springboardenergysystems/energydesk-portal:SRE_EURONEXT_COMPAT353 .
```

## Files Changed
- `/Users/steinar/PycharmProjects/energydesk-python-sdk/energydeskapi/auth/auth_django.py`

## Portal Project Status
- ✅ OIDC URLs uncommented in `portal/energydesk_urls.py`
- ✅ Health checks use `port: 8001` in Kubernetes deployment
- ✅ Gunicorn timeout set to 180s in `buildconfig/entrypoint.sh`
- ✅ Health endpoints created in `energydesk/health.py`

---

**Date:** February 11, 2026
**Status:** SDK fixes complete, ready to rebuild portal
