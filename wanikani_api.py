#!/usr/bin/env python3
"""
WaniKani API Client

Shared module for interacting with the WaniKani API.
Used by both the CLI and menu bar widget applications.
"""

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
