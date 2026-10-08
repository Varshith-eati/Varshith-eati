"""Render a 53-week calendar from validated, publicly visible GitHub data."""
from datetime import date, timedelta
import json
from svg_common import ROOT, FG, MUTED, GREEN, begin, chrome, text, save, animated

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]


def render(data, output):
    start = date.fromisoformat(data["start"])
    as_of = date.fromisoformat(data["as_of"])
    if data["weeks"] != 53 or start.weekday() != 6:
        raise ValueError("Calendar must contain 53 Sunday-first weeks")
    days = {day["date"]: day for day in data["days"]}
    stats = data["stats"]
    parts = begin(860, 278, f'{data["username"]} contribution calendar',
                  f'{stats["total"]:,} publicly visible contributions from {start} through {as_of}. '
                  f'Current streak {stats["current_streak"]} days; longest streak {stats["longest_streak"]} days.')
    chrome(parts, "Contribution activity / 53 weeks", 860)
    parts.append(text(834, 25, "Updated " + data["as_of"] + " UTC", 10, MUTED, 'text-anchor="end"'))
    parts.append('<style>@keyframes cell{from{opacity:0;transform:translateY(-5px)}'
                 'to{opacity:1;transform:translateY(0)}}</style>')
    for weekday, name in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        parts.append(text(18, 88+weekday*14, name, 9, MUTED))
    last_month = None
    for week in range(53):
        sunday = start + timedelta(weeks=week)
        # Label only first visible week of each new month; avoid overlapping the
        # clipped first month label with the next month when it is very short.
        if sunday.month != last_month:
            if week == 0 or week >= 3:
                parts.append(text(58+week*14, 67, sunday.strftime("%b"), 10, MUTED))
            last_month = sunday.month
        for weekday in range(7):
            day = sunday + timedelta(days=weekday)
            x, y = 58+week*14, 78+weekday*14
            if day > as_of:
                parts.append(f'<rect x="{x}" y="{y}" width="11" height="11" rx="2" fill="none" stroke="#21262d"><title>{day}: future date</title></rect>')
                continue
            record = days[day.isoformat()]
            style = f' style="animation:cell .24s ease-out {week*.024+weekday*.028:.3f}s both"' if animated() else ""
            parts.append(f'<rect class="reveal" x="{x}" y="{y}" width="11" height="11" rx="2" '
                         f'fill="{PALETTE[record["level"]]}"{style}><title>{day}: {record["count"]} contributions</title></rect>')
    parts.append(text(58, 196, f'{stats["total"]:,} contributions over the displayed 53 weeks', 12, FG))
    parts.append(text(674, 196, "Less", 9, MUTED))
    for i, color in enumerate(PALETTE):
        parts.append(f'<rect x="{706+i*14}" y="187" width="11" height="11" rx="2" fill="{color}"/>')
    parts.append(text(781, 196, "More", 9, MUTED))
    parts.append('<path d="M24 214H836" stroke="#21262d"/>')
    current_unit = 'day' if stats['current_streak'] == 1 else 'days'
    longest_unit = 'day' if stats['longest_streak'] == 1 else 'days'
    parts.append(text(24, 240, f'Current streak: {stats["current_streak"]} {current_unit}', 11, GREEN))
    parts.append(text(220, 240, f'Longest streak: {stats["longest_streak"]} {longest_unit}', 11, GREEN))
    parts.append(text(421, 240, f'Best day: {stats["best_day"]["count"]} contributions', 11, GREEN))
    parts.append(text(834, 240, "From my GitHub activity", 10, MUTED, 'text-anchor="end"'))
    parts.append(text(24, 262, "Daily snapshot / streaks calculated within the displayed period", 9, MUTED))
    save(output, parts)


if __name__ == "__main__":
    render(json.loads((ROOT / "data/contributions.json").read_text(encoding="utf-8")), ROOT / "contrib-heatmap.svg")
