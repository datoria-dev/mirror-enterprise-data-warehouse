"""
API Integration Framework - Base Connector Class
=================================================
Purpose: Reusable framework for all API integrations in SECURITY_ANALYTICS DW
Architecture: Follows 3-layer medallion pattern (Landing → Transformation → Reporting)
Author: GenericCorp Data Engineering Team
Date: 2025-10-24
"""

import abc
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import snowflake.connector
from snowflake.connector import DictCursor
import uuid


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_integration.log'),
        logging.StreamHandler()
    ]
)


@dataclass
class APIConfig:
    """Configuration for API integration."""
    service_name: str
    base_url: str
    auth_type: str  # 'oauth', 'api_key', 'basic'
    api_version: str
    rate_limit_per_hour: int
    timeout_seconds: int = 60
    max_retries: int = 3
    backoff_factor: float = 2.0


@dataclass
class ExtractionMetadata:
    """Metadata for extraction logging."""
    extraction_id: str
    service_name: str
    api_endpoint: str
    extraction_type: str  # 'FULL' or 'INCREMENTAL'
    execution_start: datetime
    execution_end: Optional[datetime] = None
    records_extracted: int = 0
    extraction_status: str = 'IN_PROGRESS'  # IN_PROGRESS, SUCCESS, FAILED, PARTIAL
    error_message: Optional[str] = None
    last_extraction_timestamp: Optional[datetime] = None


class APIConnectorBase(abc.ABC):
    """
    Abstract base class for all API integrations.

    This class provides:
    - Authentication management
    - HTTP retry logic with exponential backoff
    - Rate limiting handling
    - Snowflake connection management
    - Extraction metadata tracking
    - Landing layer data storage
    """

    def __init__(self, config: APIConfig, snowflake_config: Dict[str, str]):
        """
        Initialize API connector.

        Args:
            config: API configuration
            snowflake_config: Snowflake connection parameters
        """
        self.config = config
        self.snowflake_config = snowflake_config
        self.logger = logging.getLogger(f"{__name__}.{config.service_name}")
        self.session = self._create_http_session()
        self._snowflake_conn = None
        self._access_token = None
        self._token_expiry = None

    def _create_http_session(self) -> requests.Session:
        """
        Create HTTP session with retry logic.

        Returns:
            Configured requests.Session
        """
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    @property
    def snowflake_conn(self) -> snowflake.connector.SnowflakeConnection:
        """
        Get Snowflake connection (lazy initialization).

        Returns:
            Snowflake connection object
        """
        if self._snowflake_conn is None or self._snowflake_conn.is_closed():
            self.logger.info("Establishing Snowflake connection...")
            self._snowflake_conn = snowflake.connector.connect(
                user=self.snowflake_config['user'],
                password=self.snowflake_config['password'],
                account=self.snowflake_config['account'],
                warehouse=self.snowflake_config.get('warehouse', 'DEV_WH'),
                database=self.snowflake_config.get('database', 'DEV_LANDING'),
                schema=self.snowflake_config.get('schema', self.config.service_name),
                role=self.snowflake_config.get('role', 'DEV_DEVELOPER')
            )
            self.logger.info("✅ Snowflake connection established")
        return self._snowflake_conn

    @abc.abstractmethod
    def authenticate(self) -> str:
        """
        Authenticate with API and return access token.

        Returns:
            Access token string

        Raises:
            AuthenticationError: If authentication fails
        """
        pass

    @abc.abstractmethod
    def extract_data(self, endpoint: str, params: Dict[str, Any]) -> List[Dict]:
        """
        Extract data from API endpoint.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            List of records as dictionaries
        """
        pass

    def get_last_extraction_timestamp(self, api_endpoint: str) -> datetime:
        """
        Get timestamp of last successful extraction.

        Args:
            api_endpoint: API endpoint path

        Returns:
            Timestamp of last extraction (defaults to 7 days ago if none found)
        """
        query = """
            SELECT last_extraction_timestamp
            FROM DEV_TRANSFORMATION.METADATA.API_EXTRACTION_LOG
            WHERE service_name = %s
              AND api_endpoint = %s
              AND extraction_status = 'SUCCESS'
            ORDER BY extraction_id DESC
            LIMIT 1
        """

        try:
            cursor = self.snowflake_conn.cursor(DictCursor)
            cursor.execute(query, (self.config.service_name, api_endpoint))
            result = cursor.fetchone()

            if result and result['LAST_EXTRACTION_TIMESTAMP']:
                timestamp = result['LAST_EXTRACTION_TIMESTAMP']
                self.logger.info(f"Last extraction: {timestamp}")
                return timestamp
            else:
                # Default: 7 days ago
                default_timestamp = datetime.utcnow() - timedelta(days=7)
                self.logger.warning(f"No previous extraction found. Using default: {default_timestamp}")
                return default_timestamp

        except Exception as e:
            self.logger.error(f"Error getting last extraction timestamp: {e}")
            return datetime.utcnow() - timedelta(days=7)

    def load_to_landing(
        self,
        table_name: str,
        data: List[Dict],
        source_file: Optional[str] = None
    ) -> int:
        """
        Load raw data to DEV_LANDING layer.

        Args:
            table_name: Target table name (without schema)
            data: List of records to insert
            source_file: Optional source file name

        Returns:
            Number of records inserted
        """
        if not data:
            self.logger.warning("No data to insert")
            return 0

        # Prepare insert statement
        full_table_name = f"DEV_LANDING.{self.config.service_name}.{table_name}"

        insert_query = f"""
            INSERT INTO {full_table_name} (
                ingestion_id,
                ingestion_timestamp,
                source_file,
                raw_data,
                ingestion_date
            )
            SELECT
                column1,  -- UUID
                column2,  -- TIMESTAMP
                column3,  -- source_file
                PARSE_JSON(column4),  -- raw_data as VARIANT
                column5   -- DATE
            FROM VALUES
        """

        try:
            # Prepare batch data
            ingestion_timestamp = datetime.utcnow()
            ingestion_date = ingestion_timestamp.date()

            batch_data = [
                (
                    str(uuid.uuid4()),
                    ingestion_timestamp,
                    source_file or f"{self.config.service_name}_api_extraction",
                    json.dumps(record),
                    ingestion_date
                )
                for record in data
            ]

            # Insert in batches of 1000
            batch_size = 1000
            total_inserted = 0

            for i in range(0, len(batch_data), batch_size):
                batch = batch_data[i:i + batch_size]
                cursor = self.snowflake_conn.cursor()
                cursor.executemany(insert_query, batch)
                total_inserted += cursor.rowcount
                self.logger.info(f"Inserted batch {i//batch_size + 1}: {cursor.rowcount} records")

            self.snowflake_conn.commit()
            self.logger.info(f"✅ Total inserted to {full_table_name}: {total_inserted} records")
            return total_inserted

        except Exception as e:
            self.logger.error(f"Error loading to landing: {e}")
            self.snowflake_conn.rollback()
            raise

    def log_extraction(self, metadata: ExtractionMetadata) -> None:
        """
        Log extraction metadata to tracking table.

        Args:
            metadata: Extraction metadata object
        """
        insert_query = """
            INSERT INTO DEV_TRANSFORMATION.METADATA.API_EXTRACTION_LOG (
                service_name,
                api_endpoint,
                extraction_type,
                last_extraction_timestamp,
                records_extracted,
                extraction_status,
                error_message,
                execution_start,
                execution_end
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        try:
            cursor = self.snowflake_conn.cursor()
            cursor.execute(insert_query, (
                metadata.service_name,
                metadata.api_endpoint,
                metadata.extraction_type,
                metadata.last_extraction_timestamp,
                metadata.records_extracted,
                metadata.extraction_status,
                metadata.error_message,
                metadata.execution_start,
                metadata.execution_end
            ))
            self.snowflake_conn.commit()
            self.logger.info("✅ Extraction metadata logged")

        except Exception as e:
            self.logger.error(f"Error logging extraction metadata: {e}")

    def handle_rate_limit(self, response: requests.Response) -> None:
        """
        Handle API rate limiting.

        Args:
            response: HTTP response object
        """
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            self.logger.warning(f"⏳ Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)

    def make_api_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> requests.Response:
        """
        Make HTTP request with error handling and retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL
            headers: Request headers
            params: Query parameters
            data: Form data
            json_data: JSON body

        Returns:
            Response object

        Raises:
            requests.RequestException: If request fails after retries
        """
        for attempt in range(self.config.max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    data=data,
                    json=json_data,
                    timeout=self.config.timeout_seconds
                )

                # Handle rate limiting
                if response.status_code == 429:
                    self.handle_rate_limit(response)
                    continue

                response.raise_for_status()
                return response

            except requests.exceptions.Timeout:
                wait_time = self.config.backoff_factor ** attempt
                self.logger.warning(f"Timeout on attempt {attempt + 1}. Retrying in {wait_time}s...")
                time.sleep(wait_time)

            except requests.exceptions.HTTPError as e:
                if e.response.status_code in [500, 502, 503, 504]:
                    # Server error - retry
                    wait_time = self.config.backoff_factor ** attempt
                    self.logger.warning(f"Server error {e.response.status_code}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    # Client error - don't retry
                    self.logger.error(f"Client error {e.response.status_code}: {e}")
                    raise

            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request exception: {e}")
                if attempt == self.config.max_retries - 1:
                    raise

        raise requests.exceptions.RequestException(f"Failed after {self.config.max_retries} attempts")

    def run_incremental_extraction(self, endpoint: str, params: Optional[Dict] = None) -> ExtractionMetadata:
        """
        Run incremental extraction workflow.

        Args:
            endpoint: API endpoint path
            params: Additional query parameters

        Returns:
            ExtractionMetadata object with results
        """
        metadata = ExtractionMetadata(
            extraction_id=str(uuid.uuid4()),
            service_name=self.config.service_name,
            api_endpoint=endpoint,
            extraction_type='INCREMENTAL',
            execution_start=datetime.utcnow()
        )

        try:
            # Get last extraction timestamp
            last_timestamp = self.get_last_extraction_timestamp(endpoint)
            metadata.last_extraction_timestamp = last_timestamp

            # Authenticate
            self.logger.info("🔐 Authenticating...")
            self.authenticate()

            # Extract data
            self.logger.info(f"📥 Extracting data from {endpoint} since {last_timestamp}...")
            if params is None:
                params = {}
            params['since'] = last_timestamp.isoformat()

            data = self.extract_data(endpoint, params)
            metadata.records_extracted = len(data)

            # Load to landing
            self.logger.info(f"💾 Loading {len(data)} records to landing...")
            table_name = self._get_table_name_from_endpoint(endpoint)
            self.load_to_landing(f"{table_name}_RAW", data)

            # Mark as success
            metadata.execution_end = datetime.utcnow()
            metadata.extraction_status = 'SUCCESS'
            self.logger.info(f"✅ Extraction completed: {metadata.records_extracted} records")

        except Exception as e:
            metadata.execution_end = datetime.utcnow()
            metadata.extraction_status = 'FAILED'
            metadata.error_message = str(e)
            self.logger.error(f"❌ Extraction failed: {e}")

        finally:
            # Log metadata
            self.log_extraction(metadata)

        return metadata

    def _get_table_name_from_endpoint(self, endpoint: str) -> str:
        """
        Convert API endpoint to table name.

        Args:
            endpoint: API endpoint path

        Returns:
            Table name
        """
        # Example: /api/v1/detections → DETECTIONS
        return endpoint.strip('/').split('/')[-1].upper()

    def close(self) -> None:
        """Close connections."""
        if self._snowflake_conn and not self._snowflake_conn.is_closed():
            self._snowflake_conn.close()
            self.logger.info("Snowflake connection closed")
        self.session.close()
        self.logger.info("HTTP session closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
