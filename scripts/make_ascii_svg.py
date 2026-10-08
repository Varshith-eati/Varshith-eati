"""Generate a monochrome, row-by-row typing portrait without JavaScript."""
import argparse
from pathlib import Path
from PIL import Image
from svg_common import ROOT, FG, MUTED, begin, chrome, text, save, animated

RAMP = " .`:-=+*cs#%@"


def render(source, output):
    image = Image.open(source).convert("L")
    # Head-and-shoulders framing fits the terminal panel without stretching the
    # face. Correct for the actual glyph advance / row height, not a guessed 1:2.
    image = image.crop((0, 0, image.width, min(image.height, round(image.width * .91))))
    columns = 100
    rows = round(columns * image.height / image.width * (3.3 / 4.75))
    grid = image.resize((columns, rows), Image.Resampling.LANCZOS)
    parts = begin(370, 400, "ASCII portrait of Eati Varshith",
                  "A monochrome portrait generated from my photo, typing one row at a time.")
    chrome(parts, "My ASCII portrait", 370)
    parts.append('<style>@keyframes wipe{from{width:0}to{width:330px}}'
                 '@keyframes cursor{0%{opacity:1}99%{opacity:1}100%{opacity:0}}'
                 '@keyframes travel{from{transform:translateX(0)}to{transform:translateX(330px)}}'
                 '@media(prefers-reduced-motion:reduce){.cursor{display:none}}</style>')
    parts.append('<defs>')
    for row in range(rows):
        delay = row * .033
        style = f' style="animation:wipe .16s linear {delay:.3f}s both"' if animated() else ""
        parts.append(f'<clipPath id="row-{row}"><rect class="reveal" x="20" y="{62+row*4.75:.2f}" '
                     f'width="330" height="4.75"{style}/></clipPath>')
    parts.append('</defs>')
    for row in range(rows):
        line = "".join(RAMP[min(len(RAMP)-1, int((255-grid.getpixel((col,row)))/255*(len(RAMP)-1)))]
                       for col in range(columns))
        parts.append(text(20, 66+row*4.75, line, 5.5, FG,
                          f'class="ascii" xml:space="preserve" textLength="330" lengthAdjust="spacingAndGlyphs" clip-path="url(#row-{row})"'))
        if animated():
            parts.append(f'<rect class="cursor" x="20" y="{62+row*4.75:.2f}" width="3.3" height="4.75" '
                         f'fill="{FG}" opacity="0" style="animation:travel .16s linear {row*.033:.3f}s both,'
                         f'cursor .16s step-end {row*.033:.3f}s"/>')
    parts.append(text(20, 382, "Made from my photo", 11, MUTED))
    save(output, parts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, nargs="?", default=ROOT / "source-prepped.png")
    parser.add_argument("--output", type=Path, default=ROOT / "varshith-ascii.svg")
    args = parser.parse_args()
    render(args.source, args.output)
