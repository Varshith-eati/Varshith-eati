from datetime import date, timedelta
from pathlib import Path
import sys
import tempfile
import unittest
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from fetch_contributions import parse_calendar, statistics
from render_heatmap_svg import render


def fragment(as_of, counts=None, legacy=False):
    counts = counts or {}
    start = as_of - timedelta(days=(as_of.weekday()+1) % 7, weeks=52)
    parts = []
    # GitHub emits weekday-first, not date order. Reverse to exercise sorting.
    for offset in reversed(range((as_of-start).days+1)):
        day = start + timedelta(days=offset)
        count = counts.get(day, 0)
        level = min(count, 4)
        if legacy:
            parts.append(f'<rect data-date="{day}" data-level="{level}" data-count="{count}"/>')
        else:
            parts.append(f'<td data-date="{day}" data-level="{level}" id="day-{offset}"></td>')
            label = "No contributions" if not count else f'{count:,} contribution' + ('s' if count != 1 else '')
            parts.append(f'<tool-tip for="day-{offset}">{label} on a date.</tool-tip>')
    return "\n".join(parts)


class CalendarTests(unittest.TestCase):
    def test_real_markup_counts_and_order(self):
        today = date(2026, 10, 7)
        days = parse_calendar(fragment(today, {today: 1234, today-timedelta(days=1): 1}), today)
        self.assertEqual(len(days), 368)
        self.assertEqual(days[0]["date"], "2025-10-05")
        self.assertEqual(days[-1]["count"], 1234)
        self.assertEqual(statistics(days)["total"], 1235)

    def test_current_streak_tolerates_today_zero(self):
        today = date(2026, 10, 7)
        counts = {today-timedelta(days=i): 1 for i in (1, 2, 3, 7, 8, 9, 10)}
        stats = statistics(parse_calendar(fragment(today, counts), today))
        self.assertEqual(stats["current_streak"], 3)
        self.assertEqual(stats["longest_streak"], 4)
        self.assertEqual(sum(stats["monthly_totals"].values()), stats["total"])

    def test_new_year_and_leap_day(self):
        for today in [date(2026, 1, 1), date(2024, 2, 29), date(2026, 10, 4), date(2026, 10, 10)]:
            days = parse_calendar(fragment(today, legacy=True), today)
            self.assertEqual(days[-1]["date"], today.isoformat())
            self.assertEqual(statistics(days)["current_streak"], 0)
            self.assertEqual(date.fromisoformat(days[0]["date"]).weekday(), 6)

    def test_fail_closed_on_incomplete_or_changed_html(self):
        today = date(2026, 10, 7)
        html = fragment(today)
        for broken in ["<html>Rate limited</html>", html.replace('for="day-0"', 'for="missing"'),
                       html.replace('data-level="0"', 'data-level="9"', 1),
                       html + '<td data-date="2026-10-07" data-level="0" data-count="0"></td>']:
            with self.assertRaises((ValueError, KeyError)):
                parse_calendar(broken, today)

    def test_full_grid_and_xml_escaping(self):
        today = date(2026, 10, 7)
        days = parse_calendar(fragment(today, {today: 1}), today)
        data = {"username": "test<&", "as_of": str(today), "start": days[0]["date"],
                "weeks": 53, "days": days, "stats": statistics(days)}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "heatmap.svg"
            render(data, output)
            root = ET.parse(output).getroot()
            ns = {"s": "http://www.w3.org/2000/svg"}
            cells = [r for r in root.findall("s:rect", ns) if r.find("s:title", ns) is not None]
            self.assertEqual(len(cells), 53*7)
            self.assertEqual(len([r for r in cells if "future date" in r.find("s:title", ns).text]), 3)
            self.assertNotIn("<script", output.read_text())


if __name__ == "__main__":
    unittest.main()
