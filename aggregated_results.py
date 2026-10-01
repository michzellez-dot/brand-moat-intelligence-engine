import csv
from collections import defaultdict

INPUT_CSV = "reddit_brand_comments_classified.csv"
OUTPUT_SUMMARY = "brand_moat_summary.csv"


def run():
    """Aggregates classified Reddit comments into quantitative Brand Moat metrics."""
    stats = defaultdict(lambda: {
        "total": 0,
        "identity_driver": 0,
        "utility_driver": 0,
        "rejects_dupes": 0,
        "accepts_dupes": 0,
        "rationalizations": 0
    })

    try:
        with open(INPUT_CSV, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                brand = row.get("subreddit", "unknown")
                driver = row.get("primary_driver", "")
                dupe = row.get("dupe_attitude", "")
                rationalization = row.get("investment_rationalization", "").lower() == "true"

                stats[brand]["total"] += 1

                if driver == "Identity_Status":
                    stats[brand]["identity_driver"] += 1
                elif driver == "Utility_Function":
                    stats[brand]["utility_driver"] += 1

                if dupe == "Rejects_Dupes":
                    stats[brand]["rejects_dupes"] += 1
                elif dupe == "Accepts_Dupes":
                    stats[brand]["accepts_dupes"] += 1

                if rationalization:
                    stats[brand]["rationalizations"] += 1

    except FileNotFoundError:
        print(f"Error: Could not find '{INPUT_CSV}'. Make sure classify_comments.py has finished.")
        return

    print("\n" + "=" * 65)
    print("               BRAND MOAT EXECUTIVE REPORT               ")
    print("=" * 65)

    summary_rows = []

    for brand, s in stats.items():
        total = s["total"]
        if total == 0:
            continue

        identity_pct = (s["identity_driver"] / total) * 100
        dupe_mentions = s["rejects_dupes"] + s["accepts_dupes"]
        dupe_resistance_pct = (s["rejects_dupes"] / dupe_mentions * 100) if dupe_mentions > 0 else 0.0
        rationalization_pct = (s["rationalizations"] / total) * 100

        summary_rows.append({
            "brand": brand,
            "total_comments": total,
            "identity_index_pct": round(identity_pct, 1),
            "dupe_resistance_pct": round(dupe_resistance_pct, 1),
            "rationalization_rate_pct": round(rationalization_pct, 1)
        })

        print(f"\n[ Brand / Community: r/{brand} ]")
        print(f"  • Total Comments Analyzed: {total}")
        print(f"  • Identity Driver Index:   {identity_pct:.1f}%  (Status/Community driven)")
        print(f"  • Dupe Resistance Rate:    {dupe_resistance_pct:.1f}%  (Rejects knockoffs)")
        print(f"  • Rationalization Rate:    {rationalization_pct:.1f}%  (Price justification)")

    # Save summary CSV
    with open(OUTPUT_SUMMARY, mode="w", newline="", encoding="utf-8") as outfile:
        fieldnames = ["brand", "total_comments", "identity_index_pct", "dupe_resistance_pct", "rationalization_rate_pct"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)

    print("\n" + "=" * 65)
    print(f"Success! Final metrics exported to '{OUTPUT_SUMMARY}'.")


if __name__ == "__main__":
    run()