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

from wanikani_api import WaniKaniClient, find_next_review


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
