import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = os.getenv("RAPIDAPI_HOST")

BASE_URL = f"https://{API_HOST}"


def get_live_matches():
    """Fetch live matches from the Cricbuzz API."""
    if not API_KEY or not API_HOST:
        raise ValueError(
            "RAPIDAPI_KEY or RAPIDAPI_HOST is missing from .env"
        )

    url = f"{BASE_URL}/matches/v1/live"

    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST,
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()

    return response.json()



def get_match_scorecard(match_id):
    """Fetch a match scorecard using its Cricbuzz match ID."""
    if not API_KEY or not API_HOST:
        raise ValueError(
            "RAPIDAPI_KEY or RAPIDAPI_HOST is missing from .env"
        )

    url = f"{BASE_URL}/mcenter/v1/{match_id}/scard"

    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST,
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()

    return response.json()
