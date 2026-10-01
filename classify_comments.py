import csv
import json
import ssl
import time
import urllib.request

# Bypass local SSL certificate checks cleanly for macOS/PyCharm
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# CONFIGURATION
# Set MOCK_MODE = False when you are ready to use a real OpenAI API key
MOCK_MODE = True
API_KEY = "YOUR_OPENAI_API_KEY"

INPUT_CSV = "reddit_brand_comments.csv"
OUTPUT_CSV = "reddit_brand_comments_classified.csv"


def classify_with_llm(comment_text, subreddit):
    """Sends a single comment to the LLM API for JSON classification."""
    prompt = f"""
    Analyze this Reddit comment regarding r/{subreddit}.
    Classify the consumer's purchasing mindset and attitude toward dupes/alternatives.

    Comment: "{comment_text}"

    Return ONLY a JSON object with this exact structure:
    {{
        "primary_driver": "Identity_Status" OR "Utility_Function" OR "Community_Belonging" OR "Neutral",
        "dupe_attitude": "Rejects_Dupes" OR "Accepts_Dupes" OR "Neutral_Not_Mentioned",
        "investment_rationalization": true OR false,
        "key_phrase": "Short 3-6 word quote from comment showing their driver"
    }}
    """

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a consumer psychology analyzer. Output strict JSON only."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.1
    }

    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)

    try:
        with urllib.request.urlopen(req, context=ssl_context) as response:
            result = json.loads(response.read().decode("utf-8"))
            return json.loads(result["choices"][0]["message"]["content"])
    except Exception as e:
        print(f"API Error: {e}")
        return {
            "primary_driver": "Error",
            "dupe_attitude": "Error",
            "investment_rationalization": False,
            "key_phrase": ""
        }


def mock_classifier(comment_text, subreddit):
    """Simulates AI consumer psychology classification for pipeline testing."""
    text_lower = comment_text.lower()

    is_identity = any(k in text_lower for k in
                      ["love", "obsessed", "flex", "cute", "color", "style", "community", "collection", "align",
                       "scuba", "stanley", "tumbler", "quencher", "pink", "drop", "cup", "display"])
    rejects_dupe = any(k in text_lower for k in
                       ["dupe isn't same", "fake", "original", "nothing compares", "quality difference",
                        "cannot be replicated", "knockoff", "cheap", "leak", "real one", "walmart version"])
    accepts_dupe = any(k in text_lower for k in
                       ["amazon dupe", "cheaper", "same thing", "save money", "identical", "crz yoga",
                        "prefer it over"])
    is_investment = any(k in text_lower for k in
                        ["investment", "worth it", "lasts forever", "quality", "durable", "worth every penny",
                         "last 5+ years", "use it daily"])

    return {
        "primary_driver": "Identity_Status" if is_identity else "Utility_Function",
        "dupe_attitude": "Rejects_Dupes" if rejects_dupe else (
            "Accepts_Dupes" if accepts_dupe else "Neutral_Not_Mentioned"),
        "investment_rationalization": is_investment,
        "key_phrase": comment_text[:35] + "..."
    }


def run():
    """Main execution function for comment classification."""
    print("Starting classification process...")

    try:
        with open(INPUT_CSV, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: Could not find '{INPUT_CSV}'. Make sure your scraper finished running first.")
        return

    if not rows:
        print("Warning: Input CSV is empty.")
        return

    fieldnames = list(rows[0].keys()) + [
        "primary_driver", "dupe_attitude", "investment_rationalization", "key_phrase"
    ]

    processed_count = 0

    with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            comment_text = row.get("comment_text", "")
            subreddit = row.get("subreddit", "")

            if MOCK_MODE:
                analysis = mock_classifier(comment_text, subreddit)
            else:
                analysis = classify_with_llm(comment_text, subreddit)
                time.sleep(0.5)

            row["primary_driver"] = analysis.get("primary_driver", "Neutral")
            row["dupe_attitude"] = analysis.get("dupe_attitude", "Neutral_Not_Mentioned")
            row["investment_rationalization"] = analysis.get("investment_rationalization", False)
            row["key_phrase"] = analysis.get("key_phrase", "")

            writer.writerow(row)
            processed_count += 1

            if processed_count % 10 == 0 or processed_count == len(rows):
                print(f"Processed {processed_count}/{len(rows)} comments...")

    print(f"\nSuccess! Enriched dataset saved to '{OUTPUT_CSV}'.")


if __name__ == "__main__":
    run()