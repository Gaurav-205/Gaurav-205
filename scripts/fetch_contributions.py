import re
import sys
import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

def parse_count(text):
    if not text or "No contributions" in text:
        return 0
    # Match numbers with potential commas: "2 contributions", "1 contribution", "1,234 contributions"
    match = re.match(r'^([\d,]+)\s+contribution', text)
    if match:
        return int(match.group(1).replace(',', ''))
    return 0

def fetch_contributions(username="Gaurav-205"):
    url = f"https://github.com/users/{username}/contributions"
    print(f"Fetching contributions from {url}...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print(f"Error fetching URL: {e}")
        sys.exit(1)
        
    soup = BeautifulSoup(r.text, "html.parser")
    
    # Map from tooltip ID target to tooltip content
    tooltips = {}
    for t in soup.find_all("tool-tip"):
        target = t.get("for")
        if target:
            tooltips[target] = t.text.strip()
            
    # Extract days
    days = []
    total_count = 0
    best_day = {"date": None, "count": -1}
    monthly_totals = {}
    
    day_elements = soup.find_all(class_="ContributionCalendar-day")
    if not day_elements:
        print("Error: No contribution calendar days found in the response HTML.")
        print("Saving response to debug_contributions.html for diagnostics...")
        with open("debug_contributions.html", "w", encoding="utf-8") as f:
            f.write(r.text)
        sys.exit(1)
        
    for td in day_elements:
        day_id = td.get("id")
        date_str = td.get("data-date")
        level = int(td.get("data-level", 0))
        
        if not date_str:
            continue
            
        # Parse count from tooltip, fallback to level-based estimate if missing
        tooltip_text = tooltips.get(day_id, "")
        count = parse_count(tooltip_text)
        
        # Accumulate stats
        total_count += count
        
        if count > best_day["count"]:
            best_day = {"date": date_str, "count": count}
            
        # Monthly totals
        # Date format: YYYY-MM-DD -> extract YYYY-MM
        month = date_str[:7]
        monthly_totals[month] = monthly_totals.get(month, 0) + count
        
        days.append({
            "date": date_str,
            "level": level,
            "count": count
        })
        
    # Calculate streaks
    sorted_days = sorted(days, key=lambda x: x["date"])
    longest_streak = 0
    temp_streak = 0
    
    for d in sorted_days:
        if d["count"] > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0
            
    # Calculate current streak backwards from latest day
    # Allow 0 contributions on the latest day if the day before had contributions
    active_backwards = [d["count"] > 0 for d in reversed(sorted_days)]
    
    if len(active_backwards) >= 2 and not active_backwards[0] and not active_backwards[1]:
        current_streak = 0
    else:
        streak = 0
        started = False
        for has_contrib in active_backwards:
            if has_contrib:
                streak += 1
                started = True
            else:
                if started:
                    break
                else:
                    continue
        current_streak = streak
        
    data = {
        "username": username,
        "total": total_count,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": monthly_totals,
        "days": sorted_days,
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    with open("data/contributions.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        
    print(f"Successfully scraped contributions for {username}.")
    print(f"Total: {total_count} | Longest Streak: {longest_streak} | Current Streak: {current_streak}")
    print(f"Data saved to data/contributions.json")

if __name__ == "__main__":
    username = "Gaurav-205"
    if len(sys.argv) > 1:
        username = sys.argv[1]
    fetch_contributions(username)
