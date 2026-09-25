#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
烈火家今天的饭 — 二维码邀请函生成器

    python3 tools/make_invite.py --room "2-338" --line "烈火请您用餐啦"
    python3 tools/make_invite.py --room "B326" --line "请您用餐啦" --out ~/Desktop

依赖:  pip install segno pillow
验证:  pip install opencv-python numpy   (没装就跳过解码验证，会警告)

字体: 默认走 Debian/Ubuntu 的 Noto CJK 路径。macOS 上如果找不到,
      用 --font-dir 指向一个含 NotoSerifCJK-*.ttc / NotoSansCJK-*.ttc 的目录,
      或者 brew install font-noto-serif-cjk-sc font-noto-sans-cjk-sc
"""
import argparse
import io
import os
import sys

import segno
from PIL import Image, ImageDraw, ImageFont

URL_DEFAULT = "https://fire-qaq.github.io/Blaze-s-Menu/"
DISH_COUNT = 43  # 加菜以后记得改这里
CATEGORIES = "盖饭 米饭 面条 意面 小炒 炖菜 炸物 汤 小菜 甜点"

W, H = 1080, 1560
PAPER = (243, 235, 219)   # 和纸底
PLATE = (250, 246, 237)   # 二维码托板
INK = (33, 30, 25)        # 墨色，跟菜单的 --sumi 一族
AKA = (176, 26, 26)       # 朱红
RULE = (178, 166, 146)
DIM = (110, 100, 85)

FONT_DIRS = [
    "/usr/share/fonts/opentype/noto",
    "/usr/local/share/fonts",
    "/Library/Fonts",
    os.path.expanduser("~/Library/Fonts"),
]


def find_fonts(extra_dir=None):
    """返回 (serif_bold, serif_medium, sans_regular) 三个字体文件路径。"""
    wanted = {
        "serif": ["NotoSerifCJK-Bold.ttc", "NotoSerifCJK-Bold.otf"],
        "serifm": ["NotoSerifCJK-Medium.ttc", "NotoSerifCJK-Regular.ttc"],
        "sans": ["NotoSansCJK-Regular.ttc", "NotoSansCJK-Regular.otf"],
    }
    dirs = ([extra_dir] if extra_dir else []) + FONT_DIRS
    found = {}
    for key, names in wanted.items():
        for d in dirs:
            for n in names:
                p = os.path.join(d, n)
                if os.path.exists(p):
                    found[key] = p
                    break
            if key in found:
                break
    missing = [k for k in wanted if k not in found]
    if missing:
        sys.exit(
            "找不到字体: " + ", ".join(missing) + "\n"
            "在这些目录里找过: " + ", ".join(dirs) + "\n"
            "用 --font-dir 指一个含 Noto CJK 的目录，或先装字体。"
        )
    # serifm 退化成 serif 也能看
    return found["serif"], found.get("serifm", found["serif"]), found["sans"]


def build(room, line, url, out_dir, font_dir=None):
    serif, serifm, sans = find_fonts(font_dir)

    def F(path, size):
        return ImageFont.truetype(path, size)

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # 斜纹和纸肌理
    for x in range(-H, W, 9):
        d.line([(x, 0), (x + H, H)], fill=(238, 229, 212), width=1)

    # ── 顶部招牌 ──────────────────────────────
    BAND = 168
    d.rectangle([0, 0, W, BAND], fill=(26, 23, 19))
    d.rectangle([0, BAND, W, BAND + 7], fill=AKA)
    d.text((64, 42), "烈 火 家", font=F(serif, 60), fill=(245, 240, 230))
    d.text((68, 122), "今 天 的 饭", font=F(sans, 24), fill=(168, 158, 142))

    # 右上角红印
    sx, sy, sr = W - 118, 84, 54
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=AKA)
    d.text((sx, sy), "邀", font=F(serif, 54), fill=(255, 248, 240), anchor="mm")

    # ── 主句 ─────────────────────────────────
    # 字号按字数收，保证两端留白跟分隔线对得齐
    n = len(line)
    size = 84 if n <= 5 else 78 if n <= 7 else 70 if n <= 9 else 62
    d.text((W // 2, 248), line, font=F(serif, size), fill=INK, anchor="ma")
    d.line([(318, 394), (W - 318, 394)], fill=RULE, width=3)

    # ── 房号 ─────────────────────────────────
    rsize = 100 if len(room) <= 6 else 84
    d.text((W // 2, 428), room, font=F(serif, rsize), fill=AKA, anchor="ma")

    # ── 二维码（纠错 H）───────────────────────
    QS, qy = 560, 612
    bx = (W - QS) // 2
    PAD = 34
    d.rectangle([bx - PAD, qy - PAD, bx + QS + PAD, qy + QS + PAD], fill=PLATE)
    d.rectangle([bx - PAD, qy - PAD, bx + QS + PAD, qy + QS + PAD],
                outline=RULE, width=2)

    buf = io.BytesIO()
    segno.make(url, error="h").save(
        buf, kind="png", scale=20, border=0, dark="#211E19", light="#FAF6ED")
    img.paste(Image.open(buf).convert("RGB").resize((QS, QS), Image.LANCZOS),
              (bx, qy))

    # ── 码下文字 ─────────────────────────────
    y = qy + QS + PAD + 46
    d.text((W // 2, y), "扫码看今天有什么菜",
           font=F(serifm, 40), fill=INK, anchor="ma")
    d.text((W // 2, y + 66), f"{DISH_COUNT} 道 · {CATEGORIES}",
           font=F(sans, 26), fill=DIM, anchor="ma")
    d.text((W // 2, y + 118), url, font=F(sans, 26), fill=AKA, anchor="ma")

    # ── 页脚 ─────────────────────────────────
    fy = H - 96
    d.line([(64, fy), (W - 64, fy)], fill=RULE, width=2)
    d.text((64, fy + 26), "点菜品照片即可直达原视频", font=F(sans, 24), fill=DIM)
    d.text((W - 64, fy + 26), "恭 候 光 临",
           font=F(serifm, 26), fill=DIM, anchor="ra")

    os.makedirs(out_dir, exist_ok=True)
    safe = room.replace("/", "-")
    p1 = os.path.join(out_dir, f"{safe}邀请函.png")
    p2 = os.path.join(out_dir, f"{safe}邀请函-打印用.png")
    img.save(p1, optimize=True)
    img.resize((W * 2, H * 2), Image.LANCZOS).save(p2, dpi=(300, 300),
                                                   optimize=True)
    return p1, p2


def verify(path, url):
    """在五个宽度下解码。微信会压图、打印可能很小，这步别省。"""
    try:
        import cv2
        import numpy as np
    except ImportError:
        print("! 没装 opencv-python，跳过解码验证")
        return True
    det = cv2.QRCodeDetector()
    ok = True
    for w in (1080, 600, 400, 260, 160):
        im = Image.open(path)
        im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
        arr = cv2.cvtColor(np.array(im.convert("RGB")), cv2.COLOR_RGB2BGR)
        txt, *_ = det.detectAndDecode(arr)
        good = txt == url
        ok = ok and good
        print(f"  {w:>5}px  {'OK ' if good else 'FAIL'}  {txt or '(解不出)'}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--room", required=True, help='房号，例如 "2-338"')
    ap.add_argument("--line", default="请您用餐啦", help="主句")
    ap.add_argument("--url", default=URL_DEFAULT)
    ap.add_argument("--out", default=os.path.expanduser("~/Documents/菜谱/二维码"))
    ap.add_argument("--font-dir", default=None)
    a = ap.parse_args()

    p1, p2 = build(a.room, a.line, a.url, os.path.expanduser(a.out), a.font_dir)
    print(f"生成: {p1}")
    print(f"生成: {p2}")
    print("解码验证:")
    if not verify(p1, a.url):
        sys.exit("!! 有尺寸解不出来，不要交付，先查二维码区域是不是被压太小了")


if __name__ == "__main__":
    main()
