"""Placeholder for `Adele.png` (a press photo of a singer used as one of the example photos in nn/part2::RandomlyLabeledImageData / TrainOnImages).
A press photo with copyright cannot be redistributed, and no real face is generated: this is a generic head-and-shoulders silhouette card.
Output: Adele.png next to this script. CODEX: a real replacement (a free-licence portrait or an original illustration) is welcome."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "Adele.png"
W, H = 480, 640
img = Image.new("RGB", (W, H), "#4a5568")
d = ImageDraw.Draw(img)
d.ellipse((W / 2 - 90, 130, W / 2 + 90, 330), fill="#cbd5e0")            # head
d.ellipse((W / 2 - 190, 360, W / 2 + 190, 760), fill="#cbd5e0")           # shoulders
d.rectangle((0, H - 60, W, H), fill="#2d3748")
try:
    f = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf", 30)
except OSError:
    f = ImageFont.load_default()
d.text((W / 2, H - 30), "placeholder photo", fill="#e2e8f0", font=f, anchor="mm")
img.save(OUT)
