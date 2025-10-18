#!/usr/bin/env python3
"""
WaniKani Menu Bar Widget

A macOS menu bar widget that displays the next WaniKani review time
and number of items available.
"""

import os
import sys
import rumps
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from collections import defaultdict
import threading


class WaniKaniClient:
    """Client for interacting with the WaniKani API."""

    BASE_URL = "https://api.wanikani.com/v2"

    def __init__(self, api_token: str):
        """
        Initialize the WaniKani client.

        Args:
            api_token: Bearer token for API authentication
        """
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Wanikani-Revision": "20170710",
        }

    def get_user_level(self) -> int:
        """
        Get the current user level.

        Returns:
            The user's current level as an integer

        Raises:
            requests.RequestException: If the API request fails
        """
        response = requests.get(f"{self.BASE_URL}/user", headers=self.headers)
        response.raise_for_status()
        data = response.json()
        return data["data"]["level"]

    def get_unlocked_assignments(self, level: int) -> List[Dict]:
        """
        Get unlocked assignments for the specified level.

        Args:
            level: The user's current level

        Returns:
            List of assignment objects from the API

        Raises:
            requests.RequestException: If the API request fails
        """
        params = {
            "levels": str(level),
            "unlocked": "true",
            "subject_types": "kanji,radical",
            "srs_stages": "0,1,2,3,4",
        }

        response = requests.get(
            f"{self.BASE_URL}/assignments", headers=self.headers, params=params
        )
        response.raise_for_status()
        data = response.json()
        return data["data"]


def find_next_review(assignments: List[Dict]) -> Optional[Tuple[datetime, int]]:
    """
    Find the earliest available_at date and count of items with that date.

    Args:
        assignments: List of assignment objects from the API

    Returns:
        Tuple of (earliest_datetime, count) or None if no assignments
    """
    if not assignments:
        return None

    # Group assignments by available_at date
    date_counts = defaultdict(int)

    for assignment in assignments:
        available_at = assignment["data"].get("available_at")
        if available_at:
            date_counts[available_at] += 1

    if not date_counts:
        return None

    # Find the earliest date
    earliest_date_str = min(date_counts.keys())
    earliest_date = datetime.fromisoformat(earliest_date_str.replace("Z", "+00:00"))
    count = date_counts[earliest_date_str]

    return earliest_date, count


class WaniKaniMenuBarApp(rumps.App):
    """Menu bar application for WaniKani review tracking."""

    def __init__(self):
        super(WaniKaniMenuBarApp, self).__init__(
            "WK",
            title="WaniKani",
            quit_button=rumps.MenuItem("Quit", key="q"),
        )

        # Get API token from environment
        self.api_token = os.environ.get("WANIKANI_API_TOKEN")
        if not self.api_token:
            self.title = "WK: No Token"
            self.menu = [
                rumps.MenuItem("Error: WANIKANI_API_TOKEN not set", callback=None),
                rumps.separator,
            ]
            return

        self.client = WaniKaniClient(self.api_token)
        self.next_review_time = None
        self.item_count = 0
        self.last_update = None

        # Create menu items
        self.status_item = rumps.MenuItem("Loading...", callback=None)
        self.refresh_item = rumps.MenuItem("Refresh Now", callback=self.refresh_now)
        self.last_update_item = rumps.MenuItem("Last updated: Never", callback=None)

        self.menu = [
            self.status_item,
            rumps.separator,
            self.refresh_item,
            self.last_update_item,
            rumps.separator,
        ]

        # Start hourly timer (3600 seconds)
        self.timer = rumps.Timer(self.update_data, 3600)
        self.timer.start()

        # Initial update
        self.update_data(None)

    def format_time_until(self, target_time: datetime) -> str:
        """
        Format the time remaining until target_time.

        Args:
            target_time: The target datetime (in UTC)

        Returns:
            Formatted string like "5h 23m" or "Available now"
        """
        now = datetime.now(target_time.tzinfo)
        time_until = target_time - now

        total_seconds = int(time_until.total_seconds())
        if total_seconds < 0:
            return "Available now"

        hours, remainder = divmod(total_seconds, 3600)
        minutes = remainder // 60

        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

    def update_data(self, _):
        """Update the review data from WaniKani API."""
        # Run in background thread to avoid blocking UI
        thread = threading.Thread(target=self._fetch_data)
        thread.daemon = True
        thread.start()

    def _fetch_data(self):
        """Fetch data from WaniKani API (runs in background thread)."""
        try:
            # Get user level
            level = self.client.get_user_level()

            # Get unlocked assignments
            assignments = self.client.get_unlocked_assignments(level)

            # Find next review
            result = find_next_review(assignments)

            if result:
                self.next_review_time, self.item_count = result
                # Convert to local time
                local_time = self.next_review_time.astimezone()

                # Update title with time and count
                time_str = local_time.strftime("%I:%M %p")
                self.title = f"{time_str} ({self.item_count})"

                # Update status menu item
                time_until = self.format_time_until(self.next_review_time)
                date_str = local_time.strftime("%a, %b %d")
                self.status_item.title = f"Next: {date_str} at {time_str} - {time_until}"
            else:
                self.title = "WK: No reviews"
                self.status_item.title = "No reviews scheduled"

            # Update last update time
            self.last_update = datetime.now()
            update_str = self.last_update.strftime("%I:%M %p")
            self.last_update_item.title = f"Last updated: {update_str}"

        except requests.RequestException as e:
            self.title = "WK: Error"
            self.status_item.title = f"API Error: {str(e)[:50]}"
        except Exception as e:
            self.title = "WK: Error"
            self.status_item.title = f"Error: {str(e)[:50]}"

    @rumps.clicked("Refresh Now")
    def refresh_now(self, _):
        """Manual refresh triggered by user."""
        self.title = "WK: Refreshing..."
        self.update_data(None)


def main():
    """Main entry point for the menu bar app."""
    WaniKaniMenuBarApp().run()


if __name__ == "__main__":
    main()