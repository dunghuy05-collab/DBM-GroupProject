from pathlib import Path

import pandas as pd

from load_data import load_raw_data


ROOT_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
CLEAN_FILE = PROCESSED_DIR / "clean_power_consumption.csv"

NUMERIC_COLUMNS = [
    "Global_active_power",
    "Global_reactive_power",
    "Voltage",
    "Global_intensity",
    "Sub_metering_1",
    "Sub_metering_2",
    "Sub_metering_3",
]


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()

    data["datetime"] = pd.to_datetime(
        data["Date"] + " " + data["Time"],
        format="%d/%m/%Y %H:%M:%S",
        errors="coerce",
    )

    for column in NUMERIC_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data = data.dropna(subset=["datetime"])
    data = data.sort_values("datetime")
    data = data.set_index("datetime")

    data[NUMERIC_COLUMNS] = data[NUMERIC_COLUMNS].interpolate(method="time")
    data[NUMERIC_COLUMNS] = data[NUMERIC_COLUMNS].ffill().bfill()

    data["energy_kwh"] = data["Global_active_power"] / 60
    data["hour"] = data.index.hour
    data["day_of_week"] = data.index.dayofweek
    data["month"] = data.index.month
    data["is_weekend"] = data["day_of_week"].isin([5, 6]).astype(int)

    return data


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    raw_data = load_raw_data()
    clean = clean_data(raw_data)
    clean.to_csv(CLEAN_FILE)

    print("CLEAN DATA COMPLETED")
    print("-" * 40)
    print(f"Rows: {clean.shape[0]:,}")
    print(f"Columns: {clean.shape[1]:,}")
    print(f"Output file: {CLEAN_FILE}")

    print("\nMISSING VALUES AFTER CLEANING")
    print("-" * 40)
    print(clean.isna().sum())

    print("\nFIRST 5 ROWS AFTER CLEANING")
    print("-" * 40)
    print(clean.head())


if __name__ == "__main__":
    main()
