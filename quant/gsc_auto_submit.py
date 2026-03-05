#!/usr/bin/env python3
"""
Google Search Console Auto-Submission via OAuth2
Automatically submits sitemaps to GSC daily (can be run via GitHub Actions)
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
import requests
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.auth.exceptions import GoogleAuthError

# Configuration for 4 sites
SITES_CONFIG = {
    'credit': {
        'domain': 'cardclassroom.com',
        'property_url': 'https://cardclassroom.com/',
    },
    'calc': {
        'domain': 'dividendengines.com',
        'property_url': 'https://dividendengines.com/',
    },
    'affiliate': {
        'domain': 'thestackguide.com',
        'property_url': 'https://thestackguide.com/',
    },
    'quant': {
        'domain': 'quantengines.com',
        'property_url': 'https://quantengines.com/',
    }
}

SITEMAP_ENDPOINT = "https://www.googleapis.com/webmasters/v3/sites/{site_url}/sitemaps/{sitemap_url}"


class GSCAutoSubmitter:
    """Handles OAuth2 authentication and sitemap submission to Google Search Console"""

    def __init__(self, service_account_json: str):
        """
        Initialize with service account credentials

        Args:
            service_account_json: Path to Google Cloud service account JSON file
                                 (or JSON string if from environment variable)
        """
        self.credentials = None
        self.access_token = None
        self.load_credentials(service_account_json)

    def load_credentials(self, service_account_json: str):
        """Load and validate Google Cloud credentials"""
        try:
            # Try as file path first
            if os.path.isfile(service_account_json):
                with open(service_account_json) as f:
                    service_account_info = json.load(f)
            else:
                # Try as JSON string
                service_account_info = json.loads(service_account_json)

            # Create credentials with Search Console scope
            self.credentials = Credentials.from_service_account_info(
                service_account_info,
                scopes=['https://www.googleapis.com/auth/webmasters']
            )

            # Refresh to get access token
            self.credentials.refresh(Request())
            self.access_token = self.credentials.token

            print("✅ Google Cloud credentials loaded successfully")
        except (FileNotFoundError, json.JSONDecodeError, GoogleAuthError) as e:
            print(f"❌ Failed to load credentials: {e}")
            sys.exit(1)

    def submit_sitemap(self, site_name: str, site_url: str, sitemap_url: str = 'sitemap.xml') -> bool:
        """
        Submit sitemap to Google Search Console

        Args:
            site_name: Human-readable site name (for logging)
            site_url: Property URL in GSC (e.g., 'https://example.com/')
            sitemap_url: Sitemap endpoint (e.g., 'sitemap.xml')

        Returns:
            True if submission succeeded, False otherwise
        """
        if not self.access_token:
            print(f"❌ {site_name}: No access token available")
            return False

        # Build submission URL
        sitemap_full_url = f"{site_url}{sitemap_url}"
        endpoint = SITEMAP_ENDPOINT.format(
            site_url=site_url,
            sitemap_url=sitemap_url
        )

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        try:
            # First, check if sitemap already exists
            response = requests.get(endpoint, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                print(f"✅ {site_name}: Sitemap already submitted")
                print(f"   Indexed URLs: {data.get('contents', [{}])[0].get('indexed', 'N/A')}")
                print(f"   Pending URLs: {data.get('contents', [{}])[0].get('pending', 'N/A')}")
                print(f"   Errors: {data.get('contents', [{}])[0].get('errors', 'N/A')}")
                return True

            elif response.status_code == 404:
                # Sitemap not submitted yet - submit it
                post_response = requests.put(
                    endpoint,
                    headers=headers,
                    timeout=10
                )

                if post_response.status_code in [200, 204]:
                    print(f"✅ {site_name}: Sitemap submitted successfully")
                    print(f"   URL: {sitemap_full_url}")
                    return True
                else:
                    print(f"❌ {site_name}: Submission failed with status {post_response.status_code}")
                    print(f"   Response: {post_response.text[:200]}")
                    return False

            else:
                print(f"❌ {site_name}: Unexpected status {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ {site_name}: Request failed: {e}")
            return False

    def submit_all_sitemaps(self) -> Dict[str, bool]:
        """Submit sitemaps for all 4 sites"""
        results = {}

        print(f"\n{'='*70}")
        print(f"🚀 Google Search Console Auto-Submission")
        print(f"{'='*70}")
        print(f"Timestamp: {datetime.now().isoformat()}\n")

        for site_name, config in SITES_CONFIG.items():
            print(f"Submitting {site_name.upper()} ({config['domain']})...")
            success = self.submit_sitemap(
                site_name.upper(),
                config['property_url'],
                'sitemap.xml'
            )
            results[site_name] = success
            print()

        # Summary
        successful = sum(1 for v in results.values() if v)
        total = len(results)

        print(f"{'='*70}")
        print(f"📊 Summary")
        print(f"{'='*70}")
        print(f"Total: {total} | ✅ {successful} | ❌ {total - successful}")
        print(f"Success rate: {(successful/total)*100:.1f}%")

        return results


def main():
    """Main execution function"""
    # Get credentials from environment or file
    creds_source = os.environ.get('GCP_SERVICE_ACCOUNT')

    if not creds_source:
        # Try default path
        default_path = Path.home() / '.config' / 'gcp' / 'service-account.json'
        if default_path.exists():
            creds_source = str(default_path)
        else:
            print("❌ Error: No Google Cloud credentials found")
            print("\nSetup options:")
            print("1. Set environment variable: export GCP_SERVICE_ACCOUNT='<json>'")
            print("2. Place credentials at: ~/.config/gcp/service-account.json")
            print("3. Create Google Cloud service account: https://console.cloud.google.com/iam-admin/serviceaccounts")
            sys.exit(1)

    # Initialize and submit
    submitter = GSCAutoSubmitter(creds_source)
    results = submitter.submit_all_sitemaps()

    # Return exit code based on results
    if all(results.values()):
        print("\n✅ All sitemaps submitted successfully!")
        return 0
    else:
        print(f"\n⚠️ Some sitemaps failed to submit")
        return 1


if __name__ == '__main__':
    sys.exit(main())
