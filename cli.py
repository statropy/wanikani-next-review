#!/usr/bin/env python3
"""
WaniKani Next Review Checker - CLI

Command-line tool that checks the WaniKani API to determine when the next review
will be available for unlocked items at the current level.
"""

import os
import sys
import requests
from datetime import datetime

from wanikani_api import WaniKaniClient, find_next_review, next_review_day


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
        username, level = client.get_user_level()

        # Get unlocked assignments for current level
        assignments = client.get_unlocked_assignments(level)

        # Find next review
        result = find_next_review(assignments)

        if result:
            next_date, count = result

            print(
                f"鰐蟹 {username} level {level} next review {count} of {len(assignments)} unlocked items:"
            )
            # Format the time difference
            time_until = next_date - datetime.now(next_date.tzinfo)
            total_seconds = int(time_until.total_seconds())
            if total_seconds <= 0:
                print("  Available now")
            else:
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                time_str = f"{hours}h {minutes}m {seconds}s"
                print(
                    f"  {next_review_day(next_date)} {next_date.strftime('%I:%M %p').lstrip('0')} ({time_str})"
                )
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
