"""Final sync: mirror the finished calendar product into shahidportal/projects/calendar."""
import shutil, pathlib

SRC = pathlib.Path(r"C:\Users\mahdifard\Documents\projects\shahidtaghvim")
DST = pathlib.Path(r"C:\Users\mahdifard\Documents\projects\shahidportal\projects\calendar")

copied = []
for f in sorted(SRC.glob("*.html")):
    shutil.copy2(f, DST / f.name)
    copied.append(f.name)
shutil.copy2(SRC / "manifest.json", DST / "manifest.json")

for sub in ("js", "css", "images"):
    s, d = SRC / "assets" / sub, DST / "assets" / sub
    d.mkdir(parents=True, exist_ok=True)
    for f in sorted(s.glob("*")):
        shutil.copy2(f, d / f.name)

# bring the reproducible data pipeline along
td = DST / "tools"
td.mkdir(exist_ok=True)
for f in sorted((SRC / "tools").glob("*")):
    shutil.copy2(f, td / f.name)
    copied.append("tools/" + f.name)

print(f"pages synced: {sum(1 for c in copied if c.endswith('.html'))}")
print(f"tools synced: {sum(1 for c in copied if c.startswith('tools/'))}")
print(f"total items: {len(copied)}")
