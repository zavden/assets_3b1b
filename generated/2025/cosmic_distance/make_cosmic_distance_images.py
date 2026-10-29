"""Placeholder images and icons of 2025/cosmic_distance (the originals lived in Grant's Dropbox).
Called by make_cosmic_distance_assets.py ("images"/"all" mode); it can also be run on its own.

They come out next to this file:
  GalaxyStill.png                          face-on spiral galaxy (procedural)
  JovianSystem.png                         labeled placeholder image
  Nile.png                                 schematic map of the Nile and the delta (procedural)
  LunarEclipseComposite.jpg                lunar eclipse composite with moons inside the Earth's shadow
  Paul Animations/6. Transit Of Venus/New Transit of Venus scenes/JustSunBackgroundRemoved.png, JustSun.tif
                                           derived from raster_images/sun.png (the sun the lib already has)
  supplements/SunAndThumb.jpg              sky with the sun and a thumb (procedural)
  KurtArtwork/TheWellOfSyene.jpg           stone well with water (procedural)
  KurtArtwork/AristarchusProposingEarthGoesAroundTheSun.jpg + stencil-luma-masks/figure-{1..9}-masked.png
                                           scene with 9 generic silhouettes and their masks
  TerenceTaoPapers/paper_NN.png            placeholder paper pages (placeholder.py)
  names/<name>.png                         images by name (placeholder portraits, TerryTaoFieldsMedal, Dime, StarFourPoints)
  svg/<name>.svg                           generic icons (youtube_logo, email, x_logo, bluesky_logo, rss_logo)"""
import importlib.util
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
LIB = HERE.parent.parent.parent
RASTER = LIB / "raster_images"
TOOLS = LIB.parent.parent / "_tools"
W, H = 1920, 1080
PX = H / 8.0        # pixels per scene unit (the scene is 8 tall)


def font(size):
    try:
        return ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def u2p(x, y):
    """Scene coordinates -> pixels of a full-screen image."""
    return W / 2 + x * PX, H / 2 - y * PX


def placeholder_tool():
    spec = importlib.util.spec_from_file_location("placeholder", TOOLS / "placeholder.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def noise(shape, scale, rng):
    """Soft noise: random noise enlarged with bicubic interpolation, in [0, 1]."""
    h, w = shape
    small = rng.random((max(2, h // scale), max(2, w // scale))).astype(np.float32)
    im = Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return np.asarray(im).astype(np.float32) / 255


# ---------------------------------------------------------------- galaxy
def make_galaxy_still(seed=1):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = u2p(0.0, 0.05)
    x = (xx - cx) / PX
    y = -(yy - cy) / PX * 1.0
    r = np.sqrt(x**2 + y**2) + 1e-3
    th = np.arctan2(y, x)
    bulge = np.exp(-(r / 0.30) ** 1.2) * 1.4
    disk = np.exp(-r / 1.35)
    arms = 0.5 + 0.5 * np.cos(2 * (th - np.log(r / 0.4) / math.tan(math.radians(14))))
    arms = arms ** 2.2
    clumps = noise((H, W), 24, rng)
    dens = bulge + disk * (0.25 + 1.5 * arms * (0.5 + clumps)) * (r < 3.4) * np.clip((3.4 - r) / 1.2, 0, 1)
    dust = np.clip(arms * noise((H, W), 40, rng) - 0.15, 0, 1) * 0.5 * np.exp(-r / 2.0)
    dens = dens * (1 - dust)
    core = np.array([255, 224, 170], np.float32)
    blue = np.array([150, 185, 255], np.float32)
    mix = np.clip(r / 2.2, 0, 1)[..., None]
    color = core * (1 - mix) + blue * mix
    img = np.clip(color * dens[..., None] * 0.75, 0, 255)
    # pink HII regions along the arms
    pink = (arms > 0.8) & (noise((H, W), 6, rng) > 0.86) & (r > 0.6) & (r < 3.0)
    img[pink] = img[pink] * 0.4 + np.array([255, 120, 190]) * 0.8
    # background stars
    stars = rng.random((H, W)) > 0.9985
    img[stars] = 255
    Image.fromarray(img.astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)).save(HERE / "GalaxyStill.png")


# ---------------------------------------------------------------- Nile
def make_nile(seed=2):
    rng = np.random.default_rng(seed)
    base = np.zeros((H, W, 3), np.float32)
    sand = np.array([214, 187, 140], np.float32)
    n1 = noise((H, W), 60, rng)
    n2 = noise((H, W), 12, rng)
    base[:] = sand * (0.85 + 0.2 * n1[..., None] + 0.08 * n2[..., None])
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    # sea in the lower left corner
    d.polygon([(0, 560), (120, 640), (260, 690), (420, 730), (600, 780), (800, 860), (1000, 1080), (0, 1080)], fill=(40, 90, 150))
    # river: winding curve from Syene (upper right) to the delta
    p0, p1 = u2p(2.78, 1.12), (330, 690)
    pts = []
    for t in np.linspace(0, 1, 160):
        x = p0[0] + (p1[0] - p0[0]) * t + 55 * math.sin(7 * t * math.pi) * (1 - t * 0.3)
        y = p0[1] + (p1[1] - p0[1]) * t + 35 * math.sin(5 * t * math.pi + 1)
        pts.append((x, y))
    # extends the river upstream toward the upper right edge
    pts = [(p0[0] + 500 - 500 * s, p0[1] - 260 + 260 * s) for s in np.linspace(0, 1, 40)] + pts
    w_river = 14
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i + 1]], fill=(60, 130, 190), width=w_river)
    # green fertile strip
    fertile = Image.new("L", (W, H), 0)
    fd = ImageDraw.Draw(fertile)
    for i in range(len(pts) - 1):
        fd.line([pts[i], pts[i + 1]], fill=255, width=70)
    fertile = fertile.filter(ImageFilter.GaussianBlur(14))
    green = Image.new("RGB", (W, H), (70, 130, 60))
    img = Image.composite(green, img, fertile.point(lambda v: int(v * 0.85)))
    d = ImageDraw.Draw(img)
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i + 1]], fill=(60, 140, 200), width=8)
    # delta
    end = pts[-1]
    for k in range(-3, 4):
        d.line([end, (end[0] - 160 + 25 * k, end[1] + 60 + 40 * abs(k) * 0.3 + 20 * k)], fill=(60, 140, 200), width=5)
    d.text((W - 30, H - 24), "[mapa del Nilo: imagen de relleno]", font=font(26), fill=(30, 30, 30), anchor="rm")
    img.save(HERE / "Nile.png")


# ---------------------------------------------------------------- eclipse lunar
def make_eclipse_composite():
    moon = Image.open(RASTER / "moon.png").convert("RGBA")
    img = Image.new("RGB", (W, H), (4, 4, 8))
    rng = np.random.default_rng(3)
    arr = np.asarray(img).astype(np.float32)
    # stars
    ys, xs = rng.integers(0, H, 400), rng.integers(0, W, 400)
    arr[ys, xs] = rng.integers(60, 200, (400, 1))
    img = Image.fromarray(arr.astype(np.uint8))
    # Earth's shadow: faint reddish circle (umbra) with a soft edge
    cx, cy = u2p(1.503, -0.043)
    R = 2.48 * PX
    shadow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shadow).ellipse([cx - R, cy - R, cx + R, cy + R], fill=255)
    shadow = shadow.filter(ImageFilter.GaussianBlur(5))
    img = Image.composite(Image.new("RGB", (W, H), (45, 14, 10)), img, shadow.point(lambda v: int(v * 0.8)))
    # moons: one on the left (the scene's small circle) and four stacked inside the shadow
    moon_r = 0.62 * PX
    centers = [u2p(-1.0, -0.167)]
    ang = math.radians(8)
    for k in range(4):
        off = (k - 1.5) * 1.24
        centers.append(u2p(1.503 - off * math.sin(ang) * -1, -0.043 - off * math.cos(ang)))
    for i, (mx, my) in enumerate(centers):
        m = moon.resize((int(2 * moon_r), int(2 * moon_r)), Image.LANCZOS)
        # the moons inside the shadow look reddish and darker
        if i > 0:
            a = np.asarray(m).astype(np.float32)
            lum = a[..., :3].mean(axis=2, keepdims=True)
            a[..., :3] = np.clip(lum * np.array([1.0, 0.42, 0.22]) * 0.8, 0, 255)
            m = Image.fromarray(a.astype(np.uint8), "RGBA")
        img.paste(m, (int(mx - moon_r), int(my - moon_r)), m)
    d = ImageDraw.Draw(img)
    d.text((W - 30, H - 24), "[composición de eclipse: imagen de relleno]", font=font(26), fill=(200, 200, 200), anchor="rm")
    img.save(HERE / "LunarEclipseComposite.jpg", quality=92)


# ---------------------------------------------------------------- sun (derived from raster_images/sun.png)
def make_sun_images():
    sun = Image.open(RASTER / "sun.png").convert("RGBA")
    out = HERE / "Paul Animations" / "6. Transit Of Venus" / "New Transit of Venus scenes"
    out.mkdir(parents=True, exist_ok=True)
    cx, cy, R = 1111, 1100, 985            # disk measured on sun.png
    box = (cx - R - 4, cy - R - 4, cx + R + 4, cy + R + 4)
    disc = sun.crop(box)
    mask = Image.new("L", disc.size, 0)
    ImageDraw.Draw(mask).ellipse([4, 4, disc.size[0] - 4, disc.size[1] - 4], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(1.2))
    alpha = Image.fromarray(np.minimum(np.asarray(mask), 255).astype(np.uint8))
    disc.putalpha(alpha)
    disc.save(out / "JustSunBackgroundRemoved.png")
    bg = Image.new("RGB", sun.size, (0, 0, 0))
    bg.paste(sun, (0, 0), sun)
    bg.save(out / "JustSun.tif")


def make_sun_and_thumb(seed=4):
    sub = HERE / "supplements"
    sub.mkdir(exist_ok=True)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    top = np.array([60, 110, 190], np.float32)
    low = np.array([160, 200, 240], np.float32)
    t = (yy / H)[..., None]
    img = top * (1 - t) + low * t
    sx, sy = u2p(-0.63, 1.36)
    dist = np.sqrt((xx - sx) ** 2 + (yy - sy) ** 2)
    glow = np.exp(-dist / 60)[..., None] * np.array([255, 245, 210]) * 0.9 + np.exp(-dist / 260)[..., None] * np.array([120, 110, 80])
    img = np.clip(img + glow, 0, 255)
    img[dist < 0.115 * PX] = 255
    im = Image.fromarray(img.astype(np.uint8))
    d = ImageDraw.Draw(im)
    # thumb at one side of the sun (skin-colored rounded rectangle) coming from below
    d.rounded_rectangle([sx + 90, sy + 40, sx + 230, H + 60], radius=60, fill=(214, 160, 130), outline=(170, 120, 95), width=4)
    d.ellipse([sx + 120, sy + 90, sx + 200, sy + 130], fill=(226, 178, 150))
    d.text((W - 30, H - 24), "[foto del sol y un pulgar: imagen de relleno]", font=font(26), fill=(30, 40, 60), anchor="rm")
    im.save(sub / "SunAndThumb.jpg", quality=92)


# ---------------------------------------------------------------- well of Syene
def make_well(seed=5):
    out = HERE / "KurtArtwork"
    out.mkdir(exist_ok=True)
    rng = np.random.default_rng(seed)
    n = noise((H, W), 10, rng)
    base = np.array([150, 125, 95], np.float32) * (0.7 + 0.5 * n[..., None])
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    # bricks
    bh, bw = 54, 120
    for row in range(H // bh + 1):
        off = (row % 2) * bw // 2
        for col in range(-1, W // bw + 2):
            x0, y0 = col * bw + off, row * bh
            shade = int(rng.integers(-18, 18))
            d.rectangle([x0 + 2, y0 + 2, x0 + bw - 2, y0 + bh - 2], fill=(160 + shade, 133 + shade, 100 + shade))
    # opening of the well with water
    cx, cy = u2p(-2.3, 0.84)
    for k, (rx, ry, col) in enumerate([(300, 180, (90, 80, 70)), (255, 150, (20, 30, 40)), (230, 135, (30, 70, 100))]):
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=col)
    sx, sy = u2p(-2.36, 1.26)
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    ImageDraw.Draw(glow).ellipse([sx - 55, sy - 25, sx + 55, sy + 25], fill=(255, 240, 200))
    glow = glow.filter(ImageFilter.GaussianBlur(25))
    img = Image.fromarray(np.clip(np.asarray(img).astype(np.int32) + np.asarray(glow).astype(np.int32), 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    d.text((W - 30, H - 24), "[pozo de Siena: imagen de relleno]", font=font(26), fill=(230, 230, 230), anchor="rm")
    img.save(out / "TheWellOfSyene.jpg", quality=92)


# ---------------------------------------------------------------- Aristarchus + masks
def _figure(draw, x, base_y, h, fill, outline=None):
    """Generic silhouette of a person in a tunic."""
    head_r = h * 0.075
    draw.ellipse([x - head_r, base_y - h, x + head_r, base_y - h + 2 * head_r], fill=fill, outline=outline)
    draw.polygon([(x - h * 0.10, base_y - h + 2.2 * head_r), (x + h * 0.10, base_y - h + 2.2 * head_r),
                  (x + h * 0.20, base_y), (x - h * 0.20, base_y)], fill=fill, outline=outline)
    draw.line([(x - h * 0.10, base_y - h * 0.72), (x - h * 0.24, base_y - h * 0.5)], fill=fill, width=max(4, int(h * 0.05)))
    draw.line([(x + h * 0.10, base_y - h * 0.72), (x + h * 0.24, base_y - h * 0.52)], fill=fill, width=max(4, int(h * 0.05)))


def make_aristarchus():
    out = HERE / "KurtArtwork"
    masks = out / "stencil-luma-masks"
    masks.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(6)
    yy = np.linspace(0, 1, H)[:, None, None]
    top, low = np.array([40, 55, 95]), np.array([230, 170, 110])
    grad = (top * (1 - yy) + low * yy) * np.ones((1, W, 1))
    img = Image.fromarray(grad.astype(np.uint8))
    d = ImageDraw.Draw(img)
    d.rectangle([0, H * 0.78, W, H], fill=(120, 90, 60))
    for i in range(7):                      # columns
        x = 120 + i * 270
        d.rectangle([x, 160, x + 60, H * 0.78], fill=(205, 190, 165))
        d.rectangle([x - 12, 140, x + 72, 170], fill=(220, 205, 180))
    d.ellipse([W * 0.5 - 90, 60, W * 0.5 + 90, 240], fill=(255, 225, 150))   # sol
    xs = np.linspace(190, W - 190, 9)
    heights = [420, 470, 440, 500, 460, 430, 480, 450, 420]
    fills = [(88, 58, 70), (60, 80, 110), (120, 80, 55), (70, 95, 70), (110, 60, 90), (60, 70, 100), (130, 100, 60), (80, 60, 60), (70, 90, 100)]
    for x, hh, c in zip(xs, heights, fills):
        _figure(d, x, H * 0.88, hh, c)
    d.text((W - 30, H - 24), "[ilustración: imagen de relleno]", font=font(26), fill=(255, 255, 255), anchor="rm")
    img.save(out / "AristarchusProposingEarthGoesAroundTheSun.jpg", quality=92)
    for n, (x, hh, c) in enumerate(zip(xs, heights, fills), start=1):
        m = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        _figure(ImageDraw.Draw(m), x, H * 0.88, hh, tuple(min(255, int(v * 1.6)) for v in c) + (255,))
        m.save(masks / f"figure-{n}-masked.png")


# ---------------------------------------------------------------- by name (raster_images)
def make_named_images():
    ph = placeholder_tool()
    out = HERE / "names"
    out.mkdir(exist_ok=True)
    portraits = {
        "Head_of_Aristotle": "Aristóteles", "Eratosthenes": "Eratóstenes", "Kepler": "Kepler", "Copernicus": "Copérnico",
        "TychoBrahe": "Tycho Brahe", "JamesCook": "James Cook", "EdmondHalley": "Edmond Halley", "OleRomer": "Ole Rømer",
        "ChristiaanHuygens": "Christiaan Huygens", "FriedrichBessel": "Friedrich Bessel", "HenriettaLeavitt": "Henrietta Leavitt",
        "EdwinHubble": "Edwin Hubble",
    }
    bgs = ["#4a3f35", "#35444a", "#443a4a", "#3a4a38", "#4a4535", "#35384a"]
    for i, (name, label) in enumerate(portraits.items()):
        ph.make_image(str(out / f"{name}.png"), f"Retrato de {label}", (800, 1000), bgs[i % len(bgs)])
    ph.make_image(str(out / "TerryTaoFieldsMedal.png"), "Terence Tao recibiendo la Medalla Fields", (1200, 900), "#3a3550")
    # Dime coin (generic): silver disk with a ridged edge
    S = 800
    coin = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(coin)
    d.ellipse([20, 20, S - 20, S - 20], fill=(150, 152, 158, 255))
    for k in range(120):
        a = 2 * math.pi * k / 120
        d.line([S / 2 + 372 * math.cos(a), S / 2 + 372 * math.sin(a), S / 2 + 392 * math.cos(a), S / 2 + 392 * math.sin(a)], fill=(110, 112, 118, 255), width=6)
    d.ellipse([60, 60, S - 60, S - 60], fill=(190, 192, 198, 255), outline=(120, 122, 128, 255), width=6)
    d.ellipse([140, 140, S - 140, S - 140], outline=(150, 152, 158, 255), width=8)
    d.text((S / 2, S / 2), "[moneda\nde relleno]", font=font(60), fill=(90, 92, 98, 255), anchor="mm", align="center")
    coin.save(out / "Dime.png")
    # Four-pointed flash
    S = 512
    star = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    dx, dy = (xx - S / 2) / (S / 2), (yy - S / 2) / (S / 2)
    a = np.clip(np.exp(-(np.abs(dx) * 14) ** 1.0) * np.exp(-np.abs(dy) * 2.5) + np.exp(-(np.abs(dy) * 14) ** 1.0) * np.exp(-np.abs(dx) * 2.5), 0, 1)
    a = np.maximum(a, np.exp(-(dx**2 + dy**2) * 30))
    arr = np.zeros((S, S, 4), np.uint8)
    arr[..., :3] = 255
    arr[..., 3] = (a * 255).astype(np.uint8)
    Image.fromarray(arr, "RGBA").save(out / "StarFourPoints.png")


def make_papers():
    ph = placeholder_tool()
    out = HERE / "TerenceTaoPapers"
    out.mkdir(exist_ok=True)
    titles = ["On the Fourier analysis of sets", "Arithmetic progressions in the primes", "Compressed sensing: notes", "Nonlinear dispersive equations",
              "Additive combinatorics, a survey", "Structure and randomness", "Sieve methods revisited", "Harmonic analysis and PDE", "A note on prime gaps",
              "Universality in random matrices", "Ergodic theory and combinatorics", "Wave maps and regularity"]
    for i, t in enumerate(titles):
        ph.make_page(str(out / f"paper_{i + 1:02d}.png"), t, 36, i + 1)


# ---------------------------------------------------------------- generic SVG icons
def make_svgs():
    out = HERE / "svg"
    out.mkdir(exist_ok=True)

    def wrap(body, w=500, h=500):
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}pt" height="{h}pt" viewBox="0 0 {w} {h}">\n{body}\n</svg>\n'

    # Generic YouTube-like: red rounded rectangle with a white triangle
    (out / "youtube_logo.svg").write_text(wrap(
        '<rect x="20" y="105" width="460" height="290" rx="85" fill="#E62117"/>\n<polygon points="200,175 200,325 330,250" fill="#FFFFFF"/>'))
    # Mail envelope
    (out / "email.svg").write_text(wrap(
        '<rect x="30" y="100" width="440" height="300" rx="28" fill="#FFFFFF"/>\n'
        '<polyline points="30,120 250,290 470,120" fill="none" stroke="#555555" stroke-width="26" stroke-linejoin="round"/>'))
    # Generic "X": two crossed strokes
    (out / "x_logo.svg").write_text(wrap(
        '<polygon points="60,60 150,60 440,440 350,440" fill="#FFFFFF"/>\n<polygon points="440,60 350,60 60,440 150,440" fill="#FFFFFF"/>'))
    # Blue circle with two petals (generic)
    (out / "bluesky_logo.svg").write_text(wrap(
        '<circle cx="250" cy="250" r="230" fill="#1185FE"/>\n'
        '<path d="M250 250 C 190 150 110 140 110 215 C 110 260 150 300 250 270 C 350 300 390 260 390 215 C 390 140 310 150 250 250 Z" fill="#FFFFFF"/>'))
    # Feed symbol (a dot and two arcs)
    (out / "rss_logo.svg").write_text(wrap(
        '<rect x="20" y="20" width="460" height="460" rx="90" fill="#F26522"/>\n<circle cx="140" cy="360" r="38" fill="#FFFFFF"/>\n'
        '<path d="M 100 215 A 185 185 0 0 1 285 400" fill="none" stroke="#FFFFFF" stroke-width="42"/>\n'
        '<path d="M 100 110 A 290 290 0 0 1 390 400" fill="none" stroke="#FFFFFF" stroke-width="42"/>'))


def make_all():
    make_galaxy_still()
    make_nile()
    make_eclipse_composite()
    make_sun_images()
    make_sun_and_thumb()
    make_well()
    make_aristarchus()
    make_named_images()
    make_papers()
    make_svgs()
    ph = placeholder_tool()
    ph.make_image(str(HERE / "JovianSystem.png"), "Sistema joviano (JovianSystem)", (1920, 1080), "#2f3345")


if __name__ == "__main__":
    make_all()
