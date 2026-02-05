"""
Authentication modules for EnergyDesk API

- auth_fastapi: OIDC authentication for FastAPI applications
- auth_django: OIDC authentication for Django applications
"""

# Django authentication components
try:
    from .auth_django import (
        DjangoOIDCAuth,
        OIDCAuthMiddleware,
        create_auth_from_settings
    )
    __all_django__ = ['DjangoOIDCAuth', 'OIDCAuthMiddleware', 'create_auth_from_settings']
except ImportError:
    # Django not installed
    __all_django__ = []

# FastAPI authentication components
try:
    from .auth_fastapi import FastAPIOIDCAuth
    __all_fastapi__ = ['FastAPIOIDCAuth']
except ImportError:
    # FastAPI not installed
    __all_fastapi__ = []

__all__ = __all_django__ + __all_fastapi__
