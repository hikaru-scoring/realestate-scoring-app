#!/usr/bin/env python3
"""Daily score recorder for REALESTATE-1000 (standalone, no Streamlit dependency)."""
import json
import os
import sys
from datetime import date

from data_logic import get_state_rankings, get_metro_rankings

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "scores_history.json")


def main():
    today_str = date.today().isoformat()
    print(f"[REALESTATE-1000] Recording scores for {today_str}")

    # Load history
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    else:
        history = {}

    # Skip if already recorded today
    if today_str in history:
        print(f"[REALESTATE-1000] Scores already recorded for {today_str}, skipping")
        sys.exit(0)

    day_scores = {}

    # Score all states
    print("  Scoring states...")
    states = get_state_rankings()
    for s in states:
        key = f"State:{s['abbr']}"
        day_scores[key] = s["total"]
        print(f"    {s['name']}: {s['total']}")

    # Score all metros
    print("  Scoring metro areas...")
    metros = get_metro_rankings()
    for m in metros:
        key = f"Metro:{m['name']}"
        day_scores[key] = m["total"]
        print(f"    {m['name']}: {m['total']}")

    if len(day_scores) < 10:
        print(f"ERROR: Only {len(day_scores)} markets scored, skipping save")
        sys.exit(1)

    history[today_str] = day_scores

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, separators=(",", ":"))

    print(f"[REALESTATE-1000] Saved {len(day_scores)} scores for {today_str}")


if __name__ == "__main__":
    main()
