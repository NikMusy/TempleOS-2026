"""Собирает THEME.ISO (ISO9660 + Joliet) из папки theme для передачи в VM."""
import io
import sys
from pathlib import Path
import pycdlib

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "theme"
OUT = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "THEME.ISO")
SKIP = {"wallpaper_preview.png"}

iso = pycdlib.PyCdlib()
iso.new(joliet=3, vol_ident="TEMPLE2026")
names = {}


def short(rel, prefix):
    # ISO9660 видит короткие имена, ZealOS читает длинные из Joliet
    return names.setdefault(rel, f"{prefix}{len(names):06d}")


for p in sorted(SRC.rglob("*")):
    if p.name in SKIP:
        continue
    parts = p.relative_to(SRC).parts
    dirs = "/".join(short("/".join(parts[:i + 1]), "D") for i in range(len(parts) - 1))
    base = "/" + (dirs + "/" if dirs else "")
    joliet = "/" + "/".join(parts)
    if p.is_dir():
        iso.add_directory(base + short("/".join(parts), "D"), joliet_path=joliet)
    else:
        data = p.read_bytes()
        iso.add_fp(io.BytesIO(data), len(data), base + short("/".join(parts), "F") + ".;1", joliet_path=joliet)
iso.write(str(OUT))
iso.close()
print("ok", OUT, OUT.stat().st_size)
