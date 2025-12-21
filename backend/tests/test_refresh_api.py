#!/usr/bin/env python3
"""
Contract tests for POST /api/analytics/refresh endpoint
These tests MUST FAIL until the endpoint is implemented in T016
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


class TestAnalyticsRefreshAPI:
    """Contract tests for analytics refresh endpoint"""

    def test_post_analytics_refresh_success(self, client):
        """Test successful analytics refresh trigger"""
        response = client.post('/api/analytics/refresh')

        # This MUST FAIL until T016 is implemented
        assert response.status_code == 202

        data = json.loads(response.data)

        # Validate contract schema
        assert 'message' in data
        assert 'estimated_completion' in data

        # Validate message
        assert isinstance(data['message'], str)
        assert len(data['message']) > 0

        # Validate estimated_completion timestamp
        assert isinstance(data['estimated_completion'], str)
        # Verify it's a valid ISO datetime
        try:
            completion_time = datetime.fromisoformat(data['estimated_completion'].replace('Z', '+00:00'))
            # Should be in the future
            assert completion_time > datetime.now()
        except ValueError:
            pytest.fail("estimated_completion is not a valid ISO datetime format")

    def test_post_analytics_refresh_content_type(self, client):
        """Test response content type is JSON"""
        response = client.post('/api/analytics/refresh')

        # This MUST FAIL until T016 is implemented
        assert response.content_type == 'application/json'

    def test_post_analytics_refresh_idempotent(self, client):
        """Test that multiple refresh requests don't conflict"""
        # Make multiple refresh requests
        response1 = client.post('/api/analytics/refresh')
        response2 = client.post('/api/analytics/refresh')

        # Both should return 202 (accepted)
        assert response1.status_code == 202
        assert response2.status_code == 202

        # Both should have valid responses
        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)

        assert 'message' in data1
        assert 'message' in data2
        assert 'estimated_completion' in data1
        assert 'estimated_completion' in data2

    def test_post_analytics_refresh_no_body_required(self, client):
        """Test that refresh endpoint doesn't require request body"""
        # POST with empty body
        response = client.post('/api/analytics/refresh')
        assert response.status_code == 202

        # POST with JSON body (should still work)
        response = client.post('/api/analytics/refresh',
                             json={},
                             content_type='application/json')
        assert response.status_code == 202

    def test_post_analytics_refresh_method_not_allowed(self, client):
        """Test that only POST method is allowed"""
        # GET should not be allowed
        response = client.get('/api/analytics/refresh')
        assert response.status_code == 405

        # PUT should not be allowed
        response = client.put('/api/analytics/refresh')
        assert response.status_code == 405

        # DELETE should not be allowed
        response = client.delete('/api/analytics/refresh')
        assert response.status_code == 405

    def test_post_analytics_refresh_response_time(self, client):
        """Test that refresh endpoint responds quickly (async operation)"""
        import time

        start_time = time.time()
        response = client.post('/api/analytics/refresh')
        end_time = time.time()

        response_time_ms = (end_time - start_time) * 1000

        # Refresh should be async and respond quickly (<100ms)
        assert response_time_ms < 100, f"Refresh response time {response_time_ms}ms should be <100ms for async operation"


if __name__ == '__main__':
    # Run the tests
    pytest.main([__file__, '-v'])