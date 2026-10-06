/* ============================================================
   تقویم شهدا — رفتار پوسته
   ------------------------------------------------------------
   ۱) تشخیص صفحه فعال و نشانه‌گذاری لینک آن (حتی داخل زیرمنو)
   ۲) زیرمنوهای منو: هاور در دسکتاپ، کلیک و آکاردئون در موبایل
   ۳) دکمه شناور «بازگشت به بالا» با نمایش بر پایه اسکرول

   دسترس‌پذیری: aria-expanded و aria-haspopup روی دکمه گروه‌ها،
   بستن با Escape، بستن با کلیک بیرون، و پیمایش با کیبورد.
   ============================================================ */
(function () {
  'use strict';

  function init() {
    var path = location.pathname.split('/').pop() || 'index.html';
    var key = path === 'index.html' ? 'home' : (path.replace('.html', '') || 'home');

    /* ---------- ۱) صفحه فعال ---------- */
    var links = document.querySelectorAll('.shared-nav a[data-page]');
    Array.prototype.forEach.call(links, function (a) {
      var on = a.dataset.page === key;
      a.classList.toggle('is-active', on);
      if (on) {
        a.setAttribute('aria-current', 'page');
        // گروهِ نگه‌دارنده این لینک را هم فعال کن
        var group = a.closest('.nav-group');
        if (group) group.classList.add('is-active');
      }
    });

    /* ---------- ۲) منوی موبایل ---------- */
    var toggle = document.querySelector('.shared-menu-toggle');
    var nav = document.querySelector('.shared-nav');
    var isMobile = function () { return window.matchMedia('(max-width: 720px)').matches; };

    if (toggle && nav) {
      toggle.addEventListener('click', function () {
        var open = nav.classList.toggle('is-open');
        toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        toggle.textContent = open ? '×' : '☰';
        if (!open) closeAllGroups();
      });
    }

    /* ---------- ۳) گروه‌های منو ---------- */
    var groups = Array.prototype.slice.call(document.querySelectorAll('.shared-nav .nav-group'));

    function closeAllGroups(except) {
      groups.forEach(function (g) {
        if (g === except) return;
        var b = g.querySelector('.nav-group-toggle');
        var m = g.querySelector('.nav-submenu');
        if (b) b.setAttribute('aria-expanded', 'false');
        if (m) m.classList.remove('is-open');
      });
    }

    groups.forEach(function (g) {
      var btn = g.querySelector('.nav-group-toggle');
      var menu = g.querySelector('.nav-submenu');
      if (!btn || !menu) return;

      btn.setAttribute('aria-haspopup', 'true');
      btn.setAttribute('aria-expanded', 'false');

      btn.addEventListener('click', function (e) {
        e.preventDefault();
        var willOpen = !menu.classList.contains('is-open');
        closeAllGroups(g);
        menu.classList.toggle('is-open', willOpen);
        btn.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
      });

      // در دسکتاپ هاور خودش باز می‌کند؛ aria را هم همگام نگه دار
      g.addEventListener('mouseenter', function () {
        if (!isMobile()) btn.setAttribute('aria-expanded', 'true');
      });
      g.addEventListener('mouseleave', function () {
        if (!isMobile()) {
          btn.setAttribute('aria-expanded', 'false');
          menu.classList.remove('is-open');
        }
      });
    });

    document.addEventListener('click', function (e) {
      if (!e.target.closest('.shared-nav')) closeAllGroups();
    });

    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      closeAllGroups();
      if (nav && nav.classList.contains('is-open')) {
        nav.classList.remove('is-open');
        if (toggle) {
          toggle.setAttribute('aria-expanded', 'false');
          toggle.textContent = '☰';
          toggle.focus();
        }
      }
    });

    /* ---------- ۴) دکمه بازگشت به بالا ---------- */
    var toTop = document.querySelector('.to-top');
    if (!toTop) {
      toTop = document.createElement('button');
      toTop.className = 'to-top';
      toTop.type = 'button';
      toTop.setAttribute('aria-label', 'بازگشت به بالای صفحه');
      toTop.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
        'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
        '<line x1="12" y1="19" x2="12" y2="5"></line>' +
        '<polyline points="5 12 12 5 19 12"></polyline></svg>';
      document.body.appendChild(toTop);
    }

    var THRESHOLD = 320;
    var ticking = false;

    function syncToTop() {
      toTop.classList.toggle('is-visible', window.scrollY > THRESHOLD);
      ticking = false;
    }

    window.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(syncToTop);
    }, { passive: true });

    toTop.addEventListener('click', function () {
      var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' });
    });

    syncToTop();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
