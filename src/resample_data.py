from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
CLEAN_FILE = PROCESSED_DIR / "clean_power_consumption.csv"
HOURLY_FILE = PROCESSED_DIR / "hourly_consumption.csv"
DAILY_FILE = PROCESSED_DIR / "daily_consumption.csv"


def load_clean_data() -> pd.DataFrame:
    if not CLEAN_FILE.exists():
        raise FileNotFoundError(
            "Clean data file not found.\n"
            f"Expected path: {CLEAN_FILE}\n\n"
            "Run this command first:\n"
            "python src/preprocess_data.py"
        )

    return pd.read_csv(CLEAN_FILE, parse_dates=["datetime"], index_col="datetime")


def create_hourly_data(clean_data: pd.DataFrame) -> pd.DataFrame:
    hourly = clean_data.resample("h").agg(
        energy_kwh=("energy_kwh", "sum"),
        active_power_mean=("Global_active_power", "mean"),
        reactive_power_mean=("Global_reactive_power", "mean"),
        voltage_mean=("Voltage", "mean"),
        intensity_mean=("Global_intensity", "mean"),
        sub_metering_1_sum=("Sub_metering_1", "sum"),
        sub_metering_2_sum=("Sub_metering_2", "sum"),
        sub_metering_3_sum=("Sub_metering_3", "sum"),
    )

    hourly["hour"] = hourly.index.hour
    hourly["day_of_week"] = hourly.index.dayofweek
    hourly["month"] = hourly.index.month
    hourly["is_weekend"] = hourly["day_of_week"].isin([5, 6]).astype(int)

    return hourly


def create_daily_data(hourly_data: pd.DataFrame) -> pd.DataFrame:
    daily = hourly_data.resample("D").agg(
        daily_consumption=("energy_kwh", "sum"),
        avg_hourly_consumption=("energy_kwh", "mean"),
        max_hourly_consumption=("energy_kwh", "max"),
        voltage_mean=("voltage_mean", "mean"),
        intensity_mean=("intensity_mean", "mean"),
    )

    evening_usage = hourly_data[hourly_data["hour"].between(17, 22)].resample("D")["energy_kwh"].sum()
    night_usage = hourly_data[hourly_data["hour"].between(0, 5)].resample("D")["energy_kwh"].sum()

    daily["evening_usage_ratio"] = (evening_usage / daily["daily_consumption"]).fillna(0)
    daily["night_usage_ratio"] = (night_usage / daily["daily_consumption"]).fillna(0)
    daily["rolling_mean_7d"] = daily["daily_consumption"].rolling(7, min_periods=1).mean()
    daily["day_of_week"] = daily.index.dayofweek
    daily["month"] = daily.index.month
    daily["is_weekend"] = daily["day_of_week"].isin([5, 6]).astype(int)

    return daily


def main() -> None:
    clean_data = load_clean_data()
    hourly = create_hourly_data(clean_data)
    daily = create_daily_data(hourly)

    hourly.to_csv(HOURLY_FILE)
    daily.to_csv(DAILY_FILE)

    print("RESAMPLING COMPLETED")
    print("-" * 40)
    print(f"Hourly rows: {hourly.shape[0]:,}")
    print(f"Daily rows: {daily.shape[0]:,}")
    print(f"Hourly output: {HOURLY_FILE}")
    print(f"Daily output: {DAILY_FILE}")

    print("\nFIRST 5 HOURLY ROWS")
    print("-" * 40)
    print(hourly.head())

    print("\nFIRST 5 DAILY ROWS")
    print("-" * 40)
    print(daily.head())


if __name__ == "__main__":
    main()
