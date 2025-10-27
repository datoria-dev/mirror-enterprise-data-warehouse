"""
CrowdStrike Falcon API Connector
=================================
Purpose: Extract detection and endpoint data from CrowdStrike Falcon API
API Documentation: https://falcon.crowdstrike.com/documentation/
Authentication: OAuth 2.0 Client Credentials
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging
from api_connector_base import APIConnectorBase, APIConfig


class CrowdStrikeConnector(APIConnectorBase):
    """
    CrowdStrike Falcon API connector.

    Endpoints:
    - /detects/queries/detects/v1 - Detection IDs
    - /detects/entities/summaries/GET/v1 - Detection details
    - /devices/queries/devices/v1 - Device IDs
    - /devices/entities/devices/v1 - Device details
    """

    def __init__(self, client_id: str, client_secret: str, snowflake_config: Dict[str, str]):
        """
        Initialize CrowdStrike connector.

        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            snowflake_config: Snowflake connection parameters
        """
        config = APIConfig(
            service_name='CrowdStrike',
            base_url='https://api.crowdstrike.com',
            auth_type='oauth',
            api_version='v1',
            rate_limit_per_hour=5000,
            timeout_seconds=60,
            max_retries=3
        )

        super().__init__(config, snowflake_config)
        self.client_id = client_id
        self.client_secret = client_secret

    def authenticate(self) -> str:
        """
        Authenticate using OAuth 2.0 client credentials.

        Returns:
            Access token

        Raises:
            AuthenticationError: If authentication fails
        """
        if self._access_token and self._token_expiry:
            if datetime.utcnow() < self._token_expiry:
                return self._access_token

        token_url = f"{self.config.base_url}/oauth2/token"

        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        try:
            response = self.make_api_request(
                method='POST',
                url=token_url,
                data=data
            )

            token_data = response.json()
            self._access_token = token_data['access_token']
            self._token_expiry = datetime.utcnow() + timedelta(seconds=token_data.get('expires_in', 1800))

            self.logger.info("✅ CrowdStrike authentication successful")
            return self._access_token

        except Exception as e:
            self.logger.error(f"❌ Authentication failed: {e}")
            raise

    def extract_data(self, endpoint: str, params: Dict) -> List[Dict]:
        """
        Extract data from CrowdStrike API.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            List of records
        """
        # Get access token
        token = self.authenticate()

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        # CrowdStrike uses a two-step process:
        # 1. Query for IDs
        # 2. Get details for IDs

        if 'detects/queries' in endpoint:
            return self._extract_detections(headers, params)
        elif 'devices/queries' in endpoint:
            return self._extract_devices(headers, params)
        else:
            raise ValueError(f"Unsupported endpoint: {endpoint}")

    def _extract_detections(self, headers: Dict, params: Dict) -> List[Dict]:
        """
        Extract detections using two-step process.

        Args:
            headers: Request headers
            params: Query parameters

        Returns:
            List of detection records
        """
        # Step 1: Get detection IDs
        query_url = f"{self.config.base_url}/detects/queries/detects/v1"

        filter_str = self._build_filter(params)
        query_params = {
            'filter': filter_str,
            'limit': 500,
            'offset': 0
        }

        all_detection_ids = []

        while True:
            response = self.make_api_request(
                method='GET',
                url=query_url,
                headers=headers,
                params=query_params
            )

            data = response.json()
            detection_ids = data.get('resources', [])

            if not detection_ids:
                break

            all_detection_ids.extend(detection_ids)
            self.logger.info(f"Retrieved {len(detection_ids)} detection IDs (total: {len(all_detection_ids)})")

            # Check if more pages
            if len(detection_ids) < query_params['limit']:
                break

            query_params['offset'] += query_params['limit']

        # Step 2: Get detection details in batches
        details_url = f"{self.config.base_url}/detects/entities/summaries/GET/v1"
        all_detections = []

        batch_size = 100
        for i in range(0, len(all_detection_ids), batch_size):
            batch_ids = all_detection_ids[i:i + batch_size]

            response = self.make_api_request(
                method='POST',
                url=details_url,
                headers=headers,
                json_data={'ids': batch_ids}
            )

            data = response.json()
            detections = data.get('resources', [])
            all_detections.extend(detections)

            self.logger.info(f"Retrieved details for batch {i//batch_size + 1}: {len(detections)} detections")

        return all_detections

    def _extract_devices(self, headers: Dict, params: Dict) -> List[Dict]:
        """
        Extract devices using two-step process.

        Args:
            headers: Request headers
            params: Query parameters

        Returns:
            List of device records
        """
        # Step 1: Get device IDs
        query_url = f"{self.config.base_url}/devices/queries/devices/v1"

        filter_str = self._build_filter(params)
        query_params = {
            'filter': filter_str,
            'limit': 500,
            'offset': 0
        }

        all_device_ids = []

        while True:
            response = self.make_api_request(
                method='GET',
                url=query_url,
                headers=headers,
                params=query_params
            )

            data = response.json()
            device_ids = data.get('resources', [])

            if not device_ids:
                break

            all_device_ids.extend(device_ids)
            self.logger.info(f"Retrieved {len(device_ids)} device IDs (total: {len(all_device_ids)})")

            if len(device_ids) < query_params['limit']:
                break

            query_params['offset'] += query_params['limit']

        # Step 2: Get device details
        details_url = f"{self.config.base_url}/devices/entities/devices/v1"
        all_devices = []

        batch_size = 100
        for i in range(0, len(all_device_ids), batch_size):
            batch_ids = all_device_ids[i:i + batch_size]

            response = self.make_api_request(
                method='GET',
                url=details_url,
                headers=headers,
                params={'ids': batch_ids}
            )

            data = response.json()
            devices = data.get('resources', [])
            all_devices.extend(devices)

            self.logger.info(f"Retrieved details for batch {i//batch_size + 1}: {len(devices)} devices")

        return all_devices

    def _build_filter(self, params: Dict) -> str:
        """
        Build CrowdStrike filter query string.

        Args:
            params: Parameters including 'since' timestamp

        Returns:
            Filter string
        """
        filters = []

        if 'since' in params:
            # CrowdStrike uses timestamps in milliseconds
            since_dt = datetime.fromisoformat(params['since'].replace('Z', '+00:00'))
            since_ms = int(since_dt.timestamp() * 1000)
            filters.append(f"created_timestamp:>'{since_ms}'")

        if 'severity' in params:
            filters.append(f"max_severity:'{params['severity']}'")

        return '+'.join(filters) if filters else ''


# Example usage
if __name__ == "__main__":
    from datetime import timedelta

    # Configuration
    crowdstrike_config = {
        'client_id': 'your_client_id',
        'client_secret': 'your_client_secret'
    }

    snowflake_config = {
        'user': 'your_snowflake_user',
        'password': 'your_password',
        'account': 'your_account',
        'warehouse': 'DEV_WH',
        'database': 'DEV_LANDING',
        'schema': 'CROWDSTRIKE'
    }

    # Run extraction
    with CrowdStrikeConnector(
        client_id=crowdstrike_config['client_id'],
        client_secret=crowdstrike_config['client_secret'],
        snowflake_config=snowflake_config
    ) as connector:

        # Extract detections
        metadata = connector.run_incremental_extraction('/detects/queries/detects/v1')
        print(f"Extraction Status: {metadata.extraction_status}")
        print(f"Records Extracted: {metadata.records_extracted}")

        # Extract devices
        metadata = connector.run_incremental_extraction('/devices/queries/devices/v1')
        print(f"Extraction Status: {metadata.extraction_status}")
        print(f"Records Extracted: {metadata.records_extracted}")
