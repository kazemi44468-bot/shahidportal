"""Verify every page via Chrome DevTools Protocol.

Checks: console errors, uncaught exceptions, failed loads, horizontal overflow,
and that the data layer is populated and actually rendered.
Optionally saves full-page screenshots (--shots).
"""
import asyncio, base64, json, pathlib, sys, urllib.request

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(r"C:\Users\MAHDIF~1\AppData\Local\Temp\dsh-diag")
OUT.mkdir(parents=True, exist_ok=True)
PORT = 9334

args = [a for a in sys.argv[1:] if not a.startswith("--")]
SHOTS = "--shots" in sys.argv
PAGES = args or [
    "index.html", "calendar.html", "today.html", "day.html", "martyrs.html",
    "events.html", "event.html", "places.html", "periods.html", "sources.html",
    "source.html", "encyclopedia.html", "api.html", "search.html",
    "about.html", "contribute.html", "contact.html", "404.html",
]

PROBES = {
    "martyrs.html": [".martyr-card"],
    "events.html": [".event-card"],
    "search.html": [".result-card"],
    "calendar.html": [".month-grid"],
    "places.html": [".entity-card"],
    "periods.html": [".timeline-item"],
    "sources.html": [".entity-card"],
    "day.html": [".cal-day"],
    "today.html": [".upcoming-item"],
    "index.html": [".cal-day", ".discover-card"],
    "encyclopedia.html": [".entity-card"],
    "api.html": [".stats-grid li"],
    "event.html": [".detail-card"],
    "place.html": [".detail-card"],
    "period.html": [".detail-card"],
    "source.html": [".detail-card"],
}

import websockets


async def main():
    import subprocess, time
    proc = subprocess.Popen([
        CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={PORT}",
        f"--user-data-dir={OUT / 'prof'}", "--no-first-run", "--no-default-browser-check",
        "--hide-scrollbars", "--window-size=1440,1000", "about:blank",
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
        print("could not attach to chrome")
        proc.kill()
        return

    async with websockets.connect(ws_url, max_size=300 * 1024 * 1024) as ws:
        mid = 0
        events = []

        async def call(method, params=None):
            nonlocal mid
            mid += 1
            my = mid
            await ws.send(json.dumps({"id": my, "method": method, "params": params or {}}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("method"):
                    events.append(msg)
                if msg.get("id") == my:
                    if "error" in msg:
                        raise RuntimeError(f"{method}: {msg['error']}")
                    return msg.get("result", {})

        await call("Page.enable")
        await call("Runtime.enable")
        await call("Log.enable")

        async def eval_js(expr):
            r = await call("Runtime.evaluate", {"expression": expr, "returnByValue": True})
            return r.get("result", {}).get("value")

        bad = 0
        for page in PAGES:
            events.clear()
            await call("Page.navigate", {"url": "file:///" + str(REPO / page).replace("\\", "/")})
            await asyncio.sleep(2.2)

            problems = []
            for e in events:
                m = e.get("method")
                if m == "Runtime.exceptionThrown":
                    d = e["params"]["exceptionDetails"]
                    problems.append("EXCEPTION: " + str(d.get("exception", {}).get("description") or d.get("text"))[:170])
                elif m == "Runtime.consoleAPICalled" and e["params"]["type"] == "error":
                    problems.append("CONSOLE: " + " ".join(str(a.get("value", "")) for a in e["params"].get("args", []))[:170])
                elif m == "Log.entryAdded" and e["params"]["entry"].get("level") == "error":
                    problems.append("LOG: " + str(e["params"]["entry"].get("text"))[:170])

            data = json.loads(await eval_js(
                "JSON.stringify({sd:!!window.SiteData,pd:!!window.PageData,"
                "m:window.SiteData?SiteData.martyrs.length:0,"
                "e:window.SiteData?SiteData.events.length:0,"
                "s:window.PageData?PageData.searchIndex.length:0})") or "{}")
            lay = json.loads(await eval_js(
                "JSON.stringify({s:document.documentElement.scrollWidth,"
                "c:document.documentElement.clientWidth})") or "{}")
            over = lay.get("s", 0) - lay.get("c", 0)

            probes = []
            for sel in PROBES.get(page, []):
                n = await eval_js(f"document.querySelectorAll({json.dumps(sel)}).length")
                probes.append(f"{sel}={n}")
            if probes and all(p.endswith("=0") for p in probes):
                problems.append("NOTHING RENDERED: " + " ".join(probes))

            ok = not problems and over <= 8
            if not ok:
                bad += 1
            print(f"{'OK ' if ok else '!! '}{page:20s} data[m={data.get('m')} e={data.get('e')} s={data.get('s')}] "
                  f"{' '.join(probes)} overflow={over}px")
            for p in problems[:4]:
                print(f"      {p}")

            if SHOTS:
                metrics = await call("Page.getLayoutMetrics")
                css = metrics["cssContentSize"]
                w, h = int(css["width"]), min(int(css["height"]), 5000)
                await call("Emulation.setDeviceMetricsOverride",
                           {"width": w, "height": h, "deviceScaleFactor": 1, "mobile": False})
                await asyncio.sleep(0.5)
                shot = await call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": True})
                (OUT / page.replace(".html", ".png")).write_bytes(base64.b64decode(shot["data"]))

        print(f"\npages checked: {len(PAGES)}   with problems: {bad}")

    proc.kill()


asyncio.run(main())
