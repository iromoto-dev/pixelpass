"""Builds Pixel Pass from src/: the page with its sample picture embedded, one file that runs anywhere (also offline).

    python build.py                 writes index.html (GitHub Pages, or download and open)
    python build.py --site FILE     also writes the website version to FILE: the same page plus a favicon link and
                                    links home and to the legal pages under the tool
"""
import argparse
import base64
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SITELINKS = ('<nav class="site" aria-label="iromoto"><a href="/">iromoto</a><a href="/impressum">Impressum</a>'
             '<a href="/datenschutz">Privacy (Datenschutz)</a></nav>')


def page(site):
    src = open(os.path.join(HERE, "src", "pixel-pass.html"), encoding="utf-8").read()
    sample = base64.b64encode(open(os.path.join(HERE, "src", "sample.webp"), "rb").read()).decode()
    src = src.replace("/*SAMPLE*/", "data:image/webp;base64," + sample).replace("<!--SITELINKS-->", SITELINKS if site else "")
    head, body = src.split("</style>", 1)
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<meta name="description" content="Turn a painting or a photo into pixel art in your browser: a real '
            'low-resolution grid, a limited palette and ordered dither. Everything runs locally.">\n'
            + ('<link rel="icon" href="/favicon.ico">\n' if site else '')
            + head + "</style>\n</head>\n<body>\n" + body + "\n</body>\n</html>\n")


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text.encode()) // 1024, "KB")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", help="also write the website version to this file")
    a = ap.parse_args()
    write(os.path.join(HERE, "index.html"), page(False))
    if a.site:
        write(a.site, page(True))
