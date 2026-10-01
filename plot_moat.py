import csv
import matplotlib.pyplot as plt

INPUT_SUMMARY = "brand_moat_summary.csv"
OUTPUT_IMAGE = "brand_moat_chart.png"


def run():
    """Reads brand moat summary metrics and auto-generates high-res visual bar charts."""
    brands = []
    identity_scores = []
    dupe_scores = []
    rationalization_scores = []

    # Read data cleanly using native CSV module
    try:
        with open(INPUT_SUMMARY, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                brands.append(f"r/{row['brand']}")
                identity_scores.append(float(row['identity_index_pct']))
                dupe_scores.append(float(row['dupe_resistance_pct']))
                rationalization_scores.append(float(row['rationalization_rate_pct']))
    except FileNotFoundError:
        print(f"Error: Could not find '{INPUT_SUMMARY}'. Run aggregate_results.py first.")
        return

    if not brands:
        print("Warning: No brand data found in summary CSV.")
        return

    # Positioning setup for grouped bar chart
    x = range(len(brands))
    width = 0.25

    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot grouped bar series
    rects1 = ax.bar([i - width for i in x], identity_scores, width, label='Identity Index %', color='#4F46E5')
    rects2 = ax.bar(x, dupe_scores, width, label='Dupe Resistance %', color='#0EA5E9')
    rects3 = ax.bar([i + width for i in x], rationalization_scores, width, label='Rationalization Rate %', color='#10B981')

    # Chart Styling
    ax.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
    ax.set_title('Brand Moat Executive Analysis: Consumer Psychology Metrics', fontsize=14, fontweight='bold', pad=15)
    ax.set_xticks(list(x))
    ax.set_xticklabels(brands, fontsize=11, fontweight='bold')
    ax.set_ylim(0, 110)
    ax.legend(loc='upper right', frameon=True)
    ax.grid(axis='y', linestyle='--', alpha=0.4)

    # Function to attach percentage value labels above each bar
    def add_bar_labels(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

    add_bar_labels(rects1)
    add_bar_labels(rects2)
    add_bar_labels(rects3)

    plt.tight_layout()
    plt.savefig(OUTPUT_IMAGE, dpi=300)
    print(f"Success! High-resolution graphic exported to '{OUTPUT_IMAGE}'.")
    plt.close()  # Closes plot memory buffer cleanly for automated orchestrator execution


if __name__ == "__main__":
    run()