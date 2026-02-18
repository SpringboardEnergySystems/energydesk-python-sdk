#!/bin/bash
#
# Script to install the local SDK version for testing the Azure tenant fix
#

set -e

echo "=================================================="
echo "Installing Local SDK for Azure Tenant Fix Testing"
echo "=================================================="
echo ""

cd /Users/steinar/PycharmProjects/energydesk-portal

echo "Step 1: Uninstalling git-based SDK (if present)..."
pip uninstall -y energydesk-python-sdk || true

echo ""
echo "Step 2: Installing local SDK in editable mode..."
pip install -e /Users/steinar/PycharmProjects/energydesk-python-sdk

echo ""
echo "✅ Local SDK installed successfully!"
echo ""
echo "The portal will now use the updated auth_django.py with tenant extraction."
echo ""
echo "To verify, check that the SDK is installed from the local path:"
pip show energydesk-python-sdk | grep Location

echo ""
echo "=================================================="
echo "Next Steps:"
echo "=================================================="
echo "1. Restart your Django development server"
echo "2. Try logging in with Azure AD"
echo "3. Check the logs for debug output like:"
echo "   [DEBUG] Extracted Azure tenant from OIDC_OP_AUTHORIZATION_ENDPOINT: 20d3c681-..."
echo "   [DEBUG] ✅ Azure provider added to config with tenant: 20d3c681-..."
echo ""
echo "To revert to git-based SDK later:"
echo "  pip uninstall energydesk-python-sdk"
echo "  pip install git+https://github.com/SpringboardEnergySystems/energydesk-python-sdk.git@develop"
echo ""
