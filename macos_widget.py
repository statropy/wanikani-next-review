#!/usr/bin/env python3
"""
WaniKani macOS Menu Bar Widget

A macOS menu bar widget that displays the next WaniKani review time
and number of items available for your current level.
"""

import os
import rumps
import requests
from datetime import datetime
import threading

from wanikani_api import WaniKaniClient, find_next_review, next_review_day


class WaniKaniMenuBarApp(rumps.App):
    """Menu bar application for WaniKani review tracking."""

    def __init__(self):
        super(WaniKaniMenuBarApp, self).__init__(
            "WK",
            title="WaniKani",
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

    def seconds_until(self, target_time: datetime) -> int:
        now = datetime.now(target_time.tzinfo)
        time_until = target_time - now
        return int(time_until.total_seconds())

    def format_time_until(self, target_time: datetime) -> str:
        """
        Format the time remaining until target_time.

        Args:
            target_time: The target datetime (in UTC)

        Returns:
            Formatted string like "5h 23m" or "Available now"
        """
        total_seconds = self.seconds_until(target_time)
        if total_seconds < 0:
            return "Available now"

        hours, remainder = divmod(total_seconds, 3600)
        minutes = remainder // 60

        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m"
        else:
            return f"{total_seconds}s"

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
            _, level = self.client.get_user_level()

            # Get unlocked assignments
            assignments = self.client.get_unlocked_assignments(level)

            # Find next review
            result = find_next_review(assignments)

            if result:
                self.next_review_time, self.item_count = result

                # Update title with time and count
                time_str = self.next_review_time.strftime("%I:%M %p").lstrip("0")
                if self.seconds_until(self.next_review_time) <= 0:
                    self.title = f"鰐蟹 Available Now ({self.item_count})"
                else:
                    self.title = f"鰐蟹 {next_review_day(self.next_review_time)} {time_str} ({self.item_count})"

                # Update status menu item
                time_until = self.format_time_until(self.next_review_time)
                date_str = self.next_review_time.strftime("%a, %b %d")
                self.status_item.title = (
                    f"Next: {date_str} at {time_str} - {time_until}"
                )
            else:
                self.title = "WK: No reviews"
                self.status_item.title = "No reviews scheduled"

            # Update last update time
            self.last_update = datetime.now()
            update_str = self.last_update.strftime("%I:%M %p").lstrip("0")
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
