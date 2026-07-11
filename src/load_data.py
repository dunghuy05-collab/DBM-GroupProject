from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT_DIR / "data" / "raw" / "household_power_consumption.txt"


def load_raw_data() -> pd.DataFrame:
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            "Dataset file not found.\n"
            f"Expected path: {RAW_FILE}\n\n"
            "Download the UCI dataset, unzip it, then place "
            "household_power_consumption.txt inside data/raw/."
        )

    return pd.read_csv(
        RAW_FILE,
        sep=";",
        na_values=["?", ""],
        low_memory=False,
    )


def inspect_data(df: pd.DataFrame) -> None:
    print("DATASET OVERVIEW")
    print("-" * 40)
    print(f"Rows: {df.shape[0]:,}")
    print(f"Columns: {df.shape[1]:,}")

    print("\nCOLUMN NAMES")
    print("-" * 40)
    for column in df.columns:
        print(column)

    print("\nFIRST 5 ROWS")
    print("-" * 40)
    print(df.head())

    print("\nDATA TYPES")
    print("-" * 40)
    print(df.dtypes)

    print("\nMISSING VALUES")
    print("-" * 40)
    print(df.isna().sum())


def main() -> None:
    df = load_raw_data()
    inspect_data(df)


if __name__ == "__main__":
    main()
