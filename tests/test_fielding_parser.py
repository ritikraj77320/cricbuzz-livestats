
from src.api.scorecard_parser import _parse_fielding_dismissal

tests = [
    ("c Sanju Samson b Mayank Yadav", "Sanju Samson", "catch"),
    ("run out (Arshdeep Singh)", "Arshdeep Singh", "run_out"),
    ("st MS Dhoni b Ravindra Jadeja", "MS Dhoni", "stumping"),
    ("b Mitchell Santner", None, None),
    ("not out", None, None),
]

for dismissal, expected_name, expected_type in tests:
    result = _parse_fielding_dismissal(dismissal)

    if expected_name is None:
        assert result is None, f"Unexpected result: {dismissal}"
    else:
        assert result is not None, f"No result: {dismissal}"
        assert result["fielder_name"] == expected_name
        assert result["contribution_type"] == expected_type

print("All fielding parser tests passed!")
