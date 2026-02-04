from pathlib import Path

import pandas as pd

from expert_finder.expert_finder.path import PROCESSED_WORK_EXPERIENCES_CSV, RAW_WORK_EXPERIENCES_CSV


RAW_COLUMNS = [
    "full_name",
    "title",
    "company",
    "starts_at",
    "ends_at",
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

    processed = pd.DataFrame(
        {
            "full_name": _series_or_none(df, "full_name"),
            "company": _series_or_none(df, "company"),
            "role": _series_or_none(df, "title"),
            "location": _series_or_none(df, "location"),
            "start_date": _series_or_none(df, "starts_at"),
            "end_date": _series_or_none(df, "ends_at"),
            "description": _series_or_none(df, "description"),
        }
    )

    processed.to_csv(output_path, index=False)
    print("successfully built processed work experiences dataframe with shape:", processed.shape)
    print(processed.head(10))


if __name__ == "__main__":
    main()
