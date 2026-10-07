"""Prepare a portrait with a plain white backdrop; keep the original photo local."""
import argparse
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps


def local_contrast(gray, clip_limit=2.0, tiles=8):
    """Contrast-limited adaptive histogram equalization, implemented in NumPy.

    Clip each tile histogram and bilinearly blend its lookup table with adjacent
    tiles. This keeps the guide's local contrast step without an OpenCV runtime.
    """
    height, width = gray.shape
    tile_h, tile_w = (height+tiles-1)//tiles, (width+tiles-1)//tiles
    padded = np.pad(gray, ((0, tile_h*tiles-height), (0, tile_w*tiles-width)), mode="reflect")
    lookup = np.empty((tiles, tiles, 256), dtype=float)
    for ty in range(tiles):
        for tx in range(tiles):
            tile = padded[ty*tile_h:(ty+1)*tile_h, tx*tile_w:(tx+1)*tile_w]
            histogram = np.bincount(tile.ravel(), minlength=256)
            limit = max(1, int(clip_limit*tile.size/256))
            excess = int(np.maximum(histogram-limit, 0).sum())
            histogram = np.minimum(histogram, limit)
            histogram += excess//256
            remainder = excess % 256
            if remainder:
                histogram[np.linspace(0, 255, remainder, dtype=int)] += 1
            lookup[ty, tx] = np.cumsum(histogram)*255/tile.size
    yy, xx = np.mgrid[:height, :width]
    gy, gx = yy/tile_h-.5, xx/tile_w-.5
    y0, x0 = np.floor(gy).astype(int), np.floor(gx).astype(int)
    wy, wx = gy-y0, gx-x0
    y1, x1 = np.clip(y0+1, 0, tiles-1), np.clip(x0+1, 0, tiles-1)
    y0, x0 = np.clip(y0, 0, tiles-1), np.clip(x0, 0, tiles-1)
    result = ((1-wy)*((1-wx)*lookup[y0,x0,gray]+wx*lookup[y0,x1,gray])
              + wy*((1-wx)*lookup[y1,x0,gray]+wx*lookup[y1,x1,gray]))
    return np.clip(result, 0, 255).astype(np.uint8)


def prepare(source, output):
    # This supplied portrait already has a clean white background. Preserve that
    # mask through CLAHE instead of downloading a background-removal model.
    image = ImageOps.exif_transpose(Image.open(source)).convert("RGB")
    rgb = np.array(image)
    background = np.min(rgb, axis=2) >= 245
    gray = np.array(image.convert("L"))
    enhanced = local_contrast(gray)
    enhanced[background] = 255
    Image.fromarray(enhanced).save(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, default=Path("source-prepped.png"))
    args = parser.parse_args()
    prepare(args.source, args.output)
