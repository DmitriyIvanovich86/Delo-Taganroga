"""Карточка «Дело Таганрога» 1080x1080 по ссылке (Vercel).

Ссылка:  https://<сайт>.vercel.app/api/card?d=<card.json в base64url>
Поля card.json: top, big, sub (1-2 строки), badge, cols (0-2 пары [подпись, значение]), source
Шрифт Inter (OFL) скачивается сам из репозитория Google Fonts.
"""
import base64
import io
import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from PIL import Image, ImageDraw, ImageFont

W = 1080
NAVY, NAVY2, WHITE, ORANGE, MUTED = (14, 32, 68), (24, 48, 96), (255, 255, 255), (255, 140, 26), (170, 185, 215)
FONT_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf"
FONT_PATH = os.environ.get("CARD_FONT", "/tmp/Inter.ttf")
WEIGHTS = {"medium": 500, "semibold": 600, "bold": 700, "extrabold": 800}
_cache = {}


def font(weight, size):
    key = (weight, size)
    if key not in _cache:
        if not os.path.exists(FONT_PATH):
            urllib.request.urlretrieve(FONT_URL, FONT_PATH)
        f = ImageFont.truetype(FONT_PATH, size)
        f.set_variation_by_axes([32 if size >= 40 else 14, WEIGHTS[weight]])
        _cache[key] = f
    return _cache[key]


def fit(d, text, weight, size, max_w):
    f = font(weight, size)
    while d.textlength(text, font=f) > max_w and size > 20:
        size -= 4
        f = font(weight, size)
    return f


def render(c):
    im = Image.new("RGB", (W, W), NAVY)
    d = ImageDraw.Draw(im)
    for i, h in enumerate([160, 210, 250, 300, 360, 430]):
        x = 600 + i * 75
        d.rectangle([x, W - 150 - h, x + 50, W - 150], fill=NAVY2)
    d.rectangle([0, 0, W, 14], fill=ORANGE)

    def center(y, text, f, fill):
        d.text(((W - d.textlength(text, font=f)) / 2, y), text, font=f, fill=fill)

    center(80, c.get("top", ""), fit(d, c.get("top", ""), "semibold", 34, W - 120), MUTED)
    center(250, c.get("big", ""), fit(d, c.get("big", ""), "extrabold", 190, W - 100), ORANGE)
    for i, line in enumerate(c.get("sub", [])[:2]):
        center(490 + i * 60, line, fit(d, line, "medium", 46, W - 120), WHITE)
    if c.get("badge"):
        bf = fit(d, c["badge"], "bold", 48, W - 240)
        tw = d.textlength(c["badge"], font=bf)
        bx = (W - tw) / 2 - 36
        d.rounded_rectangle([bx, 650, bx + tw + 72, 730], radius=40, fill=ORANGE)
        d.text((bx + 36, 660), c["badge"], font=bf, fill=NAVY)
    cols = c.get("cols", [])[:2]
    if len(cols) == 2:
        d.line([(W / 2, 800), (W / 2, 930)], fill=MUTED, width=2)
    centers = [W / 2] if len(cols) == 1 else [W / 4, 3 * W / 4]
    for cx, (label, value) in zip(centers, cols):
        lf, vf = fit(d, label, "medium", 30, 440), fit(d, value, "bold", 48, 440)
        d.text((cx - d.textlength(label, font=lf) / 2, 805), label, font=lf, fill=MUTED)
        d.text((cx - d.textlength(value, font=vf) / 2, 855), value, font=vf, fill=WHITE)
    d.text((60, 1010), "Дело Таганрога", font=font("bold", 28), fill=WHITE)
    src = c.get("source", "")
    sf = fit(d, src, "medium", 26, 600)
    d.text((W - 60 - d.textlength(src, font=sf), 1012), src, font=sf, fill=MUTED)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return buf.getvalue()


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            raw = parse_qs(urlparse(self.path).query).get("d", [""])[0]
            raw += "=" * (-len(raw) % 4)
            png = render(json.loads(base64.urlsafe_b64decode(raw.encode()).decode("utf-8")))
        except Exception as e:
            self.send_response(400)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"bad card link: {e}".encode())
            return
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.send_header("Cache-Control", "public, max-age=31536000, immutable")
        self.end_headers()
        self.wfile.write(png)
