#!/usr/bin/env python3
"""Догрузка HD-версий изображений со старых сайтов ИПМ.

В дампах (proekt-m.com, ipm.rf) сохранились только уменьшенные превью вида
`212x209_name.jpg` / `98x135_name.jpg`. На «живых» сайтах рядом с превью лежит
оригинал без размерного префикса. Скрипт находит все превью в локальных дампах,
конструирует URL оригинала на боевом сайте и скачивает HD-версию.

Запуск на сервере:
    pip install requests
    python3 fetch_hd_images.py

Результат складывается в ./hd_images/<домен>/<тот же путь, но без префикса размера>.
"""
import os
import re
import sys
from urllib.parse import quote

try:
    import requests
except ImportError:
    sys.exit("Установите зависимость:  pip install requests")

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Локальный дамп -> базовый URL «живого» сайта
SITES = {
    "ipm.rf": "http://www.xn----8sbokaorkikhmbagi.xn--p1ai",
    "proekt-m.com": "http://proekt-m.com",
}

OUTPUT_DIR = "hd_images"
SIZE_PREFIX = re.compile(r"^\d+x\d+_")          # 212x209_ , 98x135_ ...
IMG_EXT = (".jpg", ".jpeg", ".png", ".gif", ".webp")
HEADERS = {"User-Agent": "Mozilla/5.0 (HD image refetch)"}

session = requests.Session()
session.headers.update(HEADERS)


def candidate_names(filename):
    """Возможные имена оригинала для данного превью."""
    names = []
    stripped = SIZE_PREFIX.sub("", filename)
    if stripped != filename:
        names.append(stripped)                  # без префикса размера
    # proekt-m.com: маленькие *_s.jpg -> большие *_b.jpg
    base, ext = os.path.splitext(filename)
    if base.endswith("_s"):
        names.append(base[:-2] + "_b" + ext)
    names.append(filename)                       # как есть (fallback)
    # уникализируем, сохраняя порядок
    seen, out = set(), []
    for n in names:
        if n not in seen:
            seen.add(n); out.append(n)
    return out


def download(url):
    try:
        r = session.get(url, timeout=20, verify=False, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        if r.status_code == 200 and (ct.startswith("image/") or url.lower().endswith(IMG_EXT)):
            return r.content
    except Exception as e:
        print(f"  ! {url}: {e}")
    return None


def save(local_root, rel_dir, name, content):
    out_path = os.path.join(OUTPUT_DIR, local_root, rel_dir, name)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(content)
    return out_path


def process_site(local_root, base_url):
    if not os.path.isdir(local_root):
        print(f"пропуск: нет каталога {local_root}")
        return 0, 0
    got = tried = 0
    for dirpath, _dirs, files in os.walk(local_root):
        for fn in files:
            if not fn.lower().endswith(IMG_EXT):
                continue
            rel_dir = os.path.relpath(dirpath, local_root)
            for cand in candidate_names(fn):
                # уже скачивали?
                out_path = os.path.join(OUTPUT_DIR, local_root, rel_dir, cand)
                if os.path.exists(out_path):
                    break
                url_path = os.path.join(rel_dir, cand).replace("\\", "/")
                url = base_url.rstrip("/") + "/" + quote(url_path)
                tried += 1
                data = download(url)
                if data:
                    p = save(local_root, rel_dir, cand, data)
                    got += 1
                    print(f"  + {p}  ({len(data)//1024} КБ)")
                    break
    return got, tried


def main():
    total_got = total_tried = 0
    for local_root, base_url in SITES.items():
        print(f"\n=== {local_root} -> {base_url} ===")
        g, t = process_site(local_root, base_url)
        total_got += g; total_tried += t
    print(f"\nГотово. Скачано HD: {total_got} из {total_tried} попыток. "
          f"Каталог: {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
