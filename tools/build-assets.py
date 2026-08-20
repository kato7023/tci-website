"""ロゴ原本から公開用の画像一式を生成する。

使い方:
    python tools/build-assets.py

原本 assets/source/tci-logo-master.png を読み、以下を生成する。
    assets/tci-logo.png       ヒーロー用ロゴ（マーク＋TCi＋タグライン）
    assets/tci-logo-mark.png  ヘッダー用ロゴ（マークのみ）
    assets/og-image.png       SNS共有用画像 1200x630
    assets/apple-touch-icon.png  180x180
    assets/favicon.ico        16/32/48

原本の背景はごく薄いグレーのグラデーションなので、純白へ寄せてから切り出す。
白背景のページ上で継ぎ目が見えないようにするため。
"""

from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "tci-logo-master.png"
OUT = ROOT / "assets"

WHITE = (255, 255, 255)
WHITE_THRESHOLD = 245  # これ以上の明度は背景とみなして純白へ
INK_THRESHOLD = 200    # これ未満の明度をロゴの線とみなす


def load_flattened() -> Image.Image:
    im = Image.open(SRC).convert("RGBA")
    flat = Image.new("RGB", im.size, WHITE)
    flat.paste(im, mask=im.split()[3])
    gray = flat.convert("L")
    bg_mask = gray.point(lambda v: 255 if v >= WHITE_THRESHOLD else 0).convert("L")
    flat.paste(Image.new("RGB", flat.size, WHITE), mask=bg_mask)
    return flat


def ink_blocks(img: Image.Image):
    """縦方向の空白で区切られたロゴ要素の座標を返す。"""
    mask = img.convert("L").point(lambda v: 255 if v < INK_THRESHOLD else 0)
    w, h = mask.size
    rows = [mask.crop((0, y, w, y + 1)).getbbox() is not None for y in range(h)]
    blocks, start = [], None
    for y, has_ink in enumerate(rows):
        if has_ink and start is None:
            start = y
        elif not has_ink and start is not None:
            blocks.append((start, y - 1))
            start = None
    if start is not None:
        blocks.append((start, h - 1))
    out = []
    for top, bottom in blocks:
        box = mask.crop((0, top, w, bottom + 1)).getbbox()
        out.append((box[0], top, box[2], bottom + 1))
    return out


def crop(img, box, pad=0):
    left, top, right, bottom = box
    w, h = img.size
    return img.crop((max(0, left - pad), max(0, top - pad),
                     min(w, right + pad), min(h, bottom + pad)))


def resize_to_width(img, width):
    height = round(img.height * width / img.width)
    return img.resize((width, height), Image.LANCZOS)


def save_png(img, name, colors=192):
    """パレットPNGへ量子化して保存する。グラデーションのロゴでも劣化が目立たず容量が小さい。"""
    path = OUT / name
    img.convert("RGB").quantize(colors=colors, method=Image.MEDIANCUT).save(
        path, "PNG", optimize=True)
    print(f"{name}: {img.width}x{img.height}  {path.stat().st_size // 1024} KB")


def main():
    flat = load_flattened()
    blocks = ink_blocks(flat)
    if len(blocks) < 3:
        raise SystemExit(f"ロゴ要素を3つ検出できなかった: {blocks}")
    mark, wordmark, tagline = blocks[0], blocks[1], blocks[2]

    lockup_box = (min(b[0] for b in blocks), mark[1],
                  max(b[2] for b in blocks), tagline[3])

    save_png(resize_to_width(crop(flat, lockup_box, pad=16), 1000), "tci-logo.png")
    save_png(resize_to_width(crop(flat, mark, pad=8), 360), "tci-logo-mark.png", colors=128)

    # SNS共有用 1200x630
    og = Image.new("RGB", (1200, 630), WHITE)
    lockup = resize_to_width(crop(flat, lockup_box, pad=16), 760)
    og.paste(lockup, ((1200 - lockup.width) // 2, (630 - lockup.height) // 2))
    save_png(og, "og-image.png", colors=192)

    # アイコン類はマークのみを正方形の中央へ置く
    icon_src = crop(flat, mark, pad=8)
    side = max(icon_src.size)
    square = Image.new("RGB", (side, side), WHITE)
    square.paste(icon_src, ((side - icon_src.width) // 2, (side - icon_src.height) // 2))

    touch = Image.new("RGB", (180, 180), WHITE)
    inner = square.resize((156, 156), Image.LANCZOS)
    touch.paste(inner, (12, 12))
    save_png(touch, "apple-touch-icon.png", colors=128)

    square.resize((256, 256), Image.LANCZOS).save(
        OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    print(f"favicon.ico: {(OUT / 'favicon.ico').stat().st_size // 1024} KB")

    print(f"検出したロゴ要素: マーク={mark} 文字={wordmark} タグライン={tagline}")


if __name__ == "__main__":
    main()
