#!/usr/bin/env python3
"""
Contract tests for GET /api/motors/analytics/status endpoint
These tests MUST FAIL until the endpoint is implemented in T015
"""

import pytest
import json
from datetime import datetime
import sys
import os

# Add parent directory to path to import api_server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from api_server import app
except ImportError:
    # Create a minimal Flask app for testing if api_server doesn't exist
    from flask import Flask
    app = Flask(__name__)


@pytest.fixture
def client():
    """Flask test client"""
    with app.test_client() as client:
        yield client


class TestMotorStatusAPI:
    """Contract tests for motor status indicators endpoint"""

    def test_get_all_motor_status_success(self, client):
        """Test successful retrieval of all motor status indicators"""
        response = client.get('/api/motors/analytics/status')

        # This MUST FAIL until T015 is implemented
        assert response.status_code == 200

        data = json.loads(response.data)

        # Validate contract schema
        assert 'motors' in data
        assert 'last_updated' in data

        # Validate motors array
        assert isinstance(data['motors'], list)

        # If motors exist, validate their structure
        for motor in data['motors']:
            assert 'motor_id' in motor
            assert 'status_indicator' in motor
            assert isinstance(motor['motor_id'], int)
            assert motor['status_indicator'] in ['red', 'green', 'neutral']
            assert motor['motor_id'] >= 1
            assert motor['motor_id'] <= 70  # Max 70 motors

        # Validate last_updated timestamp
        assert isinstance(data['last_updated'], str)
        # Verify it's a valid ISO datetime
        try:
            datetime.fromisoformat(data['last_updated'].replace('Z', '+00:00'))
        except ValueError:
            pytest.fail("last_updated is not a valid ISO datetime format")

    def test_get_motor_status_response_time(self, client):
        """Test API response time for status endpoint"""
        import time

        start_time = time.time()
        response = client.get('/api/motors/analytics/status')
        end_time = time.time()

        response_time_ms = (end_time - start_time) * 1000

        # Performance requirement: <500ms
        # This test may fail initially but should pass after optimization
        assert response_time_ms < 500, f"Response time {response_time_ms}ms exceeds 500ms limit"

    def test_get_motor_status_content_type(self, client):
        """Test response content type is JSON"""
        response = client.get('/api/motors/analytics/status')

        # This MUST FAIL until T015 is implemented
        assert response.content_type == 'application/json'

    def test_get_motor_status_consistent_data(self, client):
        """Test that status data is consistent across multiple calls"""
        # Make two requests within a short time frame
        response1 = client.get('/api/motors/analytics/status')
        response2 = client.get('/api/motors/analytics/status')

        # Both should succeed
        assert response1.status_code == 200
        assert response2.status_code == 200

        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)

        # Motor count should be consistent
        assert len(data1['motors']) == len(data2['motors'])

        # Motor IDs should be the same (though status might change)
        motor_ids1 = {motor['motor_id'] for motor in data1['motors']}
        motor_ids2 = {motor['motor_id'] for motor in data2['motors']}
        assert motor_ids1 == motor_ids2

    def test_get_motor_status_no_duplicates(self, client):
        """Test that no motor appears twice in the status list"""
        response = client.get('/api/motors/analytics/status')
        assert response.status_code == 200

        data = json.loads(response.data)
        motor_ids = [motor['motor_id'] for motor in data['motors']]

        # Check for duplicates
        assert len(motor_ids) == len(set(motor_ids)), "Duplicate motor IDs found in status response"


if __name__ == '__main__':
    # Run the tests
    pytest.main([__file__, '-v'])