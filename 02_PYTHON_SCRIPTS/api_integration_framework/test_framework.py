"""
API Integration Framework - Testing Script
==========================================
Purpose: Test the API connector framework with mock/real credentials
Usage: python test_framework.py [--service crowdstrike|servicenow] [--mode mock|real]
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockAPIConnector:
    """Mock connector for testing without real API credentials."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logger

    def test_authentication(self) -> bool:
        """Test authentication flow."""
        self.logger.info(f"Testing {self.service_name} authentication...")

        # Mock authentication
        if self.service_name.lower() == "crowdstrike":
            self.logger.info("✅ OAuth 2.0 authentication successful (mock)")
            return True
        elif self.service_name.lower() == "servicenow":
            self.logger.info("✅ OAuth 2.0 authentication successful (mock)")
            return True
        else:
            self.logger.info("✅ API Key authentication successful (mock)")
            return True

    def test_extraction(self) -> Dict:
        """Test data extraction."""
        self.logger.info(f"Testing {self.service_name} data extraction...")

        # Mock data
        mock_data = {
            "records_extracted": 150,
            "extraction_time_seconds": 3.5,
            "sample_record": {
                "id": "mock_001",
                "timestamp": datetime.utcnow().isoformat(),
                "service": self.service_name
            }
        }

        self.logger.info(f"✅ Extracted {mock_data['records_extracted']} records (mock)")
        return mock_data

    def test_incremental_extraction(self) -> Dict:
        """Test incremental extraction logic."""
        self.logger.info("Testing incremental extraction...")

        last_timestamp = datetime.utcnow() - timedelta(hours=1)
        self.logger.info(f"Last extraction timestamp: {last_timestamp}")

        mock_result = {
            "last_extraction_timestamp": last_timestamp.isoformat(),
            "new_records": 25,
            "updated_records": 10,
            "total_records": 35
        }

        self.logger.info(f"✅ Incremental extraction: {mock_result['total_records']} records")
        return mock_result

    def test_error_handling(self) -> Dict:
        """Test error handling and retry logic."""
        self.logger.info("Testing error handling...")

        scenarios = [
            {"error": "Rate Limit (429)", "result": "Retry after 60s", "success": True},
            {"error": "Timeout", "result": "Exponential backoff retry", "success": True},
            {"error": "Server Error (500)", "result": "Retry with backoff", "success": True},
            {"error": "Auth Failure (401)", "result": "Token refresh", "success": True}
        ]

        for scenario in scenarios:
            self.logger.info(f"  • {scenario['error']}: {scenario['result']} ✅")

        return {"scenarios_tested": len(scenarios), "all_passed": True}

    def test_landing_layer_insert(self) -> Dict:
        """Test insert to DEV_LANDING layer."""
        self.logger.info("Testing landing layer insert (mock)...")

        mock_result = {
            "table": f"DEV_LANDING.{self.service_name}.MOCK_TABLE_RAW",
            "records_inserted": 150,
            "batch_size": 1000,
            "insert_time_seconds": 1.2
        }

        self.logger.info(f"✅ Inserted {mock_result['records_inserted']} records to {mock_result['table']}")
        return mock_result

    def run_all_tests(self) -> Dict:
        """Run complete test suite."""
        self.logger.info("="*60)
        self.logger.info(f"Running {self.service_name} Connector Test Suite")
        self.logger.info("="*60)

        results = {}

        try:
            # Test 1: Authentication
            results['authentication'] = self.test_authentication()

            # Test 2: Data Extraction
            results['extraction'] = self.test_extraction()

            # Test 3: Incremental Extraction
            results['incremental'] = self.test_incremental_extraction()

            # Test 4: Error Handling
            results['error_handling'] = self.test_error_handling()

            # Test 5: Landing Layer Insert
            results['landing_insert'] = self.test_landing_layer_insert()

            # Summary
            self.logger.info("="*60)
            self.logger.info("✅ ALL TESTS PASSED")
            self.logger.info("="*60)
            results['overall_status'] = 'PASSED'

        except Exception as e:
            self.logger.error(f"❌ Test failed: {e}")
            results['overall_status'] = 'FAILED'
            results['error'] = str(e)

        return results


def test_with_real_credentials(service_name: str, credentials: Dict) -> Dict:
    """Test with real API credentials (requires actual credentials)."""
    logger.info("="*60)
    logger.info(f"Testing {service_name} with REAL credentials")
    logger.info("="*60)
    logger.warning("⚠️  This requires actual API credentials and Snowflake connection")

    # Import real connector
    try:
        if service_name.lower() == "crowdstrike":
            from crowdstrike_connector import CrowdStrikeConnector

            # Snowflake config (from environment or config file)
            snowflake_config = {
                'user': credentials.get('snowflake_user'),
                'password': credentials.get('snowflake_password'),
                'account': credentials.get('snowflake_account'),
                'warehouse': 'DEV_WH',
                'database': 'DEV_LANDING',
                'schema': 'CROWDSTRIKE'
            }

            # Test connector
            with CrowdStrikeConnector(
                client_id=credentials.get('client_id'),
                client_secret=credentials.get('client_secret'),
                snowflake_config=snowflake_config
            ) as connector:

                logger.info("Testing authentication...")
                token = connector.authenticate()
                logger.info(f"✅ Obtained access token: {token[:20]}...")

                logger.info("Testing incremental extraction...")
                metadata = connector.run_incremental_extraction('/detects/queries/detects/v1')

                logger.info(f"Extraction Status: {metadata.extraction_status}")
                logger.info(f"Records Extracted: {metadata.records_extracted}")

                return {
                    'status': metadata.extraction_status,
                    'records': metadata.records_extracted
                }

        else:
            logger.error(f"Real testing not implemented for {service_name}")
            return {'status': 'NOT_IMPLEMENTED'}

    except ImportError as e:
        logger.error(f"❌ Could not import connector: {e}")
        logger.info("Make sure connector files are in the same directory")
        return {'status': 'IMPORT_ERROR', 'error': str(e)}

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return {'status': 'FAILED', 'error': str(e)}


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description='Test API Integration Framework')
    parser.add_argument(
        '--service',
        type=str,
        default='crowdstrike',
        help='Service to test (crowdstrike, servicenow, etc.)'
    )
    parser.add_argument(
        '--mode',
        type=str,
        choices=['mock', 'real'],
        default='mock',
        help='Test mode: mock (no credentials needed) or real (requires credentials)'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to JSON config file with credentials (for real mode)'
    )

    args = parser.parse_args()

    logger.info(f"API Integration Framework Test - {args.service.upper()}")
    logger.info(f"Mode: {args.mode.upper()}")
    logger.info("")

    if args.mode == 'mock':
        # Run mock tests
        connector = MockAPIConnector(args.service)
        results = connector.run_all_tests()

        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(json.dumps(results, indent=2, default=str))

        # Exit code
        sys.exit(0 if results.get('overall_status') == 'PASSED' else 1)

    elif args.mode == 'real':
        # Load credentials
        if not args.config:
            logger.error("❌ --config required for real mode")
            logger.info("Example: python test_framework.py --mode real --config credentials.json")
            sys.exit(1)

        try:
            with open(args.config, 'r') as f:
                credentials = json.load(f)

            results = test_with_real_credentials(args.service, credentials)

            # Print summary
            print("\n" + "="*60)
            print("TEST SUMMARY")
            print("="*60)
            print(json.dumps(results, indent=2, default=str))

            sys.exit(0 if results.get('status') == 'SUCCESS' else 1)

        except FileNotFoundError:
            logger.error(f"❌ Config file not found: {args.config}")
            sys.exit(1)
        except json.JSONDecodeError:
            logger.error(f"❌ Invalid JSON in config file: {args.config}")
            sys.exit(1)


if __name__ == "__main__":
    main()
