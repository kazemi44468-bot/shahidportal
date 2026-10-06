/* ============================================================
   تقویم شهدا — رفتار پوسته
   ------------------------------------------------------------
   ۱) تشخیص صفحه فعال و نشانه‌گذاری لینک آن (حتی داخل زیرمنو)
   ۲) گروه‌های منو: کلیک روی کل گروه زیرمنو را باز/بسته می‌کند؛
      در دسکتاپ هاور هم باز می‌کند. در موبایل آکاردئون می‌شود.
   ۳) دکمه شناور «بازگشت به بالا» با نمایش بر پایه اسکرول

   دسترس‌پذیری: aria-expanded و aria-haspopup روی فلش گروه،
   بستن با Escape، بستن با کلیک بیرون، پیمایش با کیبورد.
   ============================================================ */
(function () {
  'use strict';

  function init() {
    var path = location.pathname.split('/').pop() || 'index.html';
    var key = path === 'index.html' ? 'home' : (path.replace('.html', '') || 'home');

    /* ---------- ۱) صفحه فعال ---------- */
    Array.prototype.forEach.call(
      document.querySelectorAll('.shared-nav a[data-page]'),
      function (a) {
        var on = a.dataset.page === key;
        a.classList.toggle('is-active', on);
        if (on) {
          a.setAttribute('aria-current', 'page');
          var g = a.closest('.nav-group');
          if (g) g.classList.add('is-active');
        }
      }
    );

    /* گروهی که صفحه فعال در آن است را برجسته کن */
    Array.prototype.forEach.call(
      document.querySelectorAll('.shared-nav .nav-group[data-members]'),
      function (g) {
        var members = (g.dataset.members || '').split(',');
        if (members.indexOf(key) !== -1) g.classList.add('is-active');
      }
    );

    /* ---------- ۲) منوی موبایل ---------- */
    var toggle = document.querySelector('.shared-menu-toggle');
    var nav = document.querySelector('.shared-nav');
    var isMobile = function () { return window.matchMedia('(max-width: 900px)').matches; };

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
        var m = g.querySelector('.nav-submenu');
        var c = g.querySelector('.nav-group-caret');
        if (m) m.classList.remove('is-open');
        if (c) c.setAttribute('aria-expanded', 'false');
      });
    }

    groups.forEach(function (g) {
      var caret = g.querySelector('.nav-group-caret');
      var label = g.querySelector('.nav-group-label');
      var menu = g.querySelector('.nav-submenu');
      if (!caret || !menu) return;

      function setOpen(open) {
        menu.classList.toggle('is-open', open);
        caret.setAttribute('aria-expanded', open ? 'true' : 'false');
      }
      function isOpen() { return menu.classList.contains('is-open'); }

      // کلیک روی کل گروه (برچسب یا فلش) زیرمنو را باز/بسته می‌کند،
      // چون کاربر انتظار دارد کلیک روی منو کار کند.
      g.addEventListener('click', function (e) {
        e.preventDefault();
        var willOpen = !isOpen();
        closeAllGroups(g);
        setOpen(willOpen);
      });

      // فلش با کیبورد هم باز/بسته شود
      caret.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          var willOpen = !isOpen();
          closeAllGroups(g);
          setOpen(willOpen);
        }
      });

      // دسکتاپ: هاور باز می‌کند
      g.addEventListener('mouseenter', function () {
        if (!isMobile()) { closeAllGroups(g); setOpen(true); }
      });
      g.addEventListener('mouseleave', function () {
        if (!isMobile()) setOpen(false);
      });

      if (label) {
        label.addEventListener('keydown', function (e) {
          if (e.key === 'Escape') { setOpen(false); caret.focus(); }
        });
      }
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
