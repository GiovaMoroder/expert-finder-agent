import json
from pathlib import Path

from expert_finder.infrastructure.path import MENTEES_JSON

input_path = MENTEES_JSON


def main() -> None:
    data_path = Path(input_path)
    mentees = json.loads(data_path.read_text(encoding="utf-8"))

    total = len(mentees)
    with_linkedin_profile = sum(
        1
        for mentee in mentees
        if mentee.get("linkedin_profile") is not None
        or mentee.get("linkedin_prifile") is not None
    )
    fraction = with_linkedin_profile / total if total else 0.0

    print(f"input_path: {data_path}")
    print(f"total_mentees: {total}")
    print(f"mentees_with_non_null_linkedin_profile: {with_linkedin_profile}")
    print(f"fraction_with_non_null_linkedin_profile: {fraction:.6f}")


if __name__ == "__main__":
    main()
