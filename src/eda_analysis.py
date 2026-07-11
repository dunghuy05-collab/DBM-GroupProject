from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
OUTPUT_DIR = ROOT_DIR / "outputs"
TABLE_DIR = OUTPUT_DIR / "tables"
FIGURE_DIR = OUTPUT_DIR / "figures"

HOURLY_FILE = PROCESSED_DIR / "hourly_consumption.csv"
DAILY_FILE = PROCESSED_DIR / "daily_consumption.csv"


def load_resampled_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not HOURLY_FILE.exists() or not DAILY_FILE.exists():
        raise FileNotFoundError(
            "Resampled data files not found.\n\n"
            "Run this command first:\n"
            "python src/resample_data.py"
        )

    hourly = pd.read_csv(HOURLY_FILE, parse_dates=["datetime"])
    daily = pd.read_csv(DAILY_FILE, parse_dates=["datetime"])
    return hourly, daily


def analyze_hourly_pattern(hourly: pd.DataFrame) -> pd.DataFrame:
    result = (
        hourly.groupby("hour", as_index=False)["energy_kwh"]
        .mean()
        .rename(columns={"energy_kwh": "avg_energy_kwh"})
        .sort_values("hour")
    )

    result.to_csv(TABLE_DIR / "avg_consumption_by_hour.csv", index=False)

    plt.figure(figsize=(10, 5))
    sns.barplot(data=result, x="hour", y="avg_energy_kwh", color="#2f6f73")
    plt.title("Average Electricity Consumption by Hour")
    plt.xlabel("Hour")
    plt.ylabel("Average kWh")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "avg_consumption_by_hour.png", dpi=160)
    plt.close()

    return result


def analyze_monthly_pattern(daily: pd.DataFrame) -> pd.DataFrame:
    result = (
        daily.groupby("month", as_index=False)["daily_consumption"]
        .mean()
        .rename(columns={"daily_consumption": "avg_daily_consumption"})
        .sort_values("month")
    )

    result.to_csv(TABLE_DIR / "avg_daily_consumption_by_month.csv", index=False)

    plt.figure(figsize=(10, 5))
    sns.barplot(data=result, x="month", y="avg_daily_consumption", color="#9b5d42")
    plt.title("Average Daily Electricity Consumption by Month")
    plt.xlabel("Month")
    plt.ylabel("Average daily kWh")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "avg_daily_consumption_by_month.png", dpi=160)
    plt.close()

    return result


def compare_weekday_weekend(daily: pd.DataFrame) -> pd.DataFrame:
    result = (
        daily.groupby("is_weekend", as_index=False)["daily_consumption"]
        .mean()
        .rename(columns={"daily_consumption": "avg_daily_consumption"})
    )
    result["day_type"] = result["is_weekend"].map({0: "Weekday", 1: "Weekend"})
    result = result[["day_type", "avg_daily_consumption"]]
    result.to_csv(TABLE_DIR / "weekday_vs_weekend.csv", index=False)
    return result


def create_usage_heatmap(hourly: pd.DataFrame) -> pd.DataFrame:
    heatmap_data = hourly.pivot_table(
        values="energy_kwh",
        index="day_of_week",
        columns="hour",
        aggfunc="mean",
    )

    heatmap_data.to_csv(TABLE_DIR / "usage_heatmap_day_hour.csv")

    plt.figure(figsize=(12, 5))
    sns.heatmap(heatmap_data, cmap="YlGnBu")
    plt.title("Electricity Usage Heatmap: Day of Week x Hour")
    plt.xlabel("Hour")
    plt.ylabel("Day of week")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "usage_heatmap_day_hour.png", dpi=160)
    plt.close()

    return heatmap_data


def find_top_consumption_days(daily: pd.DataFrame) -> pd.DataFrame:
    result = daily.sort_values("daily_consumption", ascending=False).head(10)
    result.to_csv(TABLE_DIR / "top_10_consumption_days.csv", index=False)
    return result


def main() -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    hourly, daily = load_resampled_data()

    hourly_pattern = analyze_hourly_pattern(hourly)
    monthly_pattern = analyze_monthly_pattern(daily)
    weekday_weekend = compare_weekday_weekend(daily)
    create_usage_heatmap(hourly)
    top_days = find_top_consumption_days(daily)

    peak_hour = hourly_pattern.loc[hourly_pattern["avg_energy_kwh"].idxmax()]
    peak_month = monthly_pattern.loc[monthly_pattern["avg_daily_consumption"].idxmax()]

    print("EDA COMPLETED")
    print("-" * 40)
    print(f"Peak hour: {int(peak_hour['hour'])}:00")
    print(f"Peak hour average kWh: {peak_hour['avg_energy_kwh']:.3f}")
    print(f"Peak month: {int(peak_month['month'])}")
    print(f"Peak month average daily kWh: {peak_month['avg_daily_consumption']:.3f}")

    print("\nWEEKDAY VS WEEKEND")
    print("-" * 40)
    print(weekday_weekend)

    print("\nTOP 10 CONSUMPTION DAYS")
    print("-" * 40)
    print(top_days[["datetime", "daily_consumption"]])

    print("\nOutput folders:")
    print(f"Tables: {TABLE_DIR}")
    print(f"Figures: {FIGURE_DIR}")


if __name__ == "__main__":
    main()
