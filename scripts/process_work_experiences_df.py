from pathlib import Path

import pandas as pd

from expert_finder.infrastructure.path import PROCESSED_WORK_EXPERIENCES_CSV, RAW_WORK_EXPERIENCES_CSV


RAW_COLUMNS = [
    "full_name",
    "title",
    "company",
    "starts_at",
    "ends_at",
    "start_date",
    "end_date",
    "location",
    "description",
]


def _series_or_none(df: pd.DataFrame, column: str) -> pd.Series:
    if column in df.columns:
        return df[column]
    return pd.Series([None] * len(df))


def main() -> None:
    input_path = Path(RAW_WORK_EXPERIENCES_CSV)
    output_path = Path(PROCESSED_WORK_EXPERIENCES_CSV)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)

    if "start_date" in df.columns:
        start_dates = pd.to_datetime(df["start_date"], errors="coerce")
    else:
        start_dates = pd.to_datetime(_series_or_none(df, "starts_at"), errors="coerce")

    if "end_date" in df.columns:
        end_dates = pd.to_datetime(df["end_date"], errors="coerce")
    else:
        end_dates = pd.to_datetime(_series_or_none(df, "ends_at"), errors="coerce")

    processed = pd.DataFrame(
        {
            "full_name": _series_or_none(df, "full_name"),
            "company": _series_or_none(df, "company"),
            "role": _series_or_none(df, "title"),
            "location": _series_or_none(df, "location"),
            "start_date": start_dates,
            "end_date": end_dates,
            "description": _series_or_none(df, "description"),
        }
    )

    processed.to_csv(output_path, index=False)
    print("successfully built processed work experiences dataframe with shape:", processed.shape)
    print(processed.head(10))


if __name__ == "__main__":
    main()
