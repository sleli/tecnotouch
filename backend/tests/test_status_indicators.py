#!/usr/bin/env python3
"""
Integration tests for status indicator logic
These tests MUST FAIL until the status determination logic is implemented in T010
"""

import pytest
import sqlite3
import tempfile
import os
from datetime import datetime, timedelta
import sys

# Add parent directory to path to import motor_analytics
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from motor_analytics import MotorAnalytics
except ImportError:
    # Motor analytics module doesn't exist yet
    MotorAnalytics = None


class TestStatusIndicatorLogic:
    """Integration tests for motor status indicator determination"""

    @pytest.fixture
    def analytics_engine(self):
        """Create analytics engine with temporary database"""
        if MotorAnalytics is None:
            pytest.skip("MotorAnalytics module not implemented yet")

        # Create temporary database
        db_fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(db_fd)

        analytics = MotorAnalytics(db_path)

        yield analytics

        # Cleanup
        os.unlink(db_path)

    def test_status_red_overdue_sales(self, analytics_engine):
        """Test red status for motors with overdue sales (>2x average interval)"""
        # Motor with last sale 5 days ago, average interval 2 days
        last_sale = datetime.now() - timedelta(days=5)
        average_interval = 48.0  # 2 days in hours

        # This MUST FAIL until T010 is implemented
        status = analytics_engine.determine_status_indicator(1, last_sale, average_interval)

        # 5 days (120 hours) > 2x average (96 hours) = red
        assert status == 'red'

    def test_status_green_normal_sales(self, analytics_engine):
        """Test green status for motors with normal sales pattern (≤2x average interval)"""
        # Motor with last sale 1 day ago, average interval 2 days
        last_sale = datetime.now() - timedelta(days=1)
        average_interval = 48.0  # 2 days in hours

        # This MUST FAIL until T010 is implemented
        status = analytics_engine.determine_status_indicator(1, last_sale, average_interval)

        # 1 day (24 hours) ≤ 2x average (96 hours) = green
        assert status == 'green'

    def test_status_green_exactly_at_threshold(self, analytics_engine):
        """Test green status for motors exactly at 2x threshold"""
        # Motor with last sale exactly at 2x average interval
        last_sale = datetime.now() - timedelta(hours=96)  # Exactly 2x 48 hours
        average_interval = 48.0  # 2 days in hours

        # This MUST FAIL until T010 is implemented
        status = analytics_engine.determine_status_indicator(1, last_sale, average_interval)

        # Exactly at threshold should be green (≤ not <)
        assert status == 'green'

    def test_status_neutral_no_sales_data(self, analytics_engine):
        """Test neutral status for motors with no sales data"""
        # This MUST FAIL until T010 is implemented
        status = analytics_engine.determine_status_indicator(1, None, None)

        assert status == 'neutral'

    def test_status_neutral_insufficient_sales_for_pattern(self, analytics_engine):
        """Test neutral status for motors with insufficient sales for pattern calculation"""
        # Motor with last sale but no average interval (< 5 sales)
        last_sale = datetime.now() - timedelta(days=1)

        # This MUST FAIL until T010 is implemented
        status = analytics_engine.determine_status_indicator(1, last_sale, None)

        assert status == 'neutral'

    def test_status_neutral_no_last_sale_with_pattern(self, analytics_engine):
        """Test neutral status for motors with pattern but no last sale"""
        # This edge case: pattern exists but no last sale timestamp
        average_interval = 48.0

        # This MUST FAIL until T010 is implemented
        status = analytics_engine.determine_status_indicator(1, None, average_interval)

        assert status == 'neutral'

    def test_status_calculation_with_varying_intervals(self, analytics_engine):
        """Test status calculation with different average intervals"""
        now = datetime.now()

        test_cases = [
            # (last_sale_hours_ago, average_interval_hours, expected_status)
            (24, 24.0, 'green'),    # 1 day ago, 1 day average = green
            (50, 24.0, 'red'),      # 2+ days ago, 1 day average = red
            (12, 48.0, 'green'),    # 12 hours ago, 2 day average = green
            (100, 48.0, 'red'),     # 4+ days ago, 2 day average = red
            (6, 12.0, 'green'),     # 6 hours ago, 12 hour average = green
            (30, 12.0, 'red'),      # 30 hours ago, 12 hour average = red
        ]

        for hours_ago, avg_interval, expected in test_cases:
            last_sale = now - timedelta(hours=hours_ago)

            # This MUST FAIL until T010 is implemented
            status = analytics_engine.determine_status_indicator(1, last_sale, avg_interval)

            threshold_hours = avg_interval * 2
            assert status == expected, f"Hours ago: {hours_ago}, Average: {avg_interval}, Threshold: {threshold_hours}, Expected: {expected}, Got: {status}"

    def test_status_calculation_considers_download_timestamp(self, analytics_engine):
        """Test that status calculation factors in last event download timestamp"""
        # This test ensures we don't flag motors as overdue if we haven't downloaded recent events

        # Motor with last sale 3 days ago, average interval 1 day
        last_sale = datetime.now() - timedelta(days=3)
        average_interval = 24.0  # 1 day

        # Normally this would be red (3 days > 2x 1 day)
        # But if last download was also 3 days ago, status should consider this

        # This MUST FAIL until T010 is implemented with download timestamp consideration
        status = analytics_engine.determine_status_indicator(1, last_sale, average_interval)

        # Without considering download timestamp, this should be red
        assert status == 'red'

        # TODO: Extend this test in T010 to include download timestamp parameter

    def test_status_indicator_consistency(self, analytics_engine):
        """Test that status indicators are consistent across multiple calls"""
        last_sale = datetime.now() - timedelta(days=2)
        average_interval = 48.0

        # This MUST FAIL until T010 is implemented
        status1 = analytics_engine.determine_status_indicator(1, last_sale, average_interval)
        status2 = analytics_engine.determine_status_indicator(1, last_sale, average_interval)

        assert status1 == status2, "Status indicator should be consistent for same inputs"

    def test_all_motor_status_indicators_valid(self, analytics_engine):
        """Test that all motor status endpoint returns only valid status values"""
        # This MUST FAIL until T010 and T015 are implemented
        result = analytics_engine.get_all_motor_status()

        assert 'motors' in result

        valid_statuses = {'red', 'green', 'neutral'}

        for motor in result['motors']:
            assert 'status_indicator' in motor
            assert motor['status_indicator'] in valid_statuses, f"Invalid status: {motor['status_indicator']}"

    def test_status_logic_handles_edge_times(self, analytics_engine):
        """Test status logic with edge case timestamps"""
        now = datetime.now()
        average_interval = 48.0  # 2 days

        edge_cases = [
            # Just under threshold (should be green)
            now - timedelta(hours=95, minutes=59),  # 95.98 hours < 96 hours

            # Just over threshold (should be red)
            now - timedelta(hours=96, minutes=1),   # 96.02 hours > 96 hours

            # Very recent (should be green)
            now - timedelta(minutes=5),

            # Very old (should be red)
            now - timedelta(days=30)
        ]

        expected_statuses = ['green', 'red', 'green', 'red']

        for i, last_sale in enumerate(edge_cases):
            # This MUST FAIL until T010 is implemented
            status = analytics_engine.determine_status_indicator(1, last_sale, average_interval)
            assert status == expected_statuses[i], f"Edge case {i}: Expected {expected_statuses[i]}, got {status}"


if __name__ == '__main__':
    # Run the tests
    pytest.main([__file__, '-v'])