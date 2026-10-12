"""
Customer Churn Investigation Pipeline
Arrowstack Data Science 1-Month Internship

Author: Emmanuel Bright Chetachi
Roll/App ID: AS-2026-18951
Email: emmanuelchetachibright@gmail.com
"""

import os
import csv
import sys


def clean_customer_churn_data(raw_filepath="WA_Fn-UseC_-Telco-Customer-Churn.csv",
                              output_filepath="cleaned_customer_churn.csv"):
    """
    Ingests raw Telco customer churn dataset, performs data audit,
    resolves whitespace strings in TotalCharges, imputes tenure=0 records with 0.0,
    and exports the cleaned CSV.
    """
    if not os.path.exists(raw_filepath):
        raise FileNotFoundError(f"Source file not found at: {raw_filepath}")

    print("=" * 60)
    print("STEP 1: DATA INGESTION & QUALITY AUDIT")
    print("=" * 60)
    print(f"Loading raw dataset: {raw_filepath}")

    with open(raw_filepath, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        total_charges_idx = header.index("TotalCharges")
        tenure_idx = header.index("tenure")

        seen = set()
        dup_count = 0
        blank_charges = 0
        tenure_zero_imputed = 0
        cleaned_rows = []

        for row in reader:
            row_tuple = tuple(row)
            if row_tuple in seen:
                dup_count += 1
            seen.add(row_tuple)

            val = row[total_charges_idx].strip()
            if val == "":
                blank_charges += 1
                if int(row[tenure_idx]) == 0:
                    tenure_zero_imputed += 1
                row[total_charges_idx] = "0.0"
            else:
                row[total_charges_idx] = str(float(val))

            cleaned_rows.append(row)

    print(f"Total Records Analyzed: {len(cleaned_rows):,}")
    print(f"Duplicate Rows Detected: {dup_count}")
    print(f"Whitespace entries converted in TotalCharges: {blank_charges}")
    print(f"TotalCharges imputed to 0.0 for tenure=0 months: {tenure_zero_imputed}")

    with open(output_filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(cleaned_rows)

    print(f"Data cleaning complete. Saved to: {output_filepath}\n")
    return output_filepath


def compute_statistical_aggregations(cleaned_filepath="cleaned_customer_churn.csv"):
    """
    Computes statistical summaries, contract churn rates,
    tenure distribution, and monthly charge benchmarks.
    """
    print("=" * 60)
    print("STEP 2: STATISTICAL AGGREGATIONS & EDA")
    print("=" * 60)

    with open(cleaned_filepath, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        records = list(reader)

    total_customers = len(records)
    churn_yes = [r for r in records if r["Churn"] == "Yes"]
    churn_no = [r for r in records if r["Churn"] == "No"]
    churn_rate = (len(churn_yes) / total_customers) * 100

    print(f"Total Customer Accounts: {total_customers:,}")
    print(f"Retained Customers: {len(churn_no):,} ({len(churn_no)/total_customers*100:.2f}%)")
    print(f"Churned Customers:  {len(churn_yes):,} ({churn_rate:.2f}%)")

    # Contract Analysis
    contracts = {}
    for r in records:
        c = r["Contract"]
        contracts.setdefault(c, {"total": 0, "churn": 0})
        contracts[c]["total"] += 1
        if r["Churn"] == "Yes":
            contracts[c]["churn"] += 1

    print("\n--- Churn Rate by Contract Type ---")
    for c, stats in sorted(contracts.items()):
        rate = (stats["churn"] / stats["total"]) * 100
        print(f"  * {c:20s}: {stats['churn']:>4d} / {stats['total']:>4d} ({rate:5.2f}%)")

    # Internet Service
    services = {}
    for r in records:
        srv = r["InternetService"]
        services.setdefault(srv, {"total": 0, "churn": 0})
        services[srv]["total"] += 1
        if r["Churn"] == "Yes":
            services[srv]["churn"] += 1

    print("\n--- Churn Rate by Internet Service ---")
    for srv, stats in sorted(services.items()):
        rate = (stats["churn"] / stats["total"]) * 100
        print(f"  * {srv:20s}: {stats['churn']:>4d} / {stats['total']:>4d} ({rate:5.2f}%)")

    # Fiber optic + month to month
    fo_m2m = [r for r in records if r["InternetService"] == "Fiber optic" and r["Contract"] == "Month-to-month"]
    fo_m2m_churn = [r for r in fo_m2m if r["Churn"] == "Yes"]
    fo_m2m_rate = (len(fo_m2m_churn) / len(fo_m2m)) * 100
    print(f"\n  * High-Risk Combo (Fiber Optic + Month-to-month): {len(fo_m2m_churn)} / {len(fo_m2m)} ({fo_m2m_rate:.2f}%)")

    # Tenure Buckets
    tenure_buckets = {
        "0 - 12 Months":  {"total": 0, "churn": 0},
        "13 - 24 Months": {"total": 0, "churn": 0},
        "25 - 48 Months": {"total": 0, "churn": 0},
        "49 - 72 Months": {"total": 0, "churn": 0},
    }
    for r in records:
        t = int(r["tenure"])
        b = "0 - 12 Months" if t <= 12 else "13 - 24 Months" if t <= 24 else "25 - 48 Months" if t <= 48 else "49 - 72 Months"
        tenure_buckets[b]["total"] += 1
        if r["Churn"] == "Yes":
            tenure_buckets[b]["churn"] += 1

    print("\n--- Churn by Tenure Bracket ---")
    for b, stats in tenure_buckets.items():
        rate = (stats["churn"] / stats["total"]) * 100
        print(f"  * {b:20s}: {stats['churn']:>4d} / {stats['total']:>4d} ({rate:5.2f}%)")

    # Payment Methods
    payments = {}
    for r in records:
        p = r["PaymentMethod"]
        payments.setdefault(p, {"total": 0, "churn": 0})
        payments[p]["total"] += 1
        if r["Churn"] == "Yes":
            payments[p]["churn"] += 1

    print("\n--- Churn Rate by Payment Method ---")
    for p, stats in sorted(payments.items()):
        rate = (stats["churn"] / stats["total"]) * 100
        print(f"  * {p:30s}: {stats['churn']:>4d} / {stats['total']:>4d} ({rate:5.2f}%)")
    print("=" * 60 + "\n")


def generate_visualizations(cleaned_filepath="cleaned_customer_churn.csv", output_dir="output/figures"):
    """
    Generates EDA plots using matplotlib and seaborn if installed.
    """
    try:
        import pandas as pd
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError:
        print("[Notice] matplotlib/seaborn not found. Skipping plot regeneration (pre-extracted figures are in output/figures/).")
        return

    os.makedirs(output_dir, exist_ok=True)
    sns.set_style("whitegrid")
    df = pd.read_csv(cleaned_filepath)

    # 1. Churn by Contract Type
    contract_df = df.groupby("Contract")["Churn"].value_counts(normalize=True).rename("Percentage").reset_index()
    contract_df["Percentage"] *= 100

    plt.figure(figsize=(8, 5))
    sns.barplot(x="Contract", y="Percentage", hue="Churn", data=contract_df, palette="Set2")
    plt.title("Churn Rate Breakdown By Contract Type", fontsize=13, fontweight="bold")
    plt.ylabel("Percentage (%)")
    plt.xlabel("Contract Type")
    plt.tight_layout()
    plot1_path = os.path.join(output_dir, "churn_by_contract.png")
    plt.savefig(plot1_path, dpi=300)
    plt.close()
    print(f"Saved: {plot1_path}")

    # 2. Tenure Distribution
    plt.figure(figsize=(8, 5))
    sns.histplot(data=df, x="tenure", hue="Churn", multiple="stack", palette="muted", bins=30)
    plt.title("Customer Tenure Distribution by Churn Status", fontsize=13, fontweight="bold")
    plt.xlabel("Tenure (Months)")
    plt.ylabel("Customer Count")
    plt.tight_layout()
    plot2_path = os.path.join(output_dir, "tenure_distribution.png")
    plt.savefig(plot2_path, dpi=300)
    plt.close()
    print(f"Saved: {plot2_path}")

    # 3. Monthly Charges Comparison
    plt.figure(figsize=(8, 5))
    sns.boxplot(x="Churn", y="MonthlyCharges", data=df, palette="Set2")
    plt.title("Monthly Charges Comparison by Churn Status", fontsize=13, fontweight="bold")
    plt.xlabel("Churn Status")
    plt.ylabel("Monthly Charges ($)")
    plt.tight_layout()
    plot3_path = os.path.join(output_dir, "monthly_charges_boxplot.png")
    plt.savefig(plot3_path, dpi=300)
    plt.close()
    print(f"Saved: {plot3_path}")


if __name__ == "__main__":
    raw_csv = "WA_Fn-UseC_-Telco-Customer-Churn.csv"
    cleaned_csv = clean_customer_churn_data(raw_csv)
    compute_statistical_aggregations(cleaned_csv)
    generate_visualizations(cleaned_csv)
