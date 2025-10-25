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
import keyring

from wanikani_api import WaniKaniClient, find_next_review, next_review_day


class WaniKaniMenuBarApp(rumps.App):
    """Menu bar application for WaniKani review tracking."""

    APP_NAME = "WaniKaniNext"
    TOKEN_NAME = "api_token"

    def __init__(self):
        super(WaniKaniMenuBarApp, self).__init__(
            "WK",
            title="WaniKani",
        )

        self.next_review_time = None
        self.item_count = 0
        self.last_update = None
        self.timer = None

        # Create menu items
        self.status_item = rumps.MenuItem("Loading...", callback=None)
        self.refresh_item = rumps.MenuItem("Refresh Now", callback=None)
        self.last_update_item = rumps.MenuItem("Last updated: Never", callback=None)
        self.update_api_token_item = rumps.MenuItem(
            "Enter API Token", callback=self.update_api_token
        )

        self.menu = [
            self.status_item,
            rumps.separator,
            self.refresh_item,
            self.last_update_item,
            rumps.separator,
            self.update_api_token_item,
        ]

        self.load_client()

    def load_client(self):
        self.api_token = self.load_api_token()
        if not self.api_token:
            self.title = "WK: No Token"
            return

        self.client = WaniKaniClient(self.api_token)

        # Start hourly timer (3600 seconds)
        if self.timer:
            self.timer.stop()
        self.timer = rumps.Timer(self.update_data, 3600)
        self.timer.start()

        # Initial update
        self.update_data(None)

    def delete_api_token(self):
        keyring.delete_password(self.APP_NAME, self.TOKEN_NAME)
        self.api_key = None

    def load_api_token(self):
        """Load API token from macOS Keychain"""
        try:
            return keyring.get_password(self.APP_NAME, self.TOKEN_NAME)
        except:
            return None

    def save_api_token(self, token):
        """Save API token to macOS Keychain"""
        keyring.set_password(self.APP_NAME, self.TOKEN_NAME, token)
        self.api_token = token

    def prompt_for_api_token(self):
        window = rumps.Window(
            title="Enter API Token",
            message="Please enter your API token:",
            default_text="",
            ok="Save",
            cancel="Cancel",
            dimensions=(300, 20),
        )

        response = window.run()

        if response.clicked:
            api_token = response.text.strip()
            if api_token:
                # self.save_api_token(api_token)
                rumps.notification(
                    title="API Token Saved",
                    subtitle="",
                    message="Your API token has been saved securely.",
                )
                self.save_api_token(api_token)
                self.load_client()
            else:
                rumps.alert("Error", "API token cannot be empty")
                self.prompt_for_api_token()

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
            self.update_api_token_item.title = "Update API Token"
            self.refresh_item.set_callback(self.refresh_now)

        except requests.RequestException as e:
            self.title = "WK: Error"
            self.status_item.title = f"API Error: {str(e)[:50]}"
        except Exception as e:
            self.title = "WK: Error"
            self.status_item.title = f"Error: {str(e)[:50]}"

    def refresh_now(self, _):
        """Manual refresh triggered by user."""
        self.title = "WK: Refreshing..."
        self.update_data(None)

    def update_api_token(self, _):
        """Manual refresh triggered by user."""
        self.prompt_for_api_token()


def main():
    """Main entry point for the menu bar app."""
    WaniKaniMenuBarApp().run()


if __name__ == "__main__":
    main()
