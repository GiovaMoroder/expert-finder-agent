import json
from pathlib import Path

import pandas as pd

from expert_finder.expert_finder.path import PROCESSED_EDUCATION_CSV, RAW_EDUCATION_CSV
from expert_finder.expert_finder.utils.education_normalization import normalize_school


RAW_COLUMNS = ["full_name", "degree", "degree_name", "field_of_study", "school"]


def _row_to_raw_json(row: pd.Series) -> str:
    raw_dict = {col: row.get(col) for col in RAW_COLUMNS if col in row}
    return json.dumps(raw_dict, ensure_ascii=False)


def main() -> None:
    input_path = Path(RAW_EDUCATION_CSV)
    output_path = Path(PROCESSED_EDUCATION_CSV)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)

    processed = pd.DataFrame(
        {
            "full_name": df.get("full_name"),
            "institution": df.get("school").map(normalize_school) if "school" in df.columns else None,
            "degree": df.get("degree"),
            "field_of_study": df.get("field_of_study"),
            "start_date": pd.NA,
            "graduation_date": pd.NA,
            "gpa": pd.NA,
            "raw": df.apply(_row_to_raw_json, axis=1),
        }
    )

    processed.to_csv(output_path, index=False)
    print("successfully built processed education dataframe with shape:", processed.shape)
    print(processed.head(10))


if __name__ == "__main__":
    main()
