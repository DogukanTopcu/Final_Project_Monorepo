from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright


A0_WIDTH_MM = 841
A0_HEIGHT_MM = 1189
DEFAULT_VIEWPORT_WIDTH = 1684
DEFAULT_VIEWPORT_HEIGHT = 2382


def export_poster_pdf(html_path: Path, output_path: Path, viewport_width: int, viewport_height: int) -> None:
    html_path = html_path.resolve()
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": viewport_width, "height": viewport_height},
            device_scale_factor=1,
        )
        page.goto(html_path.as_uri(), wait_until="networkidle")
        page.wait_for_timeout(1000)
        page.emulate_media(media="print")
        page.pdf(
            path=str(output_path),
            width=f"{A0_WIDTH_MM}mm",
            height=f"{A0_HEIGHT_MM}mm",
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            print_background=True,
            prefer_css_page_size=True,
            scale=1,
            page_ranges="1",
        )
        browser.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the HTML poster as a full-size PDF.")
    parser.add_argument(
        "--html",
        type=Path,
        default=Path("docs/poster-html/Atlas.html"),
        help="Poster HTML file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/poster-html/Atlas.pdf"),
        help="Output PDF path.",
    )
    parser.add_argument(
        "--viewport-width",
        type=int,
        default=DEFAULT_VIEWPORT_WIDTH,
        help="Browser viewport width in CSS pixels for local rendering.",
    )
    parser.add_argument(
        "--viewport-height",
        type=int,
        default=DEFAULT_VIEWPORT_HEIGHT,
        help="Browser viewport height in CSS pixels for local rendering.",
    )
    args = parser.parse_args()

    export_poster_pdf(args.html, args.output, args.viewport_width, args.viewport_height)
    print(args.output)


if __name__ == "__main__":
    main()
