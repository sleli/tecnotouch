#!/usr/bin/env python3
"""
Contract tests for GET /api/motors/{motor_id}/analytics endpoint
These tests MUST FAIL until the endpoint is implemented in T014
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


class TestMotorAnalyticsAPI:
    """Contract tests for motor analytics endpoint"""

    def test_get_motor_analytics_success(self, client):
        """Test successful motor analytics retrieval"""
        motor_id = 1
        response = client.get(f'/api/motors/{motor_id}/analytics')

        # This MUST FAIL until T014 is implemented
        assert response.status_code == 200

        data = json.loads(response.data)

        # Validate contract schema
        assert 'motor_id' in data
        assert 'position' in data
        assert 'today' in data
        assert 'week' in data
        assert 'month' in data
        assert 'status_indicator' in data

        # Validate motor_id
        assert data['motor_id'] == motor_id
        assert isinstance(data['motor_id'], int)

        # Validate position
        assert isinstance(data['position'], str)

        # Validate period metrics structure
        for period in ['today', 'week', 'month']:
            assert 'sales_count' in data[period]
            assert 'revenue' in data[period]
            assert isinstance(data[period]['sales_count'], int)
            assert isinstance(data[period]['revenue'], (int, float))
            assert data[period]['sales_count'] >= 0
            assert data[period]['revenue'] >= 0

        # Validate status indicator
        assert data['status_indicator'] in ['red', 'green', 'neutral']

        # Validate optional fields
        if data.get('last_sale'):
            assert 'timestamp' in data['last_sale']
            assert 'days_ago' in data['last_sale']
            assert isinstance(data['last_sale']['days_ago'], int)

        if data.get('sales_pattern'):
            assert 'average_interval_hours' in data['sales_pattern']
            assert 'sales_count' in data['sales_pattern']
            assert 'threshold_hours' in data['sales_pattern']
            assert isinstance(data['sales_pattern']['average_interval_hours'], (int, float))
            assert isinstance(data['sales_pattern']['sales_count'], int)
            assert isinstance(data['sales_pattern']['threshold_hours'], (int, float))

    def test_get_motor_analytics_not_found(self, client):
        """Test motor not found response"""
        motor_id = 999  # Non-existent motor
        response = client.get(f'/api/motors/{motor_id}/analytics')

        # This MUST FAIL until T014 is implemented
        assert response.status_code == 404

        data = json.loads(response.data)
        assert 'error' in data
        assert 'message' in data
        assert data['error'] == 'NotFound'

    def test_get_motor_analytics_invalid_id(self, client):
        """Test invalid motor ID parameters"""
        # Test negative motor ID
        response = client.get('/api/motors/-1/analytics')
        assert response.status_code in [400, 404]

        # Test motor ID > 70 (max motors)
        response = client.get('/api/motors/999/analytics')
        assert response.status_code == 404

        # Test non-numeric motor ID
        response = client.get('/api/motors/invalid/analytics')
        assert response.status_code == 404

    def test_get_motor_analytics_response_time(self, client):
        """Test API response time meets performance requirements (<500ms)"""
        import time

        motor_id = 1
        start_time = time.time()
        response = client.get(f'/api/motors/{motor_id}/analytics')
        end_time = time.time()

        response_time_ms = (end_time - start_time) * 1000

        # Performance requirement: <500ms
        # This test may fail initially but should pass after optimization
        assert response_time_ms < 500, f"Response time {response_time_ms}ms exceeds 500ms limit"

    def test_get_motor_analytics_content_type(self, client):
        """Test response content type is JSON"""
        motor_id = 1
        response = client.get(f'/api/motors/{motor_id}/analytics')

        # This MUST FAIL until T014 is implemented
        assert response.content_type == 'application/json'


if __name__ == '__main__':
    # Run the tests
    pytest.main([__file__, '-v'])