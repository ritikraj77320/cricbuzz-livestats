
import json
from pathlib import Path

from src.api.scorecard_parser import parse_scorecard


def main():
    file_path = Path("data/raw/test_scorecard.json")

    with file_path.open("r", encoding="utf-8") as file:
        raw_data = json.load(file)

    parsed_data = parse_scorecard(raw_data)

    print("\n=== MATCH STATUS ===")
    print(parsed_data["match_status"])

    print("\n=== INNINGS SUMMARY ===")

    for inning in parsed_data["innings"]:
        print(
            f'{inning["batting_team"]}: '
            f'{inning["team_score"]}/{inning["wickets"]} '
            f'({inning["overs"]} overs)'
        )
        print(f'Legal balls: {inning["legal_balls"]}')
        print(f'Batting entries: {len(inning["batting"])}')
        print(f'Bowling entries: {len(inning["bowling"])}')
        print(f'Extras: {inning["extras"]["total"]}')

    total_batting = sum(
        len(inning["batting"])
        for inning in parsed_data["innings"]
    )
    total_bowling = sum(
        len(inning["bowling"])
        for inning in parsed_data["innings"]
    )

    print("\n=== VALIDATION ===")
    print(f'Innings parsed: {len(parsed_data["innings"])}')
    print(f'Batting entries parsed: {total_batting}')
    print(f'Bowling entries parsed: {total_bowling}')

    assert len(parsed_data["innings"]) == 2
    assert total_batting == 22
    assert total_bowling == 11

    print("\nParser test passed!")


if __name__ == "__main__":
    main()
