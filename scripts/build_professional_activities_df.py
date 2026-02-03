import json
from pathlib import Path

import pandas as pd

from expert_finder.expert_finder.path import MENTEES_JSON, PROFESSIONAL_CSV

input_path = MENTEES_JSON
output_path = PROFESSIONAL_CSV

def main() -> None:
    data_path = Path(input_path)
    data = json.loads(data_path.read_text(encoding="utf-8"))

    all_professional_activities = []
    for p in data:
        profile = p.get("linkedin_profile") or {}
        for e in profile.get("experiences") or []:
            all_professional_activities.append(
                {
                    "full_name": profile.get("full_name"),
                    "title": e.get("title"),
                    "company": e.get("company"),
                    "starts_at": e.get("starts_at"),
                    "ends_at": e.get("ends_at"),
                    "location": e.get("location"),
                    "description": e.get("description"),
                }
            )

    all_professional_activities = pd.DataFrame(all_professional_activities)
    print(
        "successfully built professional activities dataframe with shape:",
        all_professional_activities.shape,
    )
    print(all_professional_activities.head(10))

    # save to csv
    all_professional_activities.to_csv(output_path, index=False)


if __name__ == "__main__":
    main()
