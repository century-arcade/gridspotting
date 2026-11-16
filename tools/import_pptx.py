"""Copy the images that data/sightings.tsv names out of a .pptx into images/,
scaled to at most 1600 px on the long side.

    python tools/import_pptx.py "CC Gridspotting Zimmer.pptx"
"""
import csv
import io
import sys
import zipfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
MAX = 1600


def main(pptx):
    rows = csv.DictReader(open(ROOT / "data/sightings.tsv", encoding="utf8"), delimiter="\t")
    wanted = {name for r in rows for name in r["images"].split()}
    out = ROOT / "images"
    out.mkdir(exist_ok=True)
    with zipfile.ZipFile(pptx) as z:
        for name in sorted(wanted):
            im = Image.open(io.BytesIO(z.read(f"ppt/media/{name}")))
            im.thumbnail((MAX, MAX))
            if name.endswith(".jpg"):
                im.convert("RGB").save(out / name, quality=85)
            else:
                im.save(out / name, optimize=True)
            print(name, im.size)


if __name__ == "__main__":
    main(sys.argv[1])
