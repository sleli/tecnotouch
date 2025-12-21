#!/usr/bin/env python3
"""
Motor Analytics Module
Calculates sales patterns, timing indicators, and status for individual motors
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sqlite3
import json


class MotorAnalytics:
    """
    Motor-specific analytics calculator for sales timing and status indicators
    """

    def __init__(self, db_path: str = "sales_data.db"):
        self.db_path = db_path
        self.cache = {}
        self.cache_ttl = timedelta(minutes=5)  # 5-minute cache

    def get_motor_analytics(self, motor_id: int) -> Dict:
        """
        Get comprehensive analytics for a specific motor
        Returns analytics data matching the API contract schema
        """
        # Check cache first
        cache_key = f"motor_analytics_{motor_id}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']

        try:
            # Get motor position
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT position FROM motors WHERE motor_id = ?", (motor_id,))
            motor_row = cursor.fetchone()
            if not motor_row:
                conn.close()
                raise ValueError(f"Motor {motor_id} not found")

            position = motor_row[0]

            # Calculate period metrics
            now = datetime.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = now - timedelta(days=7)
            month_start = now - timedelta(days=30)

            # Get sales data for different periods
            periods = {
                'today': today_start,
                'week': week_start,
                'month': month_start
            }

            period_metrics = {}
            for period, start_date in periods.items():
                cursor.execute("""
                    SELECT COUNT(*), COALESCE(SUM(amount), 0)
                    FROM sales_events
                    WHERE motor_id = ? AND event_type = 'sale'
                    AND datetime(timestamp) >= datetime(?)
                """, (motor_id, start_date.isoformat()))

                count, revenue = cursor.fetchone()
                period_metrics[period] = {
                    "sales_count": count or 0,
                    "revenue": float(revenue or 0.0)
                }

            # Get last sale info
            cursor.execute("""
                SELECT timestamp FROM sales_events
                WHERE motor_id = ? AND event_type = 'sale'
                ORDER BY datetime(timestamp) DESC LIMIT 1
            """, (motor_id,))

            last_sale_row = cursor.fetchone()
            last_sale = None
            if last_sale_row:
                last_sale_time = datetime.fromisoformat(last_sale_row[0])
                days_ago = (now - last_sale_time).days
                last_sale = {
                    "timestamp": last_sale_time.isoformat(),
                    "days_ago": days_ago
                }

            conn.close()

            # Calculate sales pattern and status
            sales_pattern = self.calculate_sales_pattern(motor_id)

            if sales_pattern and last_sale:
                last_sale_time = datetime.fromisoformat(last_sale['timestamp'])
                status = self.determine_status_indicator(motor_id, last_sale_time, sales_pattern['average_interval_hours'])
            else:
                status = "neutral"

            # Build result
            result = {
                "motor_id": motor_id,
                "position": position,
                "today": period_metrics['today'],
                "week": period_metrics['week'],
                "month": period_metrics['month'],
                "last_sale": last_sale,
                "status_indicator": status,
                "sales_pattern": sales_pattern
            }

            # Cache result
            self.cache[cache_key] = {
                'data': result,
                'timestamp': datetime.now()
            }

            return result

        except Exception as e:
            # Return safe default for errors
            return {
                "motor_id": motor_id,
                "position": f"M{motor_id}",
                "today": {"sales_count": 0, "revenue": 0.0},
                "week": {"sales_count": 0, "revenue": 0.0},
                "month": {"sales_count": 0, "revenue": 0.0},
                "last_sale": None,
                "status_indicator": "neutral",
                "sales_pattern": None
            }

    def get_all_motor_status(self) -> Dict:
        """
        Get status indicators for all motors for dashboard grid
        Returns simplified status data for motor buttons
        """
        # Check cache first
        cache_key = "all_motor_status"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get all motors
            cursor.execute("SELECT motor_id FROM motors ORDER BY motor_id")
            motor_rows = cursor.fetchall()
            conn.close()

            motors = []
            for (motor_id,) in motor_rows:
                # Get status for each motor
                # Note: This could be optimized with bulk queries in production
                motor_analytics = self.get_motor_analytics(motor_id)
                motors.append({
                    "motor_id": motor_id,
                    "status_indicator": motor_analytics["status_indicator"]
                })

            result = {
                "motors": motors,
                "last_updated": datetime.now().isoformat()
            }

            # Cache result
            self.cache[cache_key] = {
                'data': result,
                'timestamp': datetime.now()
            }

            return result

        except Exception as e:
            return {
                "motors": [],
                "last_updated": datetime.now().isoformat()
            }

    def calculate_sales_pattern(self, motor_id: int) -> Optional[Dict]:
        """
        Calculate sales pattern analysis for status determination
        Returns pattern data or None if insufficient data
        """
        try:
            # Get sales timestamps for this motor
            sales_data = self._get_sales_data(motor_id)

            if len(sales_data) < 5:  # Minimum 5 sales required
                return None

            # Extract timestamps and sort chronologically
            timestamps = [datetime.fromisoformat(timestamp) for timestamp, _, _ in sales_data]
            timestamps.sort()

            # Calculate intervals between consecutive sales
            intervals = []
            for i in range(1, len(timestamps)):
                interval = (timestamps[i] - timestamps[i-1]).total_seconds() / 3600  # hours
                intervals.append(interval)

            if not intervals:
                return None

            # Calculate average interval
            average_interval = sum(intervals) / len(intervals)

            return {
                "average_interval_hours": average_interval,
                "sales_count": len(sales_data),
                "threshold_hours": average_interval * 2  # 2x threshold as per requirements
            }

        except Exception as e:
            return None

    def determine_status_indicator(self, motor_id: int, last_sale: Optional[datetime],
                                 average_interval: Optional[float]) -> str:
        """
        Determine status indicator color based on sales pattern
        Returns 'red', 'green', or 'neutral'
        """
        # No data or insufficient pattern data
        if not last_sale or not average_interval:
            return "neutral"

        # Calculate time since last sale
        now = datetime.now()
        time_since_sale_hours = (now - last_sale).total_seconds() / 3600

        # Calculate threshold (2x average interval)
        threshold_hours = average_interval * 2

        # Determine status
        if time_since_sale_hours > threshold_hours:
            return "red"  # Overdue
        else:
            return "green"  # Normal

    def refresh_analytics_cache(self) -> bool:
        """
        Force refresh of all analytics calculations
        Returns True if successful
        """
        try:
            self.cache.clear()
            return True
        except Exception as e:
            return False

    def get_cache_stats(self) -> Dict:
        """
        Get cache statistics for monitoring and debugging
        """
        now = datetime.now()
        valid_entries = 0
        expired_entries = 0

        for key, entry in self.cache.items():
            if entry.get('timestamp') and now - entry['timestamp'] < self.cache_ttl:
                valid_entries += 1
            else:
                expired_entries += 1

        return {
            'total_entries': len(self.cache),
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'cache_ttl_minutes': self.cache_ttl.total_seconds() / 60,
            'last_cleanup': getattr(self, '_last_cleanup', None)
        }

    def cleanup_expired_cache(self) -> int:
        """
        Remove expired cache entries to prevent memory growth
        Returns number of entries removed
        """
        now = datetime.now()
        expired_keys = []

        for key, entry in self.cache.items():
            if not entry.get('timestamp') or now - entry['timestamp'] >= self.cache_ttl:
                expired_keys.append(key)

        for key in expired_keys:
            del self.cache[key]

        self._last_cleanup = now.isoformat()
        return len(expired_keys)

    def warm_cache_for_motors(self, motor_ids: List[int]) -> Dict:
        """
        Pre-populate cache for multiple motors to improve performance
        Returns statistics about cache warming
        """
        results = {
            'motors_processed': 0,
            'motors_cached': 0,
            'errors': 0
        }

        for motor_id in motor_ids:
            try:
                # This will populate cache if not already cached
                self.get_motor_analytics(motor_id)
                results['motors_processed'] += 1

                # Check if it's now cached
                cache_key = f"motor_analytics_{motor_id}"
                if self._is_cache_valid(cache_key):
                    results['motors_cached'] += 1

            except Exception:
                results['errors'] += 1

        return results

    def _get_sales_data(self, motor_id: int, days_back: int = 365) -> List[Tuple]:
        """
        Private method to fetch sales data from database
        Returns list of (timestamp, quantity, amount) tuples
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get sales data for the specified period
            cutoff_date = datetime.now() - timedelta(days=days_back)
            cursor.execute("""
                SELECT timestamp, quantity, amount
                FROM sales_events
                WHERE motor_id = ? AND event_type = 'sale'
                AND datetime(timestamp) >= datetime(?)
                ORDER BY datetime(timestamp) ASC
            """, (motor_id, cutoff_date.isoformat()))

            results = cursor.fetchall()
            conn.close()
            return results

        except Exception as e:
            return []

    def _is_cache_valid(self, key: str) -> bool:
        """
        Check if cached data is still valid
        """
        if key not in self.cache:
            return False

        cache_time = self.cache[key].get('timestamp')
        if not cache_time:
            return False

        return datetime.now() - cache_time < self.cache_ttl