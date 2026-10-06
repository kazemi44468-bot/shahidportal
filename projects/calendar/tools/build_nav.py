"""Rebuild the grouped navigation.

Changes vs the first version:
  - the group label is a real link to the group's main page (clickable),
    the small chevron is a separate button that opens the submenu
  - item sizing returns to the original menu scale (12.5px / tight padding)
  - the submenu panel is styled with the header's gold line on top
"""
import pathlib, re

ROOT = pathlib.Path(r"C:\Users\mahdifard\Documents\projects\shahidtaghvim")
utf8 = "utf-8"

NAV_OPEN = '<nav class="shared-nav"'


def group(gid, label, href, links):
    items = "".join(
        f'<a data-page="{page}" href="{page}.html">{text}'
        + (f'<span class="nav-submenu-hint">{hint}</span>' if hint else "")
        + "</a>"
        for page, text, hint in links
    )
    return (
        f'<div class="nav-group" data-group="{gid}" '
        f'data-members="{",".join([href] + [x[0] for x in links])}">'
        f'<a class="nav-group-label" href="{href}.html">{label}</a>'
        f'<button type="button" class="nav-group-caret" aria-label="نمایش زیرمنوی {label}" '
        f'aria-haspopup="true" aria-expanded="false"></button>'
        f'<div class="nav-submenu">{items}</div>'
        f'</div>'
    )


G_HOME = ('<a class="nav-home-link" data-page="home" href="index.html">نخست</a>')

G_CAL = group("calendar", "تقویم و زمان", "calendar", [
    ("calendar", "تقویم کامل", "چهار نما: ماهانه، هفتگی، سالانه، روزانه"),
    ("today", "امروز در تاریخ", "رویدادهای همین روز"),
    ("day", "یک روز خاص", "جست‌وجو در هر روز تقویم"),
])

G_KNOW = group("know", "کشف و دانش", "martyrs", [
    ("martyrs", "اشخاص و شهدا", "پرونده شهدا، آزادگان و فداکاران"),
    ("events", "رویدادها و عملیات", "آرشیو تاریخی و دفاع مقدس"),
    ("places", "مکان‌ها", "جبهه‌ها، شهرها، مزارها و یادمان‌ها"),
    ("periods", "دوره‌های تاریخی", "از صدر اسلام تا معاصر"),
    ("sources", "منابع و اسناد", "اعتبارسنجی و ردیابی منابع"),
    ("encyclopedia", "دانشنامه", "همه موجودیت‌ها در یک نگاه"),
])

G_SEARCH = ('<a class="nav-icon-link" data-page="search" href="search.html" '
            'aria-label="جست‌وجوی پیشرفته" title="جست‌وجو">'
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2" stroke-linecap="round" aria-hidden="true">'
            '<circle cx="11" cy="11" r="7"></circle>'
            '<line x1="16.5" y1="16.5" x2="21" y2="21"></line></svg></a>')

G_ABOUT = group("about", "درباره و همکاری", "about", [
    ("about", "درباره پروژه", "چشم‌انداز، اصول و نقشه راه"),
    ("contribute", "همکاری و مشارکت", "ثبت خاطره، سند و اصلاح اطلاعات"),
    ("contact", "تماس با ما", "ارتباط، گزارش خطا و پیشنهاد"),
    ("api", "داده و API", "دسترسی برنامه‌ای به داده"),
])

# ترتیب: نخست | تقویم و زمان | کشف و دانش | درباره و همکاری | جست‌وجو
NEW_NAV = ('<nav class="shared-nav" aria-label="منوی اصلی" id="sharedNav">'
           + G_HOME + G_CAL + G_KNOW + G_ABOUT + G_SEARCH + '</nav>')

# match the whole nav element (may span one line)
NAV_RE = re.compile(r'<nav class="shared-nav".*?</nav>', re.S)

count = 0
for p in sorted(ROOT.glob("*.html")):
    t = p.read_text(encoding=utf8)
    m = NAV_RE.search(t)
    if not m:
        continue
    if m.group(0) == NEW_NAV:
        continue
    t = t[:m.start()] + NEW_NAV + t[m.end():]
    p.write_text(t, encoding=utf8)
    count += 1

print(f"nav rebuilt on {count} pages")

# verify
import collections
bad = 0
for p in sorted(ROOT.glob("*.html")):
    t = p.read_text(encoding=utf8)
    if NAV_OPEN not in t:
        continue
    g = len(re.findall(r'class="nav-group"', t))
    lbl = len(re.findall(r'class="nav-group-label"', t))
    caret = len(re.findall(r'class="nav-group-caret"', t))
    sub = len(re.findall(r'class="nav-submenu"', t))
    if not (g == 3 and lbl == 3 and caret == 3 and sub == 3):
        print(f"  !! {p.name}: groups={g} labels={lbl} carets={caret} submenus={sub}")
        bad += 1
print(f"pages with unexpected nav shape: {bad}")
