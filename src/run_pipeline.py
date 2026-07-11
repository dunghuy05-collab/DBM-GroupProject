from anomaly_detection import detect_zscore_anomalies, load_daily_data
from eda_analysis import (
    analyze_hourly_pattern,
    analyze_monthly_pattern,
    compare_weekday_weekend,
    create_usage_heatmap,
    find_top_consumption_days,
    load_resampled_data,
)
from load_data import inspect_data, load_raw_data
from pattern_mining import build_daily_transactions, convert_frozensets_to_text, mine_patterns
from preprocess_data import CLEAN_FILE, clean_data
from resample_data import (
    DAILY_FILE,
    HOURLY_FILE,
    create_daily_data,
    create_hourly_data,
    load_clean_data,
)
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "outputs"
TABLE_DIR = OUTPUT_DIR / "tables"
FIGURE_DIR = OUTPUT_DIR / "figures"


def step_1_inspect_raw_data() -> None:
    print("\nSTEP 1: INSPECT RAW DATA")
    print("=" * 60)
    raw_data = load_raw_data()
    inspect_data(raw_data)


def step_2_clean_data() -> None:
    print("\nSTEP 2: CLEAN DATA")
    print("=" * 60)
    raw_data = load_raw_data()
    clean = clean_data(raw_data)
    clean.to_csv(CLEAN_FILE)
    print(f"Saved clean data: {CLEAN_FILE}")
    print(f"Rows: {len(clean):,}")
    print(f"Missing values after cleaning: {int(clean.isna().sum().sum()):,}")


def step_3_resample_data() -> None:
    print("\nSTEP 3: RESAMPLE DATA")
    print("=" * 60)
    clean = load_clean_data()
    hourly = create_hourly_data(clean)
    daily = create_daily_data(hourly)
    hourly.to_csv(HOURLY_FILE)
    daily.to_csv(DAILY_FILE)
    print(f"Saved hourly data: {HOURLY_FILE}")
    print(f"Saved daily data: {DAILY_FILE}")
    print(f"Hourly rows: {len(hourly):,}")
    print(f"Daily rows: {len(daily):,}")


def step_4_eda() -> None:
    print("\nSTEP 4: EDA")
    print("=" * 60)
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

    print(f"Peak hour: {int(peak_hour['hour'])}:00")
    print(f"Peak month: {int(peak_month['month'])}")
    print("\nWeekday vs weekend:")
    print(weekday_weekend)
    print("\nTop 3 high consumption days:")
    print(top_days[["datetime", "daily_consumption"]].head(3))


def step_5_anomaly_detection() -> None:
    print("\nSTEP 5: ANOMALY DETECTION")
    print("=" * 60)
    daily = load_daily_data()
    scored_daily = detect_zscore_anomalies(daily)
    anomalies = scored_daily[scored_daily["status"] == "Abnormal"]

    scored_daily.to_csv(TABLE_DIR / "daily_consumption_with_zscore.csv", index=False)
    anomalies.to_csv(TABLE_DIR / "zscore_anomalies.csv", index=False)

    print(f"Abnormal days: {len(anomalies):,}")
    print(anomalies[["datetime", "daily_consumption", "z_score", "status"]].head(5))


def step_6_pattern_mining() -> None:
    print("\nSTEP 6: PATTERN MINING")
    print("=" * 60)
    daily = load_daily_data()
    transactions = build_daily_transactions(daily)
    frequent_itemsets, rules = mine_patterns(transactions)

    transactions.to_csv(TABLE_DIR / "daily_transactions.csv", index=False)
    convert_frozensets_to_text(frequent_itemsets).to_csv(
        TABLE_DIR / "frequent_itemsets.csv",
        index=False,
    )
    convert_frozensets_to_text(rules).to_csv(
        TABLE_DIR / "association_rules.csv",
        index=False,
    )

    print(f"Transactions: {len(transactions):,}")
    print(f"Frequent itemsets: {len(frequent_itemsets):,}")
    print(f"Association rules: {len(rules):,}")


def main() -> None:
    step_1_inspect_raw_data()
    step_2_clean_data()
    step_3_resample_data()
    step_4_eda()
    step_5_anomaly_detection()
    step_6_pattern_mining()

    print("\nPIPELINE COMPLETED")
    print("=" * 60)
    print(f"Processed data folder: {ROOT_DIR / 'data' / 'processed'}")
    print(f"Output folder: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
