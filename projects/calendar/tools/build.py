"""Rebuild the data layer with the operations merged in.

Sources:
  tools/research.json    - martyrs / events / places (recovered research)
  tools/operations.json  - 38 Iran-Iraq war operations
Outputs:
  assets/js/site-data.js - canonical data + helpers (window.SiteData)
  assets/js/page-data.js - adapter shapes for list/search pages (window.PageData)
"""
import json, pathlib, re

ROOT = pathlib.Path(r"C:\Users\mahdifard\Documents\projects\shahidtaghvim")
TOOLS = ROOT / "tools"
JS = ROOT / "assets" / "js"

research = json.loads((TOOLS / "research.json").read_text(encoding="utf-8"))
operations = json.loads((TOOLS / "operations.json").read_text(encoding="utf-8"))

FA = "۰۱۲۳۴۵۶۷۸۹"

def to_en(s):
    return re.sub(r"[۰-۹]", lambda m: str(FA.index(m.group(0))), s or "")

def sort_key(rec):
    t = to_en(rec.get("date", ""))
    m = re.fullmatch(r"(\d+)/(\d+)/(\d+)", t)
    return tuple(int(x) for x in m.groups()) if m else (9999, 99, 99)

# ---------- merge + sort events, de-duplicating by id ----------
events = research.get("events", []) + operations
seen, merged_events = set(), []
for e in sorted(events, key=sort_key):
    if e.get("id") in seen:
        continue
    seen.add(e.get("id"))
    merged_events.append({
        "id": e.get("id", ""),
        "date": e.get("date", ""),
        "type": e.get("type", "واقعه"),
        "title": e.get("title", ""),
        "desc": e.get("desc", ""),
        "tags": e.get("tags", ""),
        "city": e.get("city", ""),
        "source": e.get("source", ""),
        "status": e.get("status", "تأییدشده"),
    })

martyrs = [{
    "id": r.get("id", ""), "name": r.get("name", ""), "kind": r.get("kind", "شهید"),
    "birth": r.get("birth", ""), "martyrdom": r.get("martyrdom", ""),
    "place": r.get("martyrdomPlace", ""), "country": r.get("country", "ایران"),
    "role": r.get("role", ""), "operation": r.get("operation", ""),
    "note": r.get("notes", ""), "source": r.get("source", ""),
    "status": r.get("status", "تأییدشده"),
} for r in research.get("shohada", [])]

places = [{
    "id": r.get("id", ""), "name": r.get("name", ""), "region": r.get("region", ""),
    "country": r.get("country", ""), "type": r.get("type", ""),
    "related": r.get("related", ""), "period": r.get("period", ""),
    "note": r.get("notes", ""), "source": r.get("source", ""),
} for r in research.get("places", [])]

PERIODS = json.loads((TOOLS / "periods.json").read_text(encoding="utf-8"))
SOURCES = json.loads((TOOLS / "sources.json").read_text(encoding="utf-8"))

# ---------- emit site-data.js ----------
def js(v):
    return json.dumps(v, ensure_ascii=False)

header = """/* ============================================================
   تقویم شهدا — لایه داده
   ------------------------------------------------------------
   این فایل به‌صورت خودکار از tools/ ساخته می‌شود.
   برای تغییر داده، فایل‌های tools/*.json را ویرایش کنید و
   سپس tools/build.py را اجرا کنید.

   مطابق «سند مادر» (tarhha/calendar-tarh.html) ساختار هر رکورد
   از الگوی موجودیت‌ها پیروی می‌کند: شناسه پایدار، تاریخ، مکان،
   منبع و وضعیت اعتبار.

   وضعیت «نیازمند بررسی» یعنی تاریخ یا جزئیات آن رکورد در منابع
   گوناگون متفاوت است و باید پیش از انتشار نهایی بازبینی شود.
   ============================================================ */
(function (global) {
  'use strict';

"""

body = []
body.append("  /* ---------- رویدادها و عملیات‌های دفاع مقدس ---------- */\n")
body.append("  var events = " + js(merged_events) + ";\n\n")
body.append("  /* ---------- اشخاص: شهدا، آزادگان، فداکاران ---------- */\n")
body.append("  var martyrs = " + js(martyrs) + ";\n\n")
body.append("  /* ---------- مکان‌ها ---------- */\n")
body.append("  var places = " + js(places) + ";\n\n")
body.append("  /* ---------- دوره‌های تاریخی ---------- */\n")
body.append("  var periods = " + js(PERIODS) + ";\n\n")
body.append("  /* ---------- منابع و اسناد ---------- */\n")
body.append("  var sources = " + js(SOURCES) + ";\n\n")

body.append(r"""  /* ---------- ابزار عمومی ---------- */
  var MONTHS = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'];
  var WEEKDAYS = ['شنبه', 'یک‌شنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه'];

  function toFa(value) {
    return String(value).replace(/\d/g, function (d) { return '۰۱۲۳۴۵۶۷۸۹'[d]; });
  }

  function toJalali(gy, gm, gd) {
    var g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
    var jy = (gy <= 1600) ? 0 : 979;
    gy -= (gy <= 1600) ? 621 : 1600;
    var gy2 = (gm > 2) ? (gy + 1) : gy;
    var days = (365 * gy) + Math.floor((gy2 + 3) / 4) - Math.floor((gy2 + 99) / 100) + Math.floor((gy2 + 399) / 400) - 80 + gd + g_d_m[gm - 1];
    jy += 33 * Math.floor(days / 12053); days %= 12053;
    jy += 4 * Math.floor(days / 1461); days %= 1461;
    if (days > 365) { jy += Math.floor((days - 1) / 365); days = (days - 1) % 365; }
    var jm = (days < 186) ? 1 + Math.floor(days / 31) : 7 + Math.floor((days - 186) / 30);
    var jd = 1 + ((days < 186) ? (days % 31) : ((days - 186) % 30));
    return [jy, jm, jd];
  }

  function todayJalali() {
    var now = new Date();
    return toJalali(now.getFullYear(), now.getMonth() + 1, now.getDate());
  }

  /* پارس تاریخ شمسی «۱۳۶۰/۰۳/۳۱»؛ برای تاریخ قمری null برمی‌گرداند */
  function parseJalali(str) {
    if (!str) return null;
    var fa = '۰۱۲۳۴۵۶۷۸۹';
    var en = String(str).replace(/[۰-۹]/g, function (ch) { return fa.indexOf(ch); });
    if (!/^\d+\/\d+\/\d+$/.test(en)) return null;
    var p = en.split('/').map(function (x) { return parseInt(x, 10); });
    if (p.length < 3 || isNaN(p[0])) return null;
    return { y: p[0], m: p[1], d: p[2] };
  }

  function formatJalali(str) {
    var p = parseJalali(str);
    if (!p) return str || '—';
    return toFa(p.d) + ' ' + MONTHS[p.m - 1] + ' ' + toFa(p.y);
  }

  function qs(name) {
    var m = new RegExp('[?&]' + name + '=([^&#]*)').exec(global.location.search);
    return m ? decodeURIComponent(m[1].replace(/\+/g, ' ')) : '';
  }

  global.SiteData = {
    events: events,
    martyrs: martyrs,
    places: places,
    periods: periods,
    sources: sources,
    MONTHS: MONTHS,
    WEEKDAYS: WEEKDAYS,
    toFa: toFa,
    toJalali: toJalali,
    todayJalali: todayJalali,
    parseJalali: parseJalali,
    formatJalali: formatJalali,
    qs: qs,
    find: function (list, id) {
      for (var i = 0; i < list.length; i++) if (list[i].id === id) return list[i];
      return null;
    },
    eventsOn: function (m, d) {
      return events.filter(function (e) {
        var p = parseJalali(e.date);
        return p && p.m === m && p.d === d;
      });
    },
    /* جست‌وجوی سراسری روی همه موجودیت‌ها */
    searchAll: function (q) {
      q = (q || '').trim();
      if (!q) return [];
      var out = [];
      events.forEach(function (e) {
        if ((e.title + ' ' + e.desc + ' ' + e.tags + ' ' + e.city).indexOf(q) !== -1)
          out.push({ kind: 'رویداد', title: e.title, desc: e.city, href: 'event.html?id=' + e.id });
      });
      martyrs.forEach(function (s) {
        if ((s.name + ' ' + s.role + ' ' + s.place + ' ' + s.note).indexOf(q) !== -1)
          out.push({ kind: 'شخص', title: s.name, desc: s.role, href: 'martyrs.html' });
      });
      places.forEach(function (p) {
        if ((p.name + ' ' + p.region + ' ' + p.related).indexOf(q) !== -1)
          out.push({ kind: 'مکان', title: p.name, desc: p.region, href: 'place.html?id=' + p.id });
      });
      periods.forEach(function (p) {
        if ((p.title + ' ' + p.note).indexOf(q) !== -1)
          out.push({ kind: 'دوره', title: p.title, desc: p.from + ' — ' + p.to, href: 'period.html?id=' + p.id });
      });
      sources.forEach(function (s) {
        if ((s.title + ' ' + s.org + ' ' + s.note).indexOf(q) !== -1)
          out.push({ kind: 'منبع', title: s.title, desc: s.kind, href: 'source.html?id=' + s.id });
      });
      return out;
    }
  };
})(window);
""")

(JS / "site-data.js").write_text(header + "".join(body), encoding="utf-8")
print(f"site-data.js: events={len(merged_events)} martyrs={len(martyrs)} "
      f"places={len(places)} periods={len(PERIODS)} sources={len(SOURCES)}")

# ---------- emit page-data.js ----------
def parse_date(s):
    t = to_en(s or "").strip()
    if not re.fullmatch(r"\d+/\d+/\d+", t):
        return None
    y, m, d = (int(x) for x in t.split("/"))
    return (y, m, d)

PROVINCES = ["تهران", "خوزستان", "اصفهان", "فارس", "خراسان رضوی", "آذربایجان شرقی",
             "آذربایجان غربی", "کرمانشاه", "ایلام", "کردستان", "گیلان", "مازندران",
             "یزد", "کرمان", "قم", "البرز", "همدان", "لرستان", "گلستان", "مرکزی",
             "هرمزگان", "بوشهر", "سمنان", "قزوین", "زنجان", "اردبیل", "خراسان جنوبی",
             "خراسان شمالی", "سیستان و بلوچستان", "چهارمحال و بختیاری",
             "کهگیلویه و بویراحمد", "عربستان سعودی", "عراق", "سوریه", "لبنان", "خلیج فارس"]

def province_of(rec):
    hay = " ".join(str(rec.get(k, "")) for k in ("place", "city", "region", "related"))
    for p in PROVINCES:
        if p in hay:
            return p
    return "تهران"

def period_of(rec):
    ymd = parse_date(rec.get("martyrdom") or rec.get("date", ""))
    if not ymd:
        return "تاریخ اسلام"
    y = ymd[0]
    if y < 1300:
        return "تاریخ اسلام"
    if y <= 1357:
        return "پیش از انقلاب"
    if y <= 1358:
        return "انقلاب اسلامی"
    if y <= 1367:
        return "دفاع مقدس"
    if y <= 1389:
        return "دوره پس از جنگ"
    if y <= 1397:
        return "مدافعان حرم"
    return "مدافعان سلامت"

TYPE_MAP = {"شهادت": "martyrdom", "عملیات": "operation", "جنگ": "war",
            "انقلاب": "revolution", "واقعه": "event", "مناسبت": "ceremony"}
TYPE_LABELS = {"martyrdom": "شهادت", "operation": "عملیات", "war": "جنگ",
               "revolution": "انقلاب", "event": "واقعه", "ceremony": "یادمانی"}

pd_martyrs = []
for i, r in enumerate(martyrs, start=1):
    ym, yb = parse_date(r["martyrdom"]), parse_date(r["birth"])
    pd_martyrs.append({
        "id": i, "sid": r["id"], "name": r["name"], "role": r["role"],
        "birth": yb[0] if yb else None, "martyrdom": ym[0] if ym else None,
        "birthDate": r["birth"], "martyrDate": r["martyrdom"],
        "province": province_of(r), "city": r["place"],
        "operation": r["operation"], "period": period_of(r),
        "age": (ym[0] - yb[0]) if (ym and yb) else None,
        "verified": r["status"] == "تأییدشده", "note": r["note"], "source": r["source"],
        "tags": [t for t in [r["operation"], r["place"]] if t],
    })

pd_events = []
for i, r in enumerate(merged_events, start=1):
    ymd = parse_date(r["date"])
    pd_events.append({
        "id": i, "eid": r["id"], "type": TYPE_MAP.get(r["type"], "event"),
        "rawType": r["type"], "title": r["title"], "desc": r["desc"],
        "dateText": r["date"],
        "day": ymd[2] if ymd else 0, "month": ymd[1] if ymd else 0,
        "year": ymd[0] if ymd else 0,
        "province": province_of(r), "city": r["city"], "period": period_of(r),
        "tags": r["tags"].split(), "source": r["source"],
        "verified": r["status"] == "تأییدشده",
    })

search_index = []
for r in pd_martyrs:
    search_index.append({"id": "m" + str(r["id"]), "type": "martyr", "title": r["name"],
                         "desc": (r["role"] + (" — " + r["note"] if r["note"] else "")).strip(" —"),
                         "period": r["period"], "province": r["province"],
                         "year": r["martyrdom"] or 0, "age": r["age"],
                         "tags": r["tags"], "url": "martyrs.html"})
for r in pd_events:
    search_index.append({"id": "e" + str(r["id"]), "type": "event", "title": r["title"],
                         "desc": r["desc"], "period": r["period"], "province": r["province"],
                         "year": r["year"], "tags": r["tags"],
                         "url": "event.html?id=" + r["eid"]})
for r in places:
    search_index.append({"id": r["id"], "type": "place", "title": r["name"],
                         "desc": r["note"] or (r["type"] + " — " + r["related"]),
                         "period": r["period"], "province": province_of(r), "year": 0,
                         "tags": [r["type"]], "url": "place.html?id=" + r["id"]})
for r in PERIODS:
    search_index.append({"id": r["id"], "type": "period", "title": r["title"],
                         "desc": r["note"], "period": r["title"], "province": "",
                         "year": 0, "tags": [], "url": "period.html?id=" + r["id"]})
for r in SOURCES:
    search_index.append({"id": r["id"], "type": "source", "title": r["title"],
                         "desc": r["note"], "period": "", "province": "", "year": 0,
                         "tags": [r["kind"]], "url": "source.html?id=" + r["id"]})

page_out = {
    "martyrs": pd_martyrs,
    "events": pd_events,
    "searchIndex": search_index,
    "periodMap": {v: v for v in sorted({r["period"] for r in pd_martyrs} | {r["period"] for r in pd_events})},
    "provMap": {v: v for v in sorted({r["province"] for r in pd_martyrs} | {r["province"] for r in pd_events})},
    "opMap": {v: v for v in sorted({r["operation"] for r in pd_martyrs if r["operation"]})},
    "typeLabels": TYPE_LABELS,
    "counts": {"martyrs": len(pd_martyrs), "events": len(pd_events), "places": len(places),
               "periods": len(PERIODS), "sources": len(SOURCES)},
}

adapter = """/* ============================================================
   تقویم شهدا — آداپتور داده صفحات
   ------------------------------------------------------------
   این فایل به‌صورت خودکار ساخته می‌شود. داده واقعی site-data.js
   را به همان شکلی درمی‌آورد که صفحات فهرست/جست‌وجو/تقویم از قبل
   انتظار دارند، تا منطق نمایش صفحات بازنویسی نشود.

   برای تغییر داده tools/*.json را ویرایش و tools/build.py را اجرا کنید.
   ============================================================ */
(function (global) {
  'use strict';
  global.PageData = """ + json.dumps(page_out, ensure_ascii=False, indent=1) + """;
})(window);
"""
(JS / "page-data.js").write_text(adapter, encoding="utf-8")
print(f"page-data.js: searchIndex={len(search_index)}")
print(f"  periods seen: {list(page_out['periodMap'])}")
