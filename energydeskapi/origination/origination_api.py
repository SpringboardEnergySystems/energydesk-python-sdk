"""
API wrappers for energydesk.apps.origination's DealPackage / PackageVersion
endpoints (plans/multi_leg_deals.md, appserver PR #415 "DealPackage
origination completion", merged - new DealPackage/PackageVersion models,
firm-offer/credit gates, multi-leg booking).

Same static-method + ApiConnection style as
energydeskapi/agreements/agreements_api.py::AgreementsApi.

Endpoint paths and action names are the ones from the appserver's actual
urls.py (energydesk/apps/origination/urls.py) and
interfaces/restmodel.py::DealPackageViewSet / PackageVersionViewSet, both
verified on merged PR #415:

  GET  /api/origination/packages/
  GET  /api/origination/packages/embedded/
  GET  /api/origination/packages/{pk}/
  POST /api/origination/packages/                    (create)
  POST /api/origination/packages/{pk}/add_leg/
  POST /api/origination/packages/{pk}/remove_leg/
  POST /api/origination/packages/{pk}/select_version/
  POST /api/origination/packages/{pk}/submit/
  POST /api/origination/packages/{pk}/quote/
  POST /api/origination/packages/{pk}/publish/
  GET  /api/origination/packages/{pk}/timeline/
  GET  /api/origination/packages/{pk}/versions_list/
  GET  /api/origination/package-versions/
  GET  /api/origination/package-versions/{pk}/       (read-only - a package
                                                        version is immutable
                                                        once created)

Request bodies are the corresponding
energydeskapi.types.multi_leg_deals.pydantic_types.*Write type, serialized
with `.model_dump(mode="json")` by the caller before passing in (same
convention as energydeskapi.agreements.margining_api's *Write bodies) -
these wrappers accept plain dicts so callers aren't forced through pydantic
if they already have one.

`quote` and `publish` deliberately do NOT accept a `kind` parameter:
restmodel.py::DealPackageViewSet._publish validates the request body
against PublishPackageOfferInput (so `kind` is required server-side or the
request 400s) but then ignores the validated value and forces
kind="INDICATIVE"/"FIRM" depending on which URL was called. This wrapper
sets `kind` internally to the matching literal so that oddity never leaks
into the SDK's public surface - see this PR's description for a suggested
appserver follow-up.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from energydeskapi.sdk.api_connection import ApiConnection

logger = logging.getLogger(__name__)


class OriginationApi:
    """DealPackage / PackageVersion - multi-leg deal origination."""

    @staticmethod
    def get_packages(api_connection: ApiConnection, parameters: dict = {}) -> Any:
        logger.info("Listing packages")
        return api_connection.exec_get_url("/api/origination/packages/", parameters)

    @staticmethod
    def get_packages_embedded(api_connection: ApiConnection, parameters: dict = {}) -> Any:
        logger.info("Listing packages embedded")
        return api_connection.exec_get_url("/api/origination/packages/embedded/", parameters)

    @staticmethod
    def get_package(api_connection: ApiConnection, package_pk: int) -> Any:
        logger.info("Loading package %s", package_pk)
        return api_connection.exec_get_url(f"/api/origination/packages/{package_pk}/")

    @staticmethod
    def create_package(api_connection: ApiConnection, package: dict) -> Any:
        """`package` is a energydeskapi.types.multi_leg_deals.CreatePackageWrite
        -shaped dict."""
        logger.info("Creating package")
        return api_connection.exec_post_url("/api/origination/packages/", package)

    @staticmethod
    def add_leg(api_connection: ApiConnection, package_pk: int, leg: dict) -> Any:
        """`leg` is a energydeskapi.types.multi_leg_deals.AddLegWrite-shaped
        dict. Returns the new leg (Deal) - see
        energydeskapi.types.multi_leg_deals.Leg for the wire shape."""
        logger.info("Adding leg to package %s", package_pk)
        return api_connection.exec_post_url(f"/api/origination/packages/{package_pk}/add_leg/", leg)

    @staticmethod
    def remove_leg(api_connection: ApiConnection, package_pk: int, deal_pk: int, comment: str = "") -> Any:
        """`deal_pk` is the leg's Deal pk (RemoveLegInput's `deal` field)."""
        logger.info("Removing leg %s from package %s", deal_pk, package_pk)
        body = {"deal": deal_pk, "comment": comment}
        return api_connection.exec_post_url(f"/api/origination/packages/{package_pk}/remove_leg/", body)

    @staticmethod
    def select_version(api_connection: ApiConnection, package_pk: int, package_version_pk: int) -> Any:
        logger.info("Selecting version %s for package %s", package_version_pk, package_pk)
        body = {"package_version": package_version_pk}
        return api_connection.exec_post_url(f"/api/origination/packages/{package_pk}/select_version/", body)

    @staticmethod
    def submit(api_connection: ApiConnection, package_pk: int, comment: str = "") -> Any:
        logger.info("Submitting package %s for approval", package_pk)
        body = {"comment": comment} if comment else {}
        return api_connection.exec_post_url(f"/api/origination/packages/{package_pk}/submit/", body)

    @staticmethod
    def quote(api_connection: ApiConnection, package_pk: int, offer: dict) -> Any:
        """Publish an INDICATIVE offer (a quote) - does not change
        package.status. `offer` is a
        energydeskapi.types.multi_leg_deals.PublishPackageOfferWrite-shaped
        dict (no `kind` field - see module docstring, this injects it).
        Returns a ContractOfferSerializer-shaped dict - note it does not
        currently expose `package`/`package_version` (appserver gap, see
        this PR's description)."""
        logger.info("Publishing indicative offer for package %s", package_pk)
        body = dict(offer)
        body["kind"] = "INDICATIVE"
        return api_connection.exec_post_url(f"/api/origination/packages/{package_pk}/quote/", body)

    @staticmethod
    def publish(api_connection: ApiConnection, package_pk: int, offer: dict) -> Any:
        """Publish a FIRM offer - moves the package to PUBLISHED once the
        firm-offer and credit gates pass. `offer` is a
        energydeskapi.types.multi_leg_deals.PublishPackageOfferWrite-shaped
        dict (no `kind` field - see module docstring, this injects it).
        Returns a ContractOfferSerializer-shaped dict - same
        package/package_version gap noted in `quote`."""
        logger.info("Publishing firm offer for package %s", package_pk)
        body = dict(offer)
        body["kind"] = "FIRM"
        return api_connection.exec_post_url(f"/api/origination/packages/{package_pk}/publish/", body)

    @staticmethod
    def timeline(api_connection: ApiConnection, package_pk: int) -> Any:
        """Full DealStateTransition history across all legs of this
        package. Note: DealStateTransitionSerializer does not currently
        expose `package` (appserver gap, see this PR's description)."""
        logger.info("Loading timeline for package %s", package_pk)
        return api_connection.exec_get_url(f"/api/origination/packages/{package_pk}/timeline/")

    @staticmethod
    def versions_list(api_connection: ApiConnection, package_pk: int) -> Any:
        logger.info("Listing versions for package %s", package_pk)
        return api_connection.exec_get_url(f"/api/origination/packages/{package_pk}/versions_list/")

    @staticmethod
    def get_package_versions(api_connection: ApiConnection, parameters: dict = {}) -> Any:
        logger.info("Listing package versions")
        return api_connection.exec_get_url("/api/origination/package-versions/", parameters)

    @staticmethod
    def get_package_version(api_connection: ApiConnection, package_version_pk: int) -> Any:
        logger.info("Loading package version %s", package_version_pk)
        return api_connection.exec_get_url(f"/api/origination/package-versions/{package_version_pk}/")
