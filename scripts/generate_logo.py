"""Generate pixel-art app icon for TLS."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SIZE = 64
OUT_DIR = Path(__file__).resolve().parent.parent / "resources"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def draw_pixel_font(draw, x, y, text, size, fill):
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except OSError:
        font = ImageFont.load_default()
    draw.text((x, y), text, fill=fill, font=font)


def create_logo() -> Image.Image:
    img = Image.new("RGBA", (SIZE, SIZE), (26, 26, 46, 255))
    draw = ImageDraw.Draw(img)

    inside = 4
    draw.rounded_rectangle(
        [inside, inside, SIZE - 1 - inside, SIZE - 1 - inside],
        radius=6, fill=None, outline=(80, 80, 120, 255), width=2,
    )

    draw_pixel_font(draw, 8, 14, "TLS", 28, (200, 200, 220, 255))

    tl_x, tl_y = 44, 48
    r, gap = 3, 2
    colors = [(231, 76, 60), (241, 196, 15), (46, 204, 113)]
    for i, c in enumerate(colors):
        y_off = (i - 1) * (2 * r + gap)
        draw.ellipse(
            [tl_x - r, tl_y + y_off - r, tl_x + r, tl_y + y_off + r],
            fill=c + (200,), outline=(200, 200, 220, 180), width=1,
        )

    return img


def main() -> None:
    img = create_logo()
    png_path = OUT_DIR / "icon.png"
    img.save(png_path)
    print(f"  PNG: {png_path}")

    ico_path = OUT_DIR / "icon.ico"
    img.save(ico_path, format="ICO", sizes=[(SIZE, SIZE)])
    print(f"  ICO: {ico_path}")


if __name__ == "__main__":
    main()
