#!/usr/bin/env python
"""
Quick test to verify Google ID token structure
This shows what claims are in a Google ID token vs access token
"""

import base64
import json

# Example Google ID Token (this is a sample - yours will be different)
# ID tokens are JWTs with this structure: header.payload.signature
EXAMPLE_ID_TOKEN = """
eyJhbGciOiJSUzI1NiIsImtpZCI6IjFlOWdkazcifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiIxMjM0NTY3ODkwLmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwiYXVkIjoiMTIzNDU2Nzg5MC5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbSIsInN1YiI6IjEwMzM3NjgxNjI4MjI3MTM1OTkyMSIsImVtYWlsIjoicy5yLmVyaWtzZW5AZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsIm5hbWUiOiJTdGVpbmFyIEVyaWtzZW4iLCJwaWN0dXJlIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EtL0FPaDE0R2dYWFhYWCIsImdpdmVuX25hbWUiOiJTdGVpbmFyIiwiZmFtaWx5X25hbWUiOiJFcmlrc2VuIiwiaWF0IjoxNjQ2MTI4ODAwLCJleHAiOjE2NDYxMzI0MDB9.signature
"""

# Example Google Access Token (opaque - not JWT!)
EXAMPLE_ACCESS_TOKEN = "ya29.a0Aa7MYirhlWYQR-Bk-iFxu_matTdxRO8gZrtrXXXXXXX"


def decode_jwt_payload(token):
    """Decode JWT payload without verification (for testing only)"""
    try:
        # Remove whitespace
        token = token.strip()
        
        # Split into parts
        parts = token.split('.')
        
        if len(parts) != 3:
            return None, f"Not a JWT - has {len(parts)} parts (expected 3)"
        
        # Decode payload (second part)
        payload_b64 = parts[1]
        # Add padding if needed
        payload_b64 += '=' * (4 - len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        
        return payload, None
    except Exception as e:
        return None, str(e)


def analyze_token(token, name):
    """Analyze a token and print its structure"""
    print(f"\n{'='*60}")
    print(f"{name}")
    print(f"{'='*60}")
    
    print(f"\nToken length: {len(token)}")
    print(f"First 50 chars: {token[:50]}...")
    
    # Check if it looks like a JWT
    dot_count = token.count('.')
    print(f"Number of dots: {dot_count}")
    
    if dot_count == 2:
        print("✅ Format: JWT (has 3 parts: header.payload.signature)")
        
        payload, error = decode_jwt_payload(token)
        if payload:
            print("\n📋 Decoded Payload Claims:")
            print(json.dumps(payload, indent=2))
            
            # Check for important claims
            print("\n🔍 Key Claims for Django Authentication:")
            print(f"  - Issuer (iss): {payload.get('iss', 'MISSING ❌')}")
            print(f"  - Email: {payload.get('email', 'MISSING ❌')}")
            print(f"  - Subject (sub): {payload.get('sub', 'MISSING ❌')}")
            print(f"  - Audience (aud): {payload.get('aud', 'MISSING ❌')}")
            print(f"  - Expiration: {payload.get('exp', 'MISSING ❌')}")
            
            # Check if Django can use this
            if 'email' in payload:
                print("\n✅ Django's JWTEnergydeskAuthentication CAN validate this!")
                print("   Reason: Contains 'email' claim")
            else:
                print("\n❌ Django's JWTEnergydeskAuthentication CANNOT validate this!")
                print("   Reason: Missing 'email' claim")
        else:
            print(f"\n❌ Error decoding payload: {error}")
    else:
        print("❌ Format: OPAQUE (not JWT)")
        print("   Django's JWTEnergydeskAuthentication will SKIP this token")
        print("   (It checks: token.count('.') == 2)")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("GOOGLE TOKEN ANALYSIS")
    print("="*60)
    
    print("\nThis demonstrates why we need to use ID tokens for Google:")
    
    # Analyze ID Token
    analyze_token(EXAMPLE_ID_TOKEN.strip(), "GOOGLE ID TOKEN")
    
    # Analyze Access Token
    analyze_token(EXAMPLE_ACCESS_TOKEN, "GOOGLE ACCESS TOKEN")
    
    print("\n" + "="*60)
    print("CONCLUSION")
    print("="*60)
    print("""
Google provides TWO tokens:

1. ACCESS TOKEN (opaque):
   - Format: ya29.a0Aa7MYirhl... (no dots)
   - Purpose: Call Google APIs (Gmail, Drive, etc.)
   - Can Django validate? ❌ NO - it's opaque
   
2. ID TOKEN (JWT):
   - Format: eyJhbGci... (3 parts separated by dots)
   - Purpose: Identify user to your application
   - Can Django validate? ✅ YES - contains email claim
   
THE FIX: Use ID token for Google, access token for Azure/Django
    """)
    
    print("\n✅ The fix has been applied to auth_fastapi.py")
    print("   Google users now use ID tokens ✅")
    print("   Azure users still use access tokens (which are JWTs) ✅")
    print("   Django OAuth users still use access tokens ✅")
    print("\n" + "="*60 + "\n")

