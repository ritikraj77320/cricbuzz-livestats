import subprocess
import sys


def run_step(description, module_name):
    """Run a project module and stop if it fails."""
    print(f"\n{'=' * 50}")
    print(description)
    print("=" * 50)

    subprocess.run(
        [sys.executable, "-m", module_name],
        check=True,
    )


def main():
    steps = steps = [
    ("1. Fetch fresh Cricbuzz data", "src.api.sync_matches"),
    ("2. Import teams", "src.database.import_teams"),
    ("3. Import venues", "src.database.import_venues"),
    ("4. Import series", "src.database.import_series"),
    ("5. Import matches", "src.database.import_matches"),
    (
        "6. Import live match scorecards",
        "src.database.import_scorecard",
    ),
]

    try:
        for description, module_name in steps:
            run_step(description, module_name)

        print("\nPipeline completed successfully.")

    except subprocess.CalledProcessError as error:
        print(
            f"\nPipeline stopped because "
            f"{error.cmd[-1]} failed with exit code {error.returncode}."
        )
        raise SystemExit(error.returncode)


if __name__ == "__main__":
    main()