# -*- coding: utf-8 -*-
"""把 photo.png 生成 manifest.json 需要的全部 App 图标尺寸。"""
import os
from PIL import Image

SRC = os.path.join(os.path.dirname(__file__), "photo.png")
OUT = os.path.join(os.path.dirname(__file__), "unpackage", "res", "icons")

# manifest.json 中引用的全部尺寸
SIZES = [20, 29, 40, 58, 60, 72, 76, 80, 87, 96,
         120, 144, 152, 167, 180, 192, 1024]

def main():
    img = Image.open(SRC).convert("RGBA")
    os.makedirs(OUT, exist_ok=True)
    for s in SIZES:
        resized = img.resize((s, s), Image.LANCZOS)
        path = os.path.join(OUT, f"{s}x{s}.png")
        resized.save(path, "PNG", optimize=True)
        print(f"  ok  {s}x{s}.png")
    print("DONE", len(SIZES), "icons ->", OUT)

if __name__ == "__main__":
    main()
