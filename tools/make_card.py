"""Карточка-инфографика «Дело Таганрога» 1080x1080 в фирменных цветах.

Запуск:  python3 tools/make_card.py card.json cards/ГГГГ-ММ-ДД_тема.png

card.json:
{
  "top": "ЗАРПЛАТЫ ТАГАНРОГА · I КВАРТАЛ 2026",       # надзаголовок
  "big": "96 177 ₽",                                  # главная цифра
  "sub": ["средняя зарплата на крупных", "и средних заводах города"],  # 1–2 строки
  "badge": "+10,2% за год",                           # плашка (можно пустую строку)
  "cols": [["Малые производства", "76 915 ₽"], ["На руки после НДФЛ", "≈83 670 ₽"]],  # 0–2 колонки
  "source": "Источник: администрация Таганрога"
}
Шрифт Inter (если нет — DejaVu Sans). Пометку «Иллюстрация создана ИИ» не ставим.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W = 1080
NAVY, NAVY2, WHITE, ORANGE, MUTED = (14, 32, 68), (24, 48, 96), (255, 255, 255), (255, 140, 26), (170, 185, 215)
INTER = "/usr/share/fonts/opentype/inter/"
DEJAVU = "/usr/share/fonts/truetype/dejavu/"


def font(weight, size):
    names = {"medium": ("Inter-Medium.otf", "DejaVuSans.ttf"), "semibold": ("Inter-SemiBold.otf", "DejaVuSans-Bold.ttf"),
             "bold": ("Inter-Bold.otf", "DejaVuSans-Bold.ttf"), "extrabold": ("Inter-ExtraBold.otf", "DejaVuSans-Bold.ttf")}[weight]
    for path in (INTER + names[0], DEJAVU + names[1]):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def fit(d, text, weight, size, max_w):
    f = font(weight, size)
    while d.textlength(text, font=f) > max_w and size > 20:
        size -= 4
        f = font(weight, size)
    return f


def main(spec_path, out_path):
    c = json.load(open(spec_path, encoding="utf-8"))
    im = Image.new("RGB", (W, W), NAVY)
    d = ImageDraw.Draw(im)
    for i, h in enumerate([160, 210, 250, 300, 360, 430]):  # фоновый «растущий» график
        x = 600 + i * 75
        d.rectangle([x, W - 150 - h, x + 50, W - 150], fill=NAVY2)
    d.rectangle([0, 0, W, 14], fill=ORANGE)

    def center(y, text, f, fill):
        d.text(((W - d.textlength(text, font=f)) / 2, y), text, font=f, fill=fill)

    center(80, c["top"], fit(d, c["top"], "semibold", 34, W - 120), MUTED)
    center(250, c["big"], fit(d, c["big"], "extrabold", 190, W - 100), ORANGE)
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
    sf = fit(d, c.get("source", ""), "medium", 26, 600)
    d.text((W - 60 - d.textlength(c.get("source", ""), font=sf), 1012), c.get("source", ""), font=sf, fill=MUTED)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    im.save(out_path)
    print(out_path)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
