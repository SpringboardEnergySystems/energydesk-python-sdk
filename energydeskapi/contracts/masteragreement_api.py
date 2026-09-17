"""
DEPRECATED - removed with appserver EDSK-929 (2024).

MasterAgreementApi targeted /api/portfoliomanager/mastercontractagreements/,
an endpoint that no longer exists - portfoliomanager.MasterContractAgreement
was dropped in migration 0021_delete_mastercontractagreement with no data
to carry over. The concept was revived, with a Contract link and commercial
content, as energydesk.apps.agreements.MasterAgreement
(plans/customer_account_model.md step 1, merged).

Use energydeskapi.agreements.agreements_api.AgreementsApi instead. This
module is kept only so `import energydeskapi.contracts.masteragreement_api`
does not break for any caller still holding a reference to it; every method
raises immediately.
"""
import logging

logger = logging.getLogger(__name__)

_REMOVED_MESSAGE = (
    "MasterAgreementApi was removed with appserver EDSK-929 (2024); "
    "the endpoint it called no longer exists. "
    "Use energydeskapi.agreements.agreements_api.AgreementsApi instead."
)


class MasterContractAgreement:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError(_REMOVED_MESSAGE)


class MasterAgreementApi:
    """Deprecated - see module docstring."""

    @staticmethod
    def get_master_agreements(*args, **kwargs):
        raise NotImplementedError(_REMOVED_MESSAGE)

    @staticmethod
    def get_master_agreements_embedded(*args, **kwargs):
        raise NotImplementedError(_REMOVED_MESSAGE)

    @staticmethod
    def get_master_agreements_by_key(*args, **kwargs):
        raise NotImplementedError(_REMOVED_MESSAGE)

    @staticmethod
    def upsert_master_agreement(*args, **kwargs):
        raise NotImplementedError(_REMOVED_MESSAGE)
