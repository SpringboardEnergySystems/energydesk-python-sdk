"""Regression guard: masteragreement_api.py must fail loudly, not silently
call a 404. See the module's docstring - the endpoint it wrapped was
removed from the appserver in 2024 (EDSK-929)."""
from unittest import TestCase

from energydeskapi.contracts.masteragreement_api import MasterAgreementApi, MasterContractAgreement


class TestMasterAgreementApiShim(TestCase):
    def test_instantiating_the_dataclass_raises(self):
        with self.assertRaises(NotImplementedError):
            MasterContractAgreement()

    def test_get_master_agreements_raises(self):
        with self.assertRaises(NotImplementedError):
            MasterAgreementApi.get_master_agreements(None)

    def test_get_master_agreements_embedded_raises(self):
        with self.assertRaises(NotImplementedError):
            MasterAgreementApi.get_master_agreements_embedded(None)

    def test_get_master_agreements_by_key_raises(self):
        with self.assertRaises(NotImplementedError):
            MasterAgreementApi.get_master_agreements_by_key(None, 1)

    def test_upsert_master_agreement_raises(self):
        with self.assertRaises(NotImplementedError):
            MasterAgreementApi.upsert_master_agreement(None, None)
