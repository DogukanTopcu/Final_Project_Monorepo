from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright


def export_poster_pdf(html_path: Path, output_path: Path, width: int, height: int) -> None:
    html_path = html_path.resolve()
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": width, "height": height},
            device_scale_factor=1,
        )
        page.goto(html_path.as_uri(), wait_until="networkidle")
        page.wait_for_timeout(1000)
        page.emulate_media(media="screen")
        page.pdf(
            path=str(output_path),
            width=f"{width}px",
            height=f"{height}px",
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            print_background=True,
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
    parser.add_argument("--width", type=int, default=1684, help="Poster width in CSS pixels.")
    parser.add_argument("--height", type=int, default=2382, help="Poster height in CSS pixels.")
    args = parser.parse_args()

    export_poster_pdf(args.html, args.output, args.width, args.height)
    print(args.output)


if __name__ == "__main__":
    main()
