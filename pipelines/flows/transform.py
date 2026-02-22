import subprocess
import sys
from pathlib import Path

DBT_DIR = Path(__file__).resolve().parent.parent.parent / "dbt"


def run_dbt():
    result = subprocess.run(
        [sys.executable, "-m", "dbt", "run", "--profiles-dir", "."],
        cwd=str(DBT_DIR),
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("dbt run failed")
    print("dbt transformations complete")


if __name__ == "__main__":
    run_dbt()
