from pathlib import Path

import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder


ROOT_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
OUTPUT_DIR = ROOT_DIR / "outputs"
TABLE_DIR = OUTPUT_DIR / "tables"

DAILY_FILE = PROCESSED_DIR / "daily_consumption.csv"
FREQUENT_ITEMSETS_FILE = TABLE_DIR / "frequent_itemsets.csv"
ASSOCIATION_RULES_FILE = TABLE_DIR / "association_rules.csv"
TRANSACTIONS_FILE = TABLE_DIR / "daily_transactions.csv"


def load_daily_data() -> pd.DataFrame:
    if not DAILY_FILE.exists():
        raise FileNotFoundError(
            "Daily data file not found.\n\n"
            "Run this command first:\n"
            "python src/resample_data.py"
        )

    return pd.read_csv(DAILY_FILE, parse_dates=["datetime"])


def bucket_by_quantile(series: pd.Series, prefix: str) -> pd.Series:
    labels = [f"{prefix}_low", f"{prefix}_medium", f"{prefix}_high"]
    ranked = series.rank(method="first")
    return pd.qcut(ranked, q=3, labels=labels)


def build_daily_transactions(daily: pd.DataFrame) -> pd.DataFrame:
    data = daily.copy()

    data["total_usage"] = bucket_by_quantile(data["daily_consumption"], "total_usage")
    data["evening_usage"] = bucket_by_quantile(data["evening_usage_ratio"], "evening_usage")
    data["night_usage"] = bucket_by_quantile(data["night_usage_ratio"], "night_usage")
    data["variability"] = bucket_by_quantile(data["max_hourly_consumption"], "peak_hour_usage")
    data["weekend"] = data["is_weekend"].map({0: "weekend_no", 1: "weekend_yes"})

    transaction_columns = [
        "datetime",
        "weekend",
        "total_usage",
        "evening_usage",
        "night_usage",
        "variability",
    ]
    return data[transaction_columns]


def mine_patterns(transactions_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    transaction_items = (
        transactions_df.drop(columns=["datetime"])
        .astype(str)
        .values
        .tolist()
    )

    encoder = TransactionEncoder()
    encoded_array = encoder.fit(transaction_items).transform(transaction_items)
    encoded_df = pd.DataFrame(encoded_array, columns=encoder.columns_)

    frequent_itemsets = apriori(
        encoded_df,
        min_support=0.08,
        use_colnames=True,
    ).sort_values("support", ascending=False)

    rules = association_rules(
        frequent_itemsets,
        metric="confidence",
        min_threshold=0.5,
    )

    if not rules.empty:
        rules = rules.sort_values(["lift", "confidence", "support"], ascending=False)

    return frequent_itemsets, rules


def convert_frozensets_to_text(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    for column in ["itemsets", "antecedents", "consequents"]:
        if column in result.columns:
            result[column] = result[column].apply(lambda items: ", ".join(sorted(items)))
    return result


def main() -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    daily = load_daily_data()
    transactions = build_daily_transactions(daily)
    frequent_itemsets, rules = mine_patterns(transactions)

    transactions.to_csv(TRANSACTIONS_FILE, index=False)
    convert_frozensets_to_text(frequent_itemsets).to_csv(FREQUENT_ITEMSETS_FILE, index=False)
    convert_frozensets_to_text(rules).to_csv(ASSOCIATION_RULES_FILE, index=False)

    print("PATTERN MINING COMPLETED")
    print("-" * 40)
    print(f"Transactions: {len(transactions):,}")
    print(f"Frequent itemsets: {len(frequent_itemsets):,}")
    print(f"Association rules: {len(rules):,}")

    print("\nTOP FREQUENT ITEMSETS")
    print("-" * 40)
    print(convert_frozensets_to_text(frequent_itemsets).head(10))

    print("\nTOP ASSOCIATION RULES")
    print("-" * 40)
    rule_columns = ["antecedents", "consequents", "support", "confidence", "lift"]
    if rules.empty:
        print("No rules found with current thresholds.")
    else:
        print(convert_frozensets_to_text(rules)[rule_columns].head(10))


if __name__ == "__main__":
    main()
