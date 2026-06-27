import pandas as pd
import json


def clean_value(value):
    """
    Convert pandas/numpy types into JSON serializable values.
    """
    if pd.isna(value):
        return None

    # Convert Timestamp to string
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")

    return value


def excel_to_json(excel_file, output_json):
    # Read Excel
    df = pd.read_excel(excel_file)

    # Clean column names
    df.columns = [col.strip() for col in df.columns]

    records = []

    for _, row in df.iterrows():
        record = {}

        for column in df.columns:
            record[column] = clean_value(row[column])

        records.append(record)

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=4, ensure_ascii=False)

    print(f"Saved {len(records)} records to {output_json}")


if __name__ == "__main__":
    excel_file = "azentio_data.xlsx"
    output_json = "azentio_data_processed.json"

    excel_to_json(excel_file, output_json)