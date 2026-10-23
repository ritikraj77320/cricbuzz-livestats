import json
from pathlib import Path

from src.api.api_client import get_live_matches


def sync_matches():
    """Fetch fresh match data and save the raw API response."""
    output_path = Path("data/raw/live_matches.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = get_live_matches()

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    print("Fresh API response saved.")
    print("Top-level keys:", list(data.keys()))


if __name__ == "__main__":
    sync_matches()