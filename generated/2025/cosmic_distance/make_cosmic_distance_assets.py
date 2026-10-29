"""Generates the placeholder assets of 2025/cosmic_distance (textures and data that lived in Grant's Dropbox).
Everything is procedural or derived from textures that `_lib/assets/raster_images` already has; nothing is downloaded.

Usage:  python make_cosmic_distance_assets.py [textures|data|images|all]

Outputs (next to this script):
  MoonTexture.jpg        copy of raster_images/MoonTextureMap.png (real equirectangular lunar map) as JPG
  DarkMoonTexture.jpg    that map heavily darkened (unlit side)
  RedMoonTexture.jpg     that map tinted coppery red (eclipsed moon)
  SunTexture.jpg         PLACEHOLDER: solar surface with granulation and spots (2:1 equirectangular map)
  MarsTexture.jpg / DarkMarsTexture.jpg   PLACEHOLDER: reddish Mars with dark spots
  hiptyc_2020_8k.jpg     PLACEHOLDER: 8192x4096 equirectangular starry sky with a Milky Way band (equatorial coordinates)
  constellation_figures.png  PLACEHOLDER: constellation figures (lines between bright stars of the previous map)
  Data/HYG_Data.gz       PLACEHOLDER: synthetic HYG-style star catalog (columns absmag, ci, ...) with a plausible H-R diagram
  Data/solar_spectrum.csv    PLACEHOLDER: synthetic solar spectrum (5778 K blackbody + Fraunhofer lines + atmospheric bands)
  Data/galactic_data.csv     PLACEHOLDER: synthetic galaxies (objID, ra, dec, redshift, distance_mpc) with filamentary structure and Hubble's law"""
import gzip
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
LIB = HERE.parent.parent.parent                    # _lib/assets
RASTER = LIB / "raster_images"


# ------------------------------------------------------------------ utilities
def periodic_noise(shape, beta, rng):
    """Periodic 1/f^beta noise (FFT), normalized to [0, 1]."""
    h, w = shape
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    f = np.sqrt(fx**2 + fy**2)
    f[0, 0] = 1
    spec = (rng.normal(size=(h, w)) + 1j * rng.normal(size=(h, w))) / f**beta
    spec[0, 0] = 0
    x = np.fft.ifft2(spec).real.astype(np.float32)
    return (x - x.min()) / (x.max() - x.min())


def bandpass_noise(shape, period_px, rng, width=0.6):
    """Noise with energy concentrated in structures of ~period_px pixels (granulation), normalized to [0, 1]."""
    h, w = shape
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    f = np.sqrt(fx**2 + fy**2)
    f0 = 1.0 / period_px
    spec = (rng.normal(size=(h, w)) + 1j * rng.normal(size=(h, w))) * np.exp(-((f - f0) / (width * f0)) ** 2)
    spec[0, 0] = 0
    x = np.fft.ifft2(spec).real.astype(np.float32)
    return (x - x.min()) / (x.max() - x.min())


# ------------------------------------------------------------------ textures
def make_moon_textures():
    src = Image.open(RASTER / "MoonTextureMap.png").convert("RGB")
    src.save(HERE / "MoonTexture.jpg", quality=92)
    a = np.asarray(src).astype(np.float32) / 255
    dark = np.clip(a * np.array([0.10, 0.11, 0.14]), 0, 1)           # slight bluish tint ("Earthshine")
    Image.fromarray((dark * 255).astype(np.uint8)).save(HERE / "DarkMoonTexture.jpg", quality=92)
    lum = a.mean(axis=2, keepdims=True)
    red = np.clip(lum * np.array([1.0, 0.33, 0.14]) * 1.25, 0, 1)
    Image.fromarray((red * 255).astype(np.uint8)).save(HERE / "RedMoonTexture.jpg", quality=92)


def make_sun_texture(w=4096, h=2048, seed=11):
    rng = np.random.default_rng(seed)
    big = bandpass_noise((h, w), 70, rng)               # supergranulation
    gran = bandpass_noise((h, w), 22, rng)               # granulation
    fine = bandpass_noise((h, w), 9, rng, width=0.8)
    cells = 0.30 * big + 0.50 * gran + 0.20 * fine
    cells = (cells - cells.mean()) / cells.std()
    t = 1 / (1 + np.exp(-2.2 * cells))                   # bright granules with dark lanes
    # sunspots near ±15° latitude
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    lat = (0.5 - yy / h) * 180
    spots = np.zeros((h, w), np.float32)
    for _ in range(14):
        cx = rng.uniform(0, w)
        cy = h * (0.5 - rng.choice([-1, 1]) * rng.uniform(8, 22) / 180)
        r = rng.uniform(15, 55)
        dx = (xx - cx + w / 2) % w - w / 2
        d = np.sqrt(dx**2 + (yy - cy) ** 2) / r
        spots += np.exp(-d**2 * 1.5)
    spots = np.clip(spots, 0, 1)
    faculae = periodic_noise((h, w), 2.3, rng)
    bright = 0.50 + 0.50 * t + 0.14 * (faculae - 0.5)
    bright = bright * (1 - 0.75 * spots)
    # color: orange-red -> almost white yellow
    c0 = np.array([190, 55, 5], np.float32)
    c1 = np.array([255, 215, 120], np.float32)
    c2 = np.array([255, 250, 225], np.float32)
    b = np.clip(bright, 0, 1.15)[..., None]
    rgb = np.where(b < 0.75, c0 + (c1 - c0) * (b / 0.75), c1 + (c2 - c1) * np.clip((b - 0.75) / 0.4, 0, 1))
    Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).save(HERE / "SunTexture.jpg", quality=92)


def make_mars_textures(w=2048, h=1024, seed=5):
    rng = np.random.default_rng(seed)
    base = periodic_noise((h, w), 1.7, rng)
    fine = periodic_noise((h, w), 0.8, rng)
    v = 0.7 * base + 0.3 * fine
    dark_regions = np.clip((v - 0.52) * 5, 0, 1)
    rust = np.array([190, 100, 60], np.float32)
    dark = np.array([95, 55, 40], np.float32)
    rgb = rust + (dark - rust) * dark_regions[..., None] * 0.8
    rgb *= (0.85 + 0.3 * fine[..., None])
    # polar caps
    lat = np.abs((0.5 - np.arange(h) / h) * 180)
    cap = np.clip((lat - 80) / 6, 0, 1)[:, None, None]
    rgb = rgb * (1 - cap) + 240 * cap
    img = np.clip(rgb, 0, 255).astype(np.uint8)
    Image.fromarray(img).save(HERE / "MarsTexture.jpg", quality=92)
    Image.fromarray((img * 0.1).astype(np.uint8)).save(HERE / "DarkMarsTexture.jpg", quality=92)


# Galactic north pole (J2000) to place the Milky Way on an equatorial coordinate map
_NGP_RA, _NGP_DEC = math.radians(192.859), math.radians(27.128)


def galactic_lb(ra, dec):
    sin_b = np.sin(dec) * math.sin(_NGP_DEC) + np.cos(dec) * math.cos(_NGP_DEC) * np.cos(ra - _NGP_RA)
    b = np.arcsin(np.clip(sin_b, -1, 1))
    y = np.cos(dec) * np.sin(ra - _NGP_RA)
    x = np.sin(dec) * math.cos(_NGP_DEC) - np.cos(dec) * math.sin(_NGP_DEC) * np.cos(ra - _NGP_RA)
    l = math.radians(122.932) - np.arctan2(y, x)
    return np.mod(l + math.pi, 2 * math.pi) - math.pi, b


def make_sky(W=8192, H=4096, seed=3):
    rng = np.random.default_rng(seed)
    # --- Milky Way band at half resolution
    w, h = W // 2, H // 2
    ra = (np.arange(w) / w) * 2 * math.pi
    dec = (0.5 - (np.arange(h) + 0.5) / h) * math.pi
    RA, DEC = np.meshgrid(ra, dec)
    l, b = galactic_lb(RA, DEC)
    noise = periodic_noise((h, w), 1.8, rng)
    fine = periodic_noise((h, w), 1.0, rng)
    band = np.exp(-(b / math.radians(9)) ** 2) * (0.35 + 0.65 * np.exp(-(l / math.radians(70)) ** 2))
    cloud = bandpass_noise((h, w), 40, rng)
    glow = band * (0.30 + 0.9 * noise) * (0.55 + 0.9 * cloud)
    dust = np.exp(-(b / math.radians(2.5)) ** 2) * np.clip((periodic_noise((h, w), 2.0, rng) - 0.45) * 3, 0, 1)
    glow = np.clip(glow * (1 - 0.7 * dust) * (0.8 + 0.4 * fine), 0, 1.5)
    tint = np.array([0.86, 0.90, 1.0], np.float32)
    mw = np.clip(glow[..., None] * tint * 135, 0, 255).astype(np.uint8)
    mw_img = Image.fromarray(mw).resize((W, H), Image.BICUBIC)
    sky = np.asarray(mw_img).astype(np.float32)

    # --- stars: extra density near the galactic plane
    def sample(n, band_weight):
        out = []
        while len(out) < n:
            k = n * 2
            u = rng.uniform(-1, 1, k)
            d = np.arcsin(u)
            r = rng.uniform(0, 2 * math.pi, k)
            _, bb = galactic_lb(r, d)
            p = 0.25 + band_weight * np.exp(-(bb / math.radians(14)) ** 2)
            keep = rng.uniform(0, 1, k) < p
            out.extend(zip(r[keep], d[keep]))
        return out[:n]

    stars = []
    for n, band_w, rad, amp in [(60000, 3.0, 0.0, 70), (12000, 1.5, 0.0, 150), (1800, 0.5, 1.0, 230), (260, 0.3, 1.8, 255), (24, 0.1, 3.2, 255)]:
        for (r, d) in sample(n, band_w):
            stars.append((r, d, rad, amp * rng.uniform(0.6, 1.0)))
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(layer)
    bright_list = []
    for r, d, rad, amp in stars:
        x = r / (2 * math.pi) * W
        y = (0.5 - d / math.pi) * H
        stretch = 1 / max(math.cos(d), 0.15)
        t = rng.uniform(0, 1)
        col = np.array([1.0, 0.95, 0.9]) if t < 0.6 else (np.array([0.75, 0.85, 1.0]) if t < 0.8 else np.array([1.0, 0.8, 0.6]))
        c = tuple(int(min(255, amp * v)) for v in col)
        rx, ry = max(0.6, rad) * min(stretch, 6), max(0.6, rad)
        draw.ellipse([x - rx, y - ry, x + rx, y + ry], fill=c)
        if rad >= 1.8:
            bright_list.append((r, d, amp))
    layer = layer.filter(ImageFilter.GaussianBlur(0.7))
    out = np.clip(sky + np.asarray(layer).astype(np.float32), 0, 255).astype(np.uint8)
    Image.fromarray(out).save(HERE / "hiptyc_2020_8k.jpg", quality=90)
    return bright_list


def make_constellations(bright_list, W=4096, H=2048, seed=9):
    """Constellation figures: groups nearby bright stars and joins them with lines."""
    rng = np.random.default_rng(seed)
    pts = np.array([(r, d) for r, d, _ in bright_list])
    used = np.zeros(len(pts), bool)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    def ang_dist(a, b):
        return math.acos(np.clip(math.sin(a[1]) * math.sin(b[1]) + math.cos(a[1]) * math.cos(b[1]) * math.cos(a[0] - b[0]), -1, 1))

    def to_xy(p):
        return (p[0] / (2 * math.pi) * W, (0.5 - p[1] / math.pi) * H)

    for i in rng.permutation(len(pts)):
        if used[i]:
            continue
        group = [i]
        used[i] = True
        for _ in range(rng.integers(3, 7)):
            cands = [j for j in range(len(pts)) if not used[j] and ang_dist(pts[group[-1]], pts[j]) < math.radians(14)]
            if not cands:
                break
            j = min(cands, key=lambda j: ang_dist(pts[group[-1]], pts[j]))
            used[j] = True
            group.append(j)
        if len(group) >= 3:
            for a, b in zip(group, group[1:]):
                xa, ya = to_xy(pts[a])
                xb, yb = to_xy(pts[b])
                if abs(xa - xb) < W / 2:
                    draw.line([xa, ya, xb, yb], fill=(255, 255, 255, 255), width=2)
    img.save(HERE / "constellation_figures.png")


# ------------------------------------------------------------------ data
def make_hyg(n=70000, seed=2):
    """Synthetic star catalog with HYG-style columns; what matters: absmag and ci (B-V index)."""
    rng = np.random.default_rng(seed)
    n_ms, n_giant, n_wd, n_sg = int(n * 0.84), int(n * 0.10), int(n * 0.04), int(n * 0.02)
    # Main sequence: more cool stars than hot ones
    ci_ms = np.clip(rng.gamma(2.4, 0.33, n_ms) - 0.2, -0.3, 2.0)
    ms_ci = [-0.3, 0.0, 0.3, 0.65, 1.0, 1.4, 1.8, 2.1]       # color - absolute magnitude relation of the main sequence
    ms_mag = [-4.0, 0.8, 2.7, 4.8, 6.5, 9.5, 13.5, 15.5]
    absmag_ms = np.interp(ci_ms, ms_ci, ms_mag) + rng.normal(0, 0.6, n_ms)
    # Red giants
    ci_g = rng.normal(1.25, 0.28, n_giant).clip(0.7, 2.0)
    absmag_g = rng.normal(0.3, 1.0, n_giant) - 0.6 * (ci_g - 1.2)
    # Supergiants
    ci_s = rng.normal(0.8, 0.9, n_sg).clip(-0.3, 2.0)
    absmag_s = rng.normal(-5.5, 1.3, n_sg)
    # White dwarfs
    ci_w = rng.normal(0.15, 0.25, n_wd).clip(-0.3, 0.9)
    absmag_w = rng.normal(11.5, 1.2, n_wd) + 2.0 * (ci_w - 0.15)
    ci = np.concatenate([ci_ms, ci_g, ci_s, ci_w])
    absmag = np.concatenate([absmag_ms, absmag_g, absmag_s, absmag_w])
    # Distances in pc (roughly uniform volume out to 500 pc) and apparent magnitude
    dist = 500 * rng.uniform(0, 1, len(ci)) ** (1 / 3) + 1
    mag = absmag + 5 * np.log10(dist / 10)
    lum = 10 ** (-0.4 * (absmag - 4.83))
    order = rng.permutation(len(ci))
    ci, absmag, dist, mag, lum = ci[order], absmag[order], dist[order], mag[order], lum[order]
    spect = np.array(list("OBAFGKM"))[np.digitize(ci, [-0.15, 0.0, 0.3, 0.58, 0.81, 1.4])]
    # Some missing ci values, as in the real HYG
    ci_str = [("" if rng.random() < 0.01 else f"{v:.3f}") for v in ci]
    path = HERE / "Data"
    path.mkdir(exist_ok=True)
    with gzip.open(path / "HYG_Data.gz", "wt") as f:
        f.write("id,proper,dist,mag,absmag,spect,ci,lum\n")
        for i in range(len(ci)):
            f.write(f"{i + 1},,{dist[i]:.2f},{mag[i]:.3f},{absmag[i]:.3f},{spect[i]},{ci_str[i]},{lum[i]:.4g}\n")


def planck(wl_nm, T):
    wl = wl_nm * 1e-9
    h, c, k = 6.62607015e-34, 2.99792458e8, 1.380649e-23
    return 2 * h * c**2 / wl**5 / (np.exp(h * c / (wl * k * T)) - 1)


def make_solar_spectrum(seed=4):
    """wavelength_nm, extraterrestrial, global (with atmosphere), direct; 1 nm step between 280 and 2500 nm."""
    rng = np.random.default_rng(seed)
    wl = np.arange(280, 2501, 1.0)
    et = planck(wl, 5778)
    et = et / et.max() * 1.95                                      # W m^-2 nm^-1 (peak ~ 1.95 near 500 nm)
    # Fraunhofer lines: (wavelength nm, depth, width nm)
    lines = [(393.4, 0.75, 1.3), (396.8, 0.70, 1.2), (410.2, 0.35, 1.0), (430.8, 0.30, 1.0), (434.0, 0.35, 0.9), (438.4, 0.25, 0.5),
             (466.8, 0.15, 0.4), (486.1, 0.40, 1.0), (516.7, 0.30, 0.4), (517.3, 0.35, 0.4), (518.4, 0.35, 0.4), (527.0, 0.25, 0.4),
             (532.8, 0.15, 0.3), (589.0, 0.50, 0.35), (589.6, 0.45, 0.35), (656.3, 0.60, 1.2), (766.5, 0.30, 0.4), (769.9, 0.25, 0.4),
             (849.8, 0.30, 0.8), (854.2, 0.40, 0.9), (866.2, 0.30, 0.8), (1083.0, 0.25, 0.6), (1282.0, 0.15, 0.8), (1875.0, 0.1, 1.5), (2166.0, 0.10, 1.0)]
    for _ in range(260):                                           # many weak lines
        lines.append((rng.uniform(300, 2200), rng.uniform(0.03, 0.18), rng.uniform(0.15, 0.5)))
    absorb = np.ones_like(wl)
    for c, depth, width in lines:
        absorb *= 1 - depth * np.exp(-0.5 * ((wl - c) / (width / 2.355)) ** 2) * 0 - depth * np.exp(-0.5 * ((wl - c) / width) ** 2)
    et = et * absorb
    # Atmosphere: Rayleigh scattering + O2, H2O, CO2 bands
    tau = 0.0088 * (wl / 1000) ** -4.05 * 1.15
    bands = [(687, 8, 0.35), (760, 10, 0.9), (720, 12, 0.25), (820, 15, 0.35), (940, 30, 0.9), (1130, 40, 0.9), (1380, 60, 3.0), (1600, 25, 0.25),
             (1870, 80, 3.0), (2000, 25, 0.8), (2060, 20, 0.7), (2300, 100, 0.5)]
    for c, width, strength in bands:
        tau = tau + strength * np.exp(-0.5 * ((wl - c) / width) ** 2)
    tau = tau + 0.06 * np.exp(-(wl - 280) / 40) * 12                # ozone / UV
    direct = et * np.exp(-tau * 1.5)
    glob = et * np.exp(-tau * 1.5) * 1.08 + 0.10 * et * (1 - np.exp(-tau))
    data = np.stack([wl, et, glob, direct], axis=1)
    path = HERE / "Data"
    path.mkdir(exist_ok=True)
    np.savetxt(path / "solar_spectrum.csv", data, delimiter=",", fmt=["%.1f", "%.5f", "%.5f", "%.5f"])


def make_galactic_data(n=420000, seed=7):
    """SDSS-like galaxies: ra/dec in a cone, distribution in filaments, z = H0 d / c with peculiar velocities."""
    rng = np.random.default_rng(seed)
    H0, c = 70.0, 299792.458
    ra_min, ra_max, dec_min, dec_max = 110.0, 260.0, -3.0, 65.0
    rows = []
    # filament seeds: random 3D segments in the cone; the galaxies are spread along them with dispersion
    max_d = 520.0
    nodes = []
    for _ in range(90):
        d = max_d * rng.uniform(0.15, 1) ** 0.6
        ra = rng.uniform(ra_min, ra_max)
        dec = math.degrees(math.asin(rng.uniform(math.sin(math.radians(dec_min)), math.sin(math.radians(dec_max)))))
        nodes.append((ra, dec, d))

    def to_xyz(ra, dec, d):
        r, de = math.radians(ra), math.radians(dec)
        return np.array([d * math.cos(de) * math.cos(r), d * math.cos(de) * math.sin(r), d * math.sin(de)])

    def from_xyz(p):
        d = np.linalg.norm(p, axis=-1)
        ra = np.degrees(np.arctan2(p[..., 1], p[..., 0])) % 360
        dec = np.degrees(np.arcsin(p[..., 2] / d))
        return ra, dec, d

    pts = []
    xyz_nodes = [to_xyz(*nd) for nd in nodes]
    per_fil = n // 90
    for _ in range(170):
        a, b = rng.choice(len(nodes), 2, replace=False)
        pa, pb = xyz_nodes[a], xyz_nodes[b]
        if np.linalg.norm(pa - pb) > 220:
            continue
        t = rng.uniform(0, 1, per_fil)
        base = pa[None] + t[:, None] * (pb - pa)[None]
        pts.append(base + rng.normal(0, 7, (per_fil, 3)))
    for pa in xyz_nodes:                                                # clusters at the nodes
        k = per_fil // 2
        pts.append(pa[None] + rng.normal(0, 9, (k, 3)))
    pts = np.concatenate(pts)
    rng.shuffle(pts)
    # diffuse field
    k = n // 4
    d = max_d * rng.uniform(0, 1, k) ** (1 / 3)
    ra = rng.uniform(ra_min, ra_max, k)
    dec = np.degrees(np.arcsin(rng.uniform(math.sin(math.radians(dec_min)), math.sin(math.radians(dec_max)), k)))
    field = np.array([to_xyz(a, b, dd) for a, b, dd in zip(ra, dec, d)])
    pts = np.concatenate([pts, field])
    ra, dec, dist = from_xyz(pts)
    keep = (ra >= ra_min) & (ra <= ra_max) & (dec >= dec_min) & (dec <= dec_max) & (dist > 20) & (dist < max_d)
    # selection function: decreases with distance (like a magnitude-limited catalog)
    keep &= rng.uniform(0, 1, len(dist)) < np.exp(-(dist / 330.0) ** 2) * 0.9 + 0.1
    ra, dec, dist = ra[keep][:n], dec[keep][:n], dist[keep][:n]
    z = (H0 * dist + rng.normal(0, 300, len(dist))) / c                # Hubble's law + peculiar velocities
    obj = 1237645000000000000 + np.arange(len(dist)) * 37
    path = HERE / "Data"
    path.mkdir(exist_ok=True)
    with open(path / "galactic_data.csv", "w") as f:
        f.write("# Datos sinteticos de relleno (el original, de Grant, era un recorte de un relevamiento tipo SDSS): filamentos + ley de Hubble con H0 = 70 km/s/Mpc\n")
        f.write("objID,ra,dec,redshift,distance_mpc\n")
        for i in range(len(dist)):
            f.write(f"{obj[i]},{ra[i]:.4f},{dec[i]:.4f},{z[i]:.5f},{dist[i]:.2f}\n")


def install_named():
    """Copies to _lib/assets/raster_images and svg_images the assets that the code looks for by name (without a path)."""
    import shutil
    raster, svg = LIB / "raster_images", LIB / "svg_images"
    names = ["MoonTexture.jpg", "DarkMoonTexture.jpg", "RedMoonTexture.jpg", "SunTexture.jpg", "MarsTexture.jpg", "DarkMarsTexture.jpg",
             "hiptyc_2020_8k.jpg", "constellation_figures.png"]
    for n in names:
        shutil.copy2(HERE / n, raster / n)
    for f in sorted((HERE / "names").glob("*.png")):
        shutil.copy2(f, raster / f.name)
    for f in sorted((HERE / "svg").glob("*.svg")):
        shutil.copy2(f, svg / f.name)


def main(what="all"):
    if what in ("textures", "all"):
        make_moon_textures()
        make_sun_texture()
        make_mars_textures()
        bright = make_sky()
        make_constellations(bright)
    if what in ("data", "all"):
        make_hyg()
        make_solar_spectrum()
        make_galactic_data()
    if what in ("images", "all"):
        try:
            from make_cosmic_distance_images import make_all   # placeholder images (more are added below)
            make_all()
        except ImportError:
            pass
    if what in ("install", "all"):
        install_named()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "all")
