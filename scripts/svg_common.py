"""Small, dependency-free SVG helpers. All artwork works as an embedded image."""
from html import escape
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
BG = "#0d1117"
FG = "#d1d9e0"
MUTED = "#919ba8"
GREEN = "#69f0a0"


def text(x, y, value, size=12, color=FG, extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
            f'{extra}>{escape(str(value))}</text>')


def begin(width, height, title, description):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>',
            '<style>text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}.ascii{font-family:ui-monospace,SFMono-Regular,Consolas,"Liberation Mono",monospace}'
            '@media(prefers-reduced-motion:reduce){.reveal{animation:none!important}}</style>',
            f'<rect width="{width}" height="{height}" rx="12" fill="{BG}"/>',
            f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="12" '
            'fill="none" stroke="#30363d"/>']


def chrome(parts, label, width):
    for i, fill in enumerate(["#6e7681", "#919ba8", "#d1d9e0"]):
        parts.append(f'<circle cx="{20+i*14}" cy="21" r="3.5" fill="{fill}"/>')
    parts.append(text(77, 25, label, 12, MUTED))
    parts.append(f'<path d="M1 40H{width-1}" stroke="#21262d"/>')


def animated():
    return os.environ.get("STATIC") != "1"


def save(path, parts):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text("\n".join(parts + ["</svg>"]) + "\n", encoding="utf-8")
    temporary.replace(path)
