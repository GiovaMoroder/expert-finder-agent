import argparse
import json
from pathlib import Path

from expert_finder.expert_finder.path import INSTITUTIONS_JSON, MENTEES_JSON
from expert_finder.expert_finder.utils.institutions import extract_institutions


def main() -> None:
    parser = argparse.ArgumentParser(description="Build institutions dataset from mentees JSON.")
    parser.add_argument(
        "--input",
        type=Path,
        default=MENTEES_JSON,
        help="Path to mentees JSON data",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=INSTITUTIONS_JSON,
        help="Path to write institutions dataset",
    )
    args = parser.parse_args()

    mentees = json.loads(args.input.read_text(encoding="utf-8"))

    counts: dict[str, int] = {}
    for record in mentees:
        for institution in extract_institutions(record):
            counts[institution] = counts.get(institution, 0) + 1

    institutions = [
        {"name": name, "count": count}
        for name, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(institutions, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Wrote {len(institutions)} institutions to {args.output}")


if __name__ == "__main__":
    main()
