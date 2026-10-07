"""Fetch GitHub's public contribution HTML. No PAT or third-party service needed."""
import argparse
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = []
        self.tips = {}
        self.active_tip = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("td", "rect") and "data-date" in attrs:
            self.cells.append(attrs)
        if tag == "tool-tip" and attrs.get("for"):
            self.active_tip = attrs["for"]
            self.tips[self.active_tip] = ""

    def handle_data(self, value):
        if self.active_tip:
            self.tips[self.active_tip] += value

    def handle_endtag(self, tag):
        if tag == "tool-tip":
            self.active_tip = None


def parse_calendar(html, as_of):
    parser = CalendarParser()
    parser.feed(html)
    # Exactly 53 Sunday-first week columns, including the current partial week.
    end_week = as_of - timedelta(days=(as_of.weekday()+1) % 7)
    start = end_week - timedelta(weeks=52)
    days = {}
    for attrs in parser.cells:
        day = date.fromisoformat(attrs["data-date"])
        if not start <= day <= as_of:
            continue
        if day in days:
            raise ValueError(f"Duplicate contribution date: {day}")
        level = int(attrs["data-level"])
        if level not in range(5):
            raise ValueError(f"Unknown contribution intensity: {level}")
        if "data-count" in attrs:
            count_text = attrs["data-count"].replace(",", "")
        else:
            tip = parser.tips.get(attrs.get("id", ""), "")
            match = re.search(r"\b(No|[\d,]+) contributions?\b", tip, re.I)
            if not match:
                raise ValueError(f"Missing contribution count for {day}; HTML may have changed")
            count_text = match[1].replace(",", "")
        count = 0 if count_text.lower() == "no" else int(count_text)
        if count < 0 or (count == 0) != (level == 0):
            raise ValueError(f"Inconsistent contribution count/level for {day}")
        days[day] = {"date": day.isoformat(), "count": count, "level": level}
    expected = (as_of-start).days + 1
    if len(days) != expected:
        raise ValueError(f"Incomplete calendar: expected {expected} days, got {len(days)}; keeping previous output")
    return [days[key] for key in sorted(days)]


def statistics(days):
    longest = run = 0
    monthly = {}
    for day in days:
        run = run+1 if day["count"] else 0
        longest = max(longest, run)
        month = day["date"][:7]
        monthly[month] = monthly.get(month, 0) + day["count"]
    # A zero today doesn't end yesterday's streak before today is over.
    current = 0
    tail = days if days[-1]["count"] else days[:-1]
    for day in reversed(tail):
        if not day["count"]:
            break
        current += 1
    return {"total": sum(d["count"] for d in days), "current_streak": current,
            "longest_streak": longest, "best_day": max(days, key=lambda d: d["count"]),
            "monthly_totals": monthly}


def fetch_html(username, as_of):
    # GitHub's unfiltered fragment is the rolling calendar. A cross-year from/to
    # query can silently return only the current calendar year, so don't use it.
    url = f"https://github.com/users/{username}/contributions"
    request = Request(url, headers={"User-Agent": f"{username}-profile-art/1.0",
                                  "Accept": "text/html", "Accept-Language": "en-US,en;q=0.9"})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                return response.read().decode("utf-8"), url
        except (HTTPError, URLError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username")
    parser.add_argument("--as-of", type=date.fromisoformat, default=datetime.now(timezone.utc).date())
    parser.add_argument("--html", type=Path, help="Read a saved fragment for offline tests")
    parser.add_argument("--output", type=Path, default=ROOT / "data/contributions.json")
    args = parser.parse_args()
    username = args.username or json.loads((ROOT / "data/profile.json").read_text(encoding="utf-8"))["username"]
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", username):
        raise ValueError("Invalid GitHub username")
    if args.html:
        html, source = args.html.read_text(encoding="utf-8"), f"https://github.com/users/{username}/contributions"
    else:
        html, source = fetch_html(username, args.as_of)
    days = parse_calendar(html, args.as_of)
    payload = {"username": username, "source": source, "as_of": args.as_of.isoformat(),
               "start": days[0]["date"], "weeks": 53, "days": days, "stats": statistics(days)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    print(f"Fetched {len(days)} days, {payload['stats']['total']:,} contributions through {args.as_of}")


if __name__ == "__main__":
    main()
