"""Builds Pixel Pass from src/: the page with its sample picture embedded, one file that runs anywhere (also offline).

    python build.py                 writes index.html (GitHub Pages, or download and open)
    python build.py --site FILE     also writes the website version to FILE: the same page plus a favicon link and
                                    links home and to the legal pages under the tool
The pixel engine runs in a worker made from the page's own script (see "engine" in the page), except on the website.
"""
import argparse
import base64
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SITELINKS = ('<nav class="site" aria-label="iromoto"><a href="/">iromoto</a><a href="/impressum">Impressum</a>'
             '<a href="/datenschutz">Privacy (Datenschutz)</a></nav>')


def webp_size(data):
    """Width and height of a WebP file, from its header (lossy, lossless or extended)."""
    assert data[:4] == b"RIFF" and data[8:12] == b"WEBP", "not a WebP"
    kind = data[12:16]
    if kind == b"VP8 ":
        return int.from_bytes(data[26:28], "little") & 0x3FFF, int.from_bytes(data[28:30], "little") & 0x3FFF
    if kind == b"VP8L":
        bits = int.from_bytes(data[21:25], "little")
        return (bits & 0x3FFF) + 1, (bits >> 14 & 0x3FFF) + 1
    if kind == b"VP8X":
        return int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1
    raise ValueError("unknown WebP kind %r" % kind)


def page(site):
    src = open(os.path.join(HERE, "src", "pixel-pass.html"), encoding="utf-8").read()
    raw = open(os.path.join(HERE, "src", "sample.webp"), "rb").read()
    sample = base64.b64encode(raw).decode()
    w, h = webp_size(raw)
    src = src.replace("/*SAMPLE*/", "data:image/webp;base64," + sample).replace("<!--SITELINKS-->", SITELINKS if site else "")
    # the sample's shape from the first moment: the page's width follows it, so a guess would jump on load
    src = src.replace("/*SAMPLE-RATIO*/2", "%.4f" % (w / h))
    head, body = src.split("</style>", 1)
    # the website's security policy lets only the page's own scripts run, not a worker made from them: the engine
    # runs on the page there (data-noworker) until the policy allows "worker-src blob:"
    return ('<!doctype html>\n<html lang="en"' + (' data-noworker' if site else '') + '>\n<head>\n<meta charset="utf-8">\n'
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
