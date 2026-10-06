"""Functional test for the grouped nav + back-to-top button via CDP.

Checks per viewport width:
  - nav does not overflow its container
  - group toggles open/close and keep aria-expanded in sync
  - the active page is highlighted (including inside a submenu)
  - the back-to-top button appears after scrolling and returns to top
"""
import asyncio, json, pathlib, subprocess, sys, time, urllib.request

# Persian labels are printed below; force UTF-8 so the Windows console
# code page cannot crash the run mid-test.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
REPO = pathlib.Path(__file__).resolve().parent.parent
PORT = 9336

import websockets

WIDTHS = [1440, 1200, 1024, 960, 860, 768, 720, 600, 390]


async def main():
    proc = subprocess.Popen([
        CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={PORT}",
        f"--user-data-dir={REPO / 'tools' / '.chrome'}", "--no-first-run",
        "--no-default-browser-check", "--hide-scrollbars", "about:blank",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    ws_url = None
    for _ in range(60):
        try:
            tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list").read())
            cand = [t for t in tabs if t.get("type") == "page"]
            if cand:
                ws_url = cand[0]["webSocketDebuggerUrl"]
                break
        except Exception:
            pass
        time.sleep(0.25)
    if not ws_url:
        print("could not attach")
        proc.kill()
        return

    async with websockets.connect(ws_url, max_size=100 * 1024 * 1024) as ws:
        mid = 0

        async def call(method, params=None):
            nonlocal mid
            mid += 1
            my = mid
            await ws.send(json.dumps({"id": my, "method": method, "params": params or {}}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == my:
                    if "error" in msg:
                        raise RuntimeError(f"{method}: {msg['error']}")
                    return msg.get("result", {})

        await call("Page.enable")
        await call("Runtime.enable")

        async def js(expr):
            r = await call("Runtime.evaluate", {"expression": expr, "returnByValue": True})
            return r.get("result", {}).get("value")

        url = "file:///" + str(REPO / "martyrs.html").replace("\\", "/")

        print("=== nav overflow across widths (martyrs.html) ===")
        bad = 0
        for w in WIDTHS:
            await call("Emulation.setDeviceMetricsOverride",
                       {"width": w, "height": 900, "deviceScaleFactor": 1, "mobile": False})
            await call("Page.navigate", {"url": url})
            await asyncio.sleep(1.4)
            res = json.loads(await js("""
              (function(){
                var nav = document.getElementById('sharedNav');
                var hdr = document.querySelector('.shared-header-inner');
                var doc = document.documentElement;
                var cs = nav ? getComputedStyle(nav) : null;
                return JSON.stringify({
                  docOverflow: doc.scrollWidth - doc.clientWidth,
                  navVisible: cs ? cs.display !== 'none' : false,
                  navRight: nav ? Math.round(nav.getBoundingClientRect().right) : 0,
                  hdrRight: hdr ? Math.round(hdr.getBoundingClientRect().right) : 0,
                  hamburger: getComputedStyle(document.querySelector('.shared-menu-toggle')).display
                });
              })()
            """) or "{}")
            overflow = res.get("docOverflow", 0)
            flag = ""
            if overflow > 8:
                flag = "  <-- OVERFLOW"
                bad += 1
            print(f"  {w:>5}px  docOverflow={overflow:>4}px  navVisible={res.get('navVisible')}  "
                  f"hamburger={res.get('hamburger')}{flag}")

        print("\n=== dropdown behaviour (1440px) ===")
        await call("Emulation.setDeviceMetricsOverride",
                   {"width": 1440, "height": 900, "deviceScaleFactor": 1, "mobile": False})
        await call("Page.navigate", {"url": url})
        await asyncio.sleep(1.5)

        before = await js("document.querySelector('.nav-group-toggle').getAttribute('aria-expanded')")
        await js("document.querySelector('.nav-group-toggle').click()")
        await asyncio.sleep(0.4)
        after = await js("document.querySelector('.nav-group-toggle').getAttribute('aria-expanded')")
        open_cls = await js("document.querySelector('.nav-submenu').classList.contains('is-open')")
        print(f"  aria-expanded before={before} after click={after}  submenu is-open={open_cls}")

        await js("document.body.click()")
        await asyncio.sleep(0.3)
        closed = await js("document.querySelector('.nav-group-toggle').getAttribute('aria-expanded')")
        print(f"  after outside click aria-expanded={closed}")

        # active page highlight should be inside the "کشف و دانش" group
        active = await js(
            "JSON.stringify(Array.from(document.querySelectorAll('.shared-nav a.is-active'))"
            ".map(a=>a.getAttribute('href')))")
        group_active = await js(
            "JSON.stringify(Array.from(document.querySelectorAll('.nav-group.is-active .nav-group-toggle'))"
            ".map(b=>b.textContent))")
        print(f"  active links: {active}")
        print(f"  active group: {group_active}")

        print("\n=== back-to-top button ===")
        hidden_before = await js("document.querySelector('.to-top').classList.contains('is-visible')")
        await js("window.scrollTo(0, 1200)")
        await asyncio.sleep(0.6)
        shown = await js("document.querySelector('.to-top').classList.contains('is-visible')")
        print(f"  visible at top={hidden_before}  visible after scroll={shown}")
        await js("document.querySelector('.to-top').click()")
        await asyncio.sleep(1.2)
        y = await js("Math.round(window.scrollY)")
        print(f"  scrollY after clicking to-top = {y}")
        hidden_after = await js("document.querySelector('.to-top').classList.contains('is-visible')")
        print(f"  visible after returning to top={hidden_after}")

        print("\n=== mobile accordion (390px) ===")
        await call("Emulation.setDeviceMetricsOverride",
                   {"width": 390, "height": 800, "deviceScaleFactor": 1, "mobile": True})
        await call("Page.navigate", {"url": url})
        await asyncio.sleep(1.5)
        await js("document.querySelector('.shared-menu-toggle').click()")
        await asyncio.sleep(0.3)
        nav_open = await js("document.querySelector('.shared-nav').classList.contains('is-open')")
        await js("document.querySelector('.nav-group-toggle').click()")
        await asyncio.sleep(0.3)
        sub_open = await js("document.querySelector('.nav-submenu').classList.contains('is-open')")
        sub_visible = await js(
            "getComputedStyle(document.querySelector('.nav-submenu')).display")
        print(f"  nav is-open={nav_open}  first submenu is-open={sub_open}  display={sub_visible}")
        doc_over = await js("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        print(f"  doc overflow with menu open = {doc_over}px")

        print(f"\nwidths with overflow: {bad}/{len(WIDTHS)}")

    proc.kill()


asyncio.run(main())
