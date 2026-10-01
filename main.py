# main.py
import scrape_reddit
import classify_comments
import aggregated_results
import plot_moat

if __name__ == "__main__":
    print("🚀 Starting End-to-End Brand Moat Pipeline...")
    scrape_reddit.run()
    classify_comments.run()
    aggregated_results.run()
    plot_moat.run()
    print("✅ Pipeline Complete! Output updated.")