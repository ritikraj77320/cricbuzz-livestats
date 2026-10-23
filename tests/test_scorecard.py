
import json

from src.api.api_client import get_match_scorecard

MATCH_ID = "163643"

try:
    scorecard = get_match_scorecard(MATCH_ID)

    print("Scorecard fetched successfully.")
    print("Response type:", type(scorecard).__name__)
    print("Top-level keys:",
          list(scorecard.keys()) if isinstance(scorecard, dict)
          else "Response is not a dictionary")

    with open(
        "data/raw/test_scorecard.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(scorecard, file, indent=2, ensure_ascii=False)

    print("Saved to data/raw/test_scorecard.json")

except Exception as error:
    print("Scorecard request failed.")
    print("Error type:", type(error).__name__)
    print("Details:", error)
