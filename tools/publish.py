#!/usr/bin/env python3
"""Публикует файл и печатает публичную HTTPS-ссылку — для отправки в Telegram по URL.

Файлы лежат в отдельной ветке `files` этого репозитория (папка f/), сайт на Vercel не пересобирается.
Ссылка: https://raw.githubusercontent.com/DmitriyIvanovich86/Delo-Taganroga/files/f/<имя>

ВНИМАНИЕ: репозиторий публичный. Сюда — только то, что не страшно показать всем
(картинки, графики, обезличенные отчёты). Персональные данные клиентов, договоры, цены под клиента — НЕ сюда.

Запуск:  python3 tools/publish.py <файл> [--name короткое_имя]
Вывод (последняя строка): URL
"""
import argparse
import datetime as dt
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile

REPO = "https://github.com/DmitriyIvanovich86/Delo-Taganroga"
RAW = "https://raw.githubusercontent.com/DmitriyIvanovich86/Delo-Taganroga/files/f/"
BRANCH = "files"
TRANSLIT = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
                    ["a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "y", "k", "l", "m", "n", "o", "p",
                     "r", "s", "t", "u", "f", "h", "c", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya"]))


def slug(s):
    s = "".join(TRANSLIT.get(c, c) for c in s.lower())
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:40] or "file"


def git(*args, cwd):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout.strip()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("path")
    p.add_argument("--name", help="короткое имя без расширения")
    a = p.parse_args()
    if not os.path.isfile(a.path):
        sys.exit(f"нет файла: {a.path}")
    if os.path.getsize(a.path) > 20 * 1024 * 1024:
        sys.exit("файл больше 20 МБ — Telegram по ссылке не возьмёт")

    stem, ext = os.path.splitext(os.path.basename(a.path))
    name = f"{dt.date.today():%Y-%m-%d}_{slug(a.name or stem)}_{secrets.token_hex(3)}{ext.lower()}"

    tmp = tempfile.mkdtemp(prefix="publish-")
    try:
        # Только ветка files, без содержимого старых файлов — быстро, сколько бы их ни накопилось
        git("clone", "--depth", "1", "--filter=blob:none", "--no-checkout", "--branch", BRANCH, REPO, tmp, cwd=".")
        git("reset", "-q", cwd=tmp)
        os.makedirs(os.path.join(tmp, "f"), exist_ok=True)
        shutil.copyfile(a.path, os.path.join(tmp, "f", name))
        git("add", f"f/{name}", cwd=tmp)
        git("-c", "user.name=Автоматизатор", "-c", "user.email=noreply@anthropic.com",
            "commit", "-q", "-m", f"Файл: {name}", cwd=tmp)
        for attempt in range(3):  # параллельная публикация из другой задачи → подтянуть и повторить
            r = subprocess.run(["git", "push", "-q", "origin", BRANCH], cwd=tmp, capture_output=True, text=True)
            if r.returncode == 0:
                break
            git("pull", "-q", "--rebase", "origin", BRANCH, cwd=tmp)
        else:
            sys.exit(f"push не прошёл: {r.stderr.strip()}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(RAW + name)


if __name__ == "__main__":
    main()
