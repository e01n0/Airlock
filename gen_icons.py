#!/usr/bin/env python3
"""Rasterise the Airlock app icon from icon-source.svg.

The icon is authored once as SVG (the chamber: tick collar, pressure arc,
iris) and rendered to the PNG sizes a PWA and iOS need. Headless Chromium
does the rasterising, because it is the same renderer that draws the icon's
big brother in the app itself — no second vector stack to keep in step.

    pip install playwright && playwright install chromium
    python3 gen_icons.py

Writes icon-192.png, icon-512.png and apple-touch-icon.png next to the source.
"""
import os, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SIZES = [("icon-512.png", 512), ("icon-192.png", 192), ("apple-touch-icon.png", 180)]

def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("pip install playwright && playwright install chromium")
    svg = (ROOT / "icon-source.svg").read_text(encoding="utf-8")
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for name, size in SIZES:
            page = browser.new_page(viewport={"width": size, "height": size},
                                    device_scale_factor=1)
            page.set_content(
                f'<body style="margin:0;background:#05080b">'
                f'<div style="width:{size}px;height:{size}px">{svg}</div></body>')
            page.locator("svg").first.evaluate(
                "(el, s) => { el.setAttribute('width', s); el.setAttribute('height', s); }", size)
            page.screenshot(path=str(ROOT / name), omit_background=False)
            page.close()
            print(f"  {name}  {size}x{size}")
        browser.close()

if __name__ == "__main__":
    main()
