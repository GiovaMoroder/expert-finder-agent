import json
from pathlib import Path

import pandas as pd

from expert_finder.infrastructure.path import MENTEES_JSON, RAW_EDUCATION_CSV
from expert_finder.domain.shared.dates import linkedin_date_to_iso

input_path = MENTEES_JSON
output_path = RAW_EDUCATION_CSV

def main() -> None:
    data_path = Path(input_path)
    data = json.loads(data_path.read_text(encoding="utf-8"))

    all_educations = []
    for p in data:
        profile = p.get("linkedin_profile") or {}
        for e in profile.get("education") or []:
            start_date = linkedin_date_to_iso(e.get("starts_at") or e.get("start_date"))
            end_date = linkedin_date_to_iso(e.get("ends_at") or e.get("end_date"))
            all_educations.append(
                {
                    "full_name": profile.get("full_name"),
                    "degree": e.get("degree"),
                    "degree_name": e.get("degree_name"),
                    "field_of_study": e.get("field_of_study"),
                    "school": e.get("school"),
                    "start_date": start_date,
                    "end_date": end_date,
                }
            )

    all_educations = pd.DataFrame(all_educations)
    print("successfully built education dataframe with shape:", all_educations.shape)
    print(all_educations.head(10))

    # save to csv
    all_educations.to_csv(output_path, index=False)


if __name__ == "__main__":
    main()
