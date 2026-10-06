"""Apply the grouped dropdown navigation + back-to-top button to every page."""
import pathlib, re

ROOT = pathlib.Path(r"C:\Users\mahdifard\Documents\projects\shahidtaghvim")
utf8 = "utf-8"

NAV_CSS = '<link rel="stylesheet" href="assets/css/site-nav.css">'


def group(label, links):
    items = "".join(
        f'<a data-page="{page}" href="{page}.html"'
        + (f' data-hint="{hint}"' if hint else "")
        + f'>{text}'
        + (f'<span class="nav-submenu-hint">{hint}</span>' if hint else "")
        + "</a>"
        for page, text, hint in links
    )
    return ('<div class="nav-group"><button type="button" class="nav-group-toggle" '
            f'aria-haspopup="true" aria-expanded="false">{label}</button>'
            f'<div class="nav-submenu">{items}</div></div>')


G1 = group("تقویم و زمان", [
    ("calendar", "تقویم کامل", "چهار نما: ماهانه، هفتگی، سالانه، روزانه"),
    ("today", "امروز در تاریخ", "رویدادهای همین روز"),
    ("day", "یک روز خاص", "جست‌وجو در هر روز تقویم"),
])

G2 = group("کشف و دانش", [
    ("martyrs", "اشخاص و شهدا", "پرونده شهدا، آزادگان و فداکاران"),
    ("events", "رویدادها و عملیات", "آرشیو تاریخی و دفاع مقدس"),
    ("places", "مکان‌ها", "جبهه‌ها، شهرها، مزارها و یادمان‌ها"),
    ("periods", "دوره‌های تاریخی", "از صدر اسلام تا معاصر"),
    ("sources", "منابع و اسناد", "اعتبارسنجی و ردیابی منابع"),
    ("encyclopedia", "دانشنامه", "همه موجودیت‌ها در یک نگاه"),
])

G3 = ('<a class="nav-icon-link" data-page="search" href="search.html" '
      'aria-label="جست‌وجوی پیشرفته" title="جست‌وجو">'
      '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
      'stroke-width="2" stroke-linecap="round" aria-hidden="true">'
      '<circle cx="11" cy="11" r="7"></circle><line x1="16.5" y1="16.5" x2="21" y2="21"></line>'
      '</svg></a>')

G4 = group("درباره و همکاری", [
    ("about", "درباره پروژه", "چشم‌انداز، اصول و نقشه راه"),
    ("contribute", "همکاری و مشارکت", "ثبت خاطره، سند و اصلاح اطلاعات"),
    ("contact", "تماس با ما", "ارتباط، گزارش خطا و پیشنهاد"),
    ("api", "داده و API", "دسترسی برنامه‌ای به داده"),
])

NEW_NAV = ('<nav class="shared-nav" aria-label="منوی اصلی" id="sharedNav">'
           + G1 + G2 + G3 + G4 + '</nav>')

NAV_RE = re.compile(r'<nav class="shared-nav".*?</nav>', re.S)

pages = sorted(ROOT.glob("*.html"))
updated = 0

for p in pages:
    t = p.read_text(encoding=utf8)
    orig = t
    notes = []

    # 1) nav stylesheet + nav script in <head>
    head_end = t.find("</head>")
    if head_end == -1:
        print(f"  {p.name}: no </head>, skipped")
        continue
    head = t[:head_end]

    if "site-nav.css" not in head:
        # place right after the existing site.css link so it can override
        if '<link rel="stylesheet" href="assets/css/site.css">' in head:
            head = head.replace('<link rel="stylesheet" href="assets/css/site.css">',
                                '<link rel="stylesheet" href="assets/css/site.css">\n' + NAV_CSS, 1)
        else:
            head = head + NAV_CSS + "\n"
        notes.append("css")
    t = head + t[head_end:]

    # 2) replace the flat nav with the grouped nav
    m = NAV_RE.search(t)
    if m:
        t = t[:m.start()] + NEW_NAV + t[m.end():]
        notes.append("nav")

    # 3) back-to-top button element (site.js also injects one if missing)
    if 'class="to-top"' not in t:
        t = t.replace("</body>",
                      '<button class="to-top" type="button" aria-label="بازگشت به بالای صفحه">'
                      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
                      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                      '<line x1="12" y1="19" x2="12" y2="5"></line>'
                      '<polyline points="5 12 12 5 19 12"></polyline></svg></button>\n</body>', 1)
        notes.append("totop")

    if t != orig:
        p.write_text(t, encoding=utf8)
        updated += 1
        print(f"  {p.name:22s} {', '.join(notes)}")

print(f"\npages updated: {updated}/{len(pages)}")
