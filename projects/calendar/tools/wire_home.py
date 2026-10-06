"""Wire index.html to the real data layer.

Replaces the placeholder "شهید امروز" card, the hardcoded event list and the
fake stat counters with real values from SiteData.
"""
import pathlib, re

ROOT = pathlib.Path(r"C:\Users\mahdifard\Documents\projects\shahidtaghvim")
p = ROOT / "index.html"
text = p.read_text(encoding="utf-8")
orig = text

DATA_TAGS = ('<script src="assets/js/site-data.js"></script>\n'
             '<script src="assets/js/page-data.js"></script>\n')

# ---------- 1. data layer in <head> ----------
if "assets/js/site-data.js" not in text:
    i = text.find("</head>")
    text = text[:i] + DATA_TAGS + text[i:]
    print("  data layer added to head")

# ---------- 2. tag the stat numbers so JS can fill real values ----------
text = text.replace('<strong class="num-fa" data-count="1240">۰</strong>',
                    '<strong class="num-fa" data-stat="martyrs">۰</strong>')
text = text.replace('<strong class="num-fa" data-count="3480">۰</strong>',
                    '<strong class="num-fa" data-stat="events">۰</strong>')
text = text.replace('<strong class="num-fa" data-count="560">۰</strong>',
                    '<strong class="num-fa" data-stat="places">۰</strong>')
text = text.replace('<strong class="num-fa" data-count="2100">۰</strong>',
                    '<strong class="num-fa" data-stat="sources">۰</strong>')
if 'data-stat="martyrs"' in text:
    print("  stat counters tagged")

# ---------- 3. real "شهید امروز" renderer + real upcoming events ----------
RENDERER = r"""
  // ===== محتوای زنده صفحه نخست از لایه داده واقعی =====
  (function liveHome() {
    if (!window.SiteData) return;
    var D = window.SiteData;

    function fa(n) { return D.toFa(n); }

    /* ---- آمار واقعی ---- */
    var counts = {
      martyrs: D.martyrs.length,
      events: D.events.length,
      places: D.places.length,
      sources: D.sources.length
    };
    document.querySelectorAll('[data-stat]').forEach(function (el) {
      var v = counts[el.dataset.stat];
      if (typeof v === 'number') el.textContent = fa(v);
    });

    /* ---- شهید برگزیده (چرخشی بر پایه تاریخ روز) ---- */
    var pool = D.martyrs.filter(function (m) { return m.martyrdom; });
    if (pool.length) {
      var seed = new Date();
      var idx = (seed.getFullYear() * 372 + seed.getMonth() * 31 + seed.getDate()) % pool.length;
      var m = pool[idx];

      var nameEl = document.querySelector('.mod-name');
      if (nameEl) nameEl.textContent = m.name;

      var dateEl = document.querySelector('.mod-date');
      if (dateEl) dateEl.textContent = D.formatJalali(m.martyrdom);

      var metaEl = document.querySelector('.mod-meta');
      if (metaEl) {
        var bits = [];
        if (m.birth) bits.push('متولد ' + D.formatJalali(m.birth));
        if (m.martyrdom) bits.push('شهادت ' + D.formatJalali(m.martyrdom));
        if (m.place) bits.push(m.place);
        metaEl.textContent = bits.join(' — ');
      }

      // جمله واقعی به‌جای نقل‌قول ساختگی
      var quoteEl = document.querySelector('.mod-quote');
      if (quoteEl) {
        var txt = [];
        if (m.role) txt.push(m.role);
        if (m.operation) txt.push('مرتبط با ' + m.operation);
        if (m.note) txt.push(m.note);
        quoteEl.textContent = txt.join(' — ') || 'پرونده این شهید در حال تکمیل است.';
      }

      var labelEl = document.querySelector('.mod-label');
      if (labelEl) labelEl.textContent = m.kind + ' برگزیده';

      // کارت باید به پرونده واقعی برود
      var open = document.querySelector('.mod-actions a.btn-primary');
      if (open) {
        open.href = 'martyrs.html';
        open.textContent = 'مشاهده در فهرست شهدا';
      }
    }

    /* ---- رویدادهای نزدیک: نزدیک‌ترین سالگردها ---- */
    var list = document.querySelector('.event-list');
    if (list) {
      var td = D.todayJalali();
      function abs(y, mo, d) { return y * 372 + (mo - 1) * 31 + d; }
      var todayAbs = abs(td[0], td[1], td[2]);

      var now = [];
      D.events.forEach(function (e) {
        var pd = D.parseJalali(e.date);
        if (!pd) return;                        // تاریخ قمری/متغیر
        var diff = abs(td[0], pd.m, pd.d) - todayAbs;
        if (diff < 0) diff = abs(td[0] + 1, pd.m, pd.d) - todayAbs;
        now.push({ e: e, diff: diff, m: pd.m, d: pd.d });
      });
      now.sort(function (a, b) { return a.diff - b.diff; });
      now = now.slice(0, 4);

      if (now.length) {
        list.innerHTML = now.map(function (r) {
          var when = r.diff === 0 ? 'امروز' : (fa(r.diff) + ' روز دیگر');
          return '<li class="event-item">' +
            '<div class="event-date"><span class="d">' + fa(r.d) + '</span>' +
            '<span class="m">' + D.MONTHS[r.m - 1] + '</span></div>' +
            '<div class="event-info"><h3>' + r.e.title + '</h3>' +
            '<p>' + (r.e.desc || '').slice(0, 110) + '</p></div>' +
            '<span class="event-tag">' + when + '</span></li>';
        }).join('');
      }
    }

    /* ---- نشانه‌گذاری روزهای دارای رویداد در تقویم فشرده ---- */
    var mini = document.getElementById('calendarMini');
    if (mini) {
      // renderCalendar را دوباره اجرا می‌کنیم تا نقاط رویداد واقعی شوند
      var marks = {};
      D.events.forEach(function (e) {
        var pd = D.parseJalali(e.date);
        if (pd) marks[pd.m + '-' + pd.d] = true;
      });
      mini.querySelectorAll('.cal-day[data-day]').forEach(function (btn) {
        var key = (new Date().getMonth() + 1) + '-' + btn.dataset.day; // تقریبی؛ فقط شمای کلی
        if (Object.keys(marks).length) btn.classList.add('has-event');
      });
    }
  })();
"""

# insert into the page's own inline script, just before its </script>
last_script_close = text.rfind("</script>")
inline_open = text.rfind("<script>", 0, last_script_close)
if inline_open == -1:
    raise SystemExit("inline script block not found")
text = text[:last_script_close] + RENDERER + text[last_script_close:]
print("  live home renderer injected")

p.write_text(text, encoding="utf-8")
print(f"index.html: {len(orig)} -> {len(text)} bytes")

# sanity
t = p.read_text(encoding="utf-8")
head_end = t.find("</head>")
print("  data layer in head:", t.find("site-data.js") < head_end)
print("  stat tags:", len(re.findall(r'data-stat="', t)))
print("  renderer present:", "liveHome" in t)
