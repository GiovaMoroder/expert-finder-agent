import json
from pathlib import Path

import pandas as pd

from expert_finder.expert_finder.path import MENTEES_JSON, RAW_EDUCATION_CSV

input_path = MENTEES_JSON
output_path = RAW_EDUCATION_CSV

def main() -> None:
    data_path = Path(input_path)
    data = json.loads(data_path.read_text(encoding="utf-8"))

    all_educations = []
    for p in data:
        profile = p.get("linkedin_profile") or {}
        for e in profile.get("education") or []:
            all_educations.append(
                {
                    "full_name": profile.get("full_name"),
                    "degree": e.get("degree"),
                    "degree_name": e.get("degree_name"),
                    "field_of_study": e.get("field_of_study"),
                    "school": e.get("school"),
                }
            )

    all_educations = pd.DataFrame(all_educations)
    print("successfully built education dataframe with shape:", all_educations.shape)
    print(all_educations.head(10))

    # save to csv
    all_educations.to_csv(output_path, index=False)


if __name__ == "__main__":
    main()
