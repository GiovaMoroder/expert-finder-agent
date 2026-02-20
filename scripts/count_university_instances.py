from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from expert_finder.infrastructure.path import (
    PROCESSED_EDUCATION_CSV,
    PROCESSED_WORK_EXPERIENCES_CSV,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Count unique universities or companies and print per-value frequencies."
    )
    parser.add_argument(
        "entity_type",
        choices=("universities", "companies"),
        help="Choose what to count: universities (education) or companies (work experiences).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.entity_type == "universities":
        input_path = Path(PROCESSED_EDUCATION_CSV)
        column_candidates = ("institution", "school")
        singular_label = "university"
        plural_label = "universities"
    else:
        input_path = Path(PROCESSED_WORK_EXPERIENCES_CSV)
        column_candidates = ("company",)
        singular_label = "company"
        plural_label = "companies"

    if not input_path.exists():
        raise FileNotFoundError(
            f"CSV not found: {input_path}. "
            f"Create the processed {args.entity_type} table first."
        )

    df = pd.read_csv(input_path)

    value_series = None
    for column in column_candidates:
        if column in df.columns:
            value_series = df[column]
            break
    if value_series is None:
        expected = "', '".join(column_candidates)
        raise ValueError(
            f"Could not find expected column(s) for {args.entity_type}. Expected '{expected}'."
        )

    counts = (
        value_series
        .dropna()
        .astype(str)
        .str.strip()
        .loc[lambda s: s != ""]
        .value_counts()
        .sort_index()
    )

    print(f"{singular_label.capitalize()} instance counts:")
    for value, count in counts.items():
        print(f"{value}: {count}")

    print(f"\nNumber of unique {plural_label}: {len(counts)}")


if __name__ == "__main__":
    main()
