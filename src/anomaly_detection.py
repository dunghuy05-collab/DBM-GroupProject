from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
OUTPUT_DIR = ROOT_DIR / "outputs"
TABLE_DIR = OUTPUT_DIR / "tables"

DAILY_FILE = PROCESSED_DIR / "daily_consumption.csv"
ANOMALY_FILE = TABLE_DIR / "zscore_anomalies.csv"
DAILY_WITH_SCORE_FILE = TABLE_DIR / "daily_consumption_with_zscore.csv"


def load_daily_data() -> pd.DataFrame:
    if not DAILY_FILE.exists():
        raise FileNotFoundError(
            "Daily data file not found.\n\n"
            "Run this command first:\n"
            "python src/resample_data.py"
        )

    return pd.read_csv(DAILY_FILE, parse_dates=["datetime"])


def detect_zscore_anomalies(daily: pd.DataFrame, threshold: float = 3.0) -> pd.DataFrame:
    result = daily.copy()

    mean_consumption = result["daily_consumption"].mean()
    std_consumption = result["daily_consumption"].std()

    result["z_score"] = (
        (result["daily_consumption"] - mean_consumption) / std_consumption
    )

    result["status"] = "Normal"
    result.loc[result["z_score"].abs() > threshold, "status"] = "Abnormal"

    return result


def main() -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    daily = load_daily_data()
    scored_daily = detect_zscore_anomalies(daily)
    anomalies = scored_daily[scored_daily["status"] == "Abnormal"]

    scored_daily.to_csv(DAILY_WITH_SCORE_FILE, index=False)
    anomalies.to_csv(ANOMALY_FILE, index=False)

    print("ANOMALY DETECTION COMPLETED")
    print("-" * 40)
    print(f"Total days: {len(scored_daily):,}")
    print(f"Abnormal days: {len(anomalies):,}")
    print(f"Output file: {ANOMALY_FILE}")

    print("\nTOP ABNORMAL DAYS")
    print("-" * 40)
    columns = ["datetime", "daily_consumption", "z_score", "status"]
    print(anomalies.sort_values("z_score", ascending=False)[columns].head(10))


if __name__ == "__main__":
    main()
