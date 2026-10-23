import json
from pathlib import Path

from src.api.match_parser import extract_matches


def main():
    file_path = Path("data/raw/live_matches.json")

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    matches = extract_matches(data)

    print("Matches extracted:", len(matches))

    for match in matches[:5]:
        print("-" * 40)
        print("Match ID:", match["match_id"])
        print("Match:", match["team1_name"], "vs", match["team2_name"])
        print("Format:", match["match_format"])
        print("State:", match["state"])
        print("Venue:", match["venue_name"], match["venue_city"])


if __name__ == "__main__":
    main()