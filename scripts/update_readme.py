"""Update the most recently completed quarter in README.md."""
import re
from datetime import date


def last_completed_quarter(today: date = None) -> tuple[int, int]:
    """Return (quarter, year) for the most recently completed quarter."""
    if today is None:
        today = date.today()
    month = today.month
    year = today.year
    if month <= 3:
        return 4, year - 1
    elif month <= 6:
        return 1, year
    elif month <= 9:
        return 2, year
    else:
        return 3, year


def update_readme(path: str = "README.md") -> bool:
    with open(path) as f:
        content = f.read()

    q, year = last_completed_quarter()
    new_quarter = f"**(Q{q} {year})**"

    updated, count = re.subn(r"\*\*\(Q\d \d{4}\)\*\*", new_quarter, content)
    if count == 0:
        print(f"No quarter pattern found in {path}")
        return False

    if updated == content:
        print(f"{path} already shows {new_quarter}, no update needed.")
        return False

    with open(path, "w") as f:
        f.write(updated)
    print(f"Updated {path} to {new_quarter}")
    return True


if __name__ == "__main__":
    update_readme()
