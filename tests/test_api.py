import json
from pathlib import Path

from src.api.api_client import get_live_matches


def main():
    try:
        data = get_live_matches()

        output_path = Path("data/raw/live_matches.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

        print("API connection successful!")
        print(f"Response saved to: {output_path}")
        print("Top-level keys:", list(data.keys()))

    except Exception as error:
        print("API test failed:", type(error).__name__)
        print("Details:", error)


if __name__ == "__main__":
    main()