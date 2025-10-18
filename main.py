#!/usr/bin/env python3
"""
WaniKani Next Review Checker

This script checks the WaniKani API to determine when the next review
will be available for unlocked items at the current level.
"""

import os
import sys
import requests
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from collections import defaultdict


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


def main():
    """Main entry point for the script."""
    # Get API token from environment variable
    api_token = os.environ.get("WANIKANI_API_TOKEN")

    if not api_token:
        print("Error: WANIKANI_API_TOKEN environment variable not set", file=sys.stderr)
        print(
            "Please set your API token: export WANIKANI_API_TOKEN='your_token_here'",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        # Initialize client
        client = WaniKaniClient(api_token)

        # Get current user level
        print("Fetching user level...")
        level = client.get_user_level()
        print(f"Current level: {level}")

        # Get unlocked assignments for current level
        print(f"\nFetching unlocked assignments for level {level}...")
        assignments = client.get_unlocked_assignments(level)
        print(f"Found {len(assignments)} unlocked assignments")

        # Find next review
        result = find_next_review(assignments)

        if result:
            next_date, count = result
            # Convert UTC to local timezone
            local_date = next_date.astimezone()
            # Calculate time until next review
            now = datetime.now(next_date.tzinfo)
            time_until = next_date - now

            # Format the time difference
            total_seconds = int(time_until.total_seconds())
            if total_seconds < 0:
                time_str = "Available now"
            else:
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                time_str = f"{hours}h {minutes}m {seconds}s"

            print(f"\nNext review available:")
            print(f"  UTC:   {next_date.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"  Local: {local_date.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"  In:    {time_str}")
            print(f"  Items: {count}")
        else:
            print("\nNo reviews scheduled for the current level")

    except requests.RequestException as e:
        print(f"API Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
