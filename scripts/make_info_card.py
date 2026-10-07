"""Edit data/profile.json, then regenerate the neofetch card."""
import json
from svg_common import ROOT, FG, MUTED, GREEN, begin, chrome, text, save, animated


def render(profile, output):
    parts = begin(490, 400, f'{profile["name"]} - profile',
                  f'{profile["role"]}. Building {profile["building"]}. Learning {profile["learning"]}.')
    chrome(parts, "~/about / neofetch", 490)
    parts.append('<style>@keyframes enter{from{opacity:0;transform:translateY(5px)}'
                 'to{opacity:1;transform:translateY(0)}}</style>')
    parts.append(text(24, 72, profile["username"] + "@github", 16, GREEN))
    parts.append(text(24, 93, "-----------------------------------------", 12, MUTED))
    rows = [("Name", profile["name"]), ("Role", profile["role"]), ("Now", profile["building"]),
            ("Learn", profile["learning"]), ("Lang", profile["languages"]), ("Web", profile["web"]),
            ("Data", profile["data"]), ("Tools", profile["tools"]),
            ("Built", profile["highlights"][0]), ("", profile["highlights"][1]), ("Since", profile["since"])]
    for index, (key, value) in enumerate(rows):
        if len(value) > 48:
            raise ValueError(f"Profile value too long for card: {key}")
        style = f' style="animation:enter .32s ease-out {index*.10:.2f}s both"' if animated() else ""
        parts.append(f'<g class="reveal"{style}>')
        parts.append(text(24, 120+index*21, key + (":" if key else ""), 11.5, GREEN))
        parts.append(text(85, 120+index*21, value, 11.5, FG))
        parts.append('</g>')
    parts.append(text(24, 379, "$ " + profile["motto"], 11, MUTED))
    for i, color in enumerate(["#0e4429", "#006d32", "#26a641", "#39d353", GREEN]):
        parts.append(f'<rect x="{366+i*18}" y="365" width="16" height="16" rx="2" fill="{color}"/>')
    save(output, parts)


if __name__ == "__main__":
    render(json.loads((ROOT / "data/profile.json").read_text(encoding="utf-8")), ROOT / "info-card.svg")
