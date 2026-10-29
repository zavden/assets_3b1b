"""Placeholders that were created with _tools/placeholder.py from the command line (without a script of their own). This file recreates them so that _tools/setup_assets.py is reproducible.
They are own placeholder images: a box with the file's name, nothing more."""
import shutil
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ASSETS.parents[1] / "_tools"))
from placeholder import make_image, make_page

# (path inside _lib/assets, label, size, background color)
IMAGES = [
    ("generated/2025/grover/Comments/comment_1.png", "comment 1", "900x260", "#2a2f3a"),
    ("generated/2025/grover/Comments/comment_2.png", "comment 2", "900x260", "#2a2f3a"),
    ("generated/2025/grover/Comments/comment_3.png", "comment 3", "900x260", "#2a2f3a"),
    ("generated/2025/grover/Comments/comment_4.png", "comment 4", "900x260", "#2a2f3a"),
    ("generated/2025/grover/Comments/comment_5.png", "comment 5", "900x260", "#2a2f3a"),
    ("generated/2025/grover/Comments/comment_6.png", "comment 6", "900x260", "#2a2f3a"),
    ("generated/2025/guest_videos/Aleph0Banner.png", "Aleph0Banner", "1920x480", "#3a2b55"),
    ("generated/2025/guest_videos/WelchLabsBanner.png", "WelchLabsBanner", "1920x480", "#2b3a55"),
    ("generated/2025/guest_videos/alpha_geometry_TN.png", "alpha geometry TN", "1280x720", "#3a2b55"),
    ("generated/2025/guest_videos/diffusion_TN.png", "diffusion TN", "1280x720", "#2b3a55"),
    ("generated/2025/guest_videos/euclid_TN.png", "euclid TN", "1280x720", "#552b3a"),
    ("generated/2025/guest_videos/incomplete_cubes_TN.png", "incomplete cubes TN", "1280x720", "#55482b"),
    ("generated/2025/guest_videos/phase_change_TN.png", "phase change TN", "1280x720", "#2b5548"),
    ("generated/2025/guest_videos/vilas_winstein.png", "vilas winstein", "1920x480", "#2b5548"),
    ("raster_images/AI Evolution Timeline images/alphago.png", "alphago", "900x600", "#2b3a4a"),
    ("raster_images/AI Evolution Timeline images/deepmind_2024.jpg", "deepmind 2024", "960x540", "#4a3a2b"),
    ("raster_images/AI Evolution Timeline images/dota.png", "dota", "960x540", "#3a2b4a"),
    ("raster_images/AI Evolution Timeline images/erdos_problems.png", "erdos problems", "1200x600", "#333344"),
    ("raster_images/AI Evolution Timeline images/fel.png", "fel", "1200x600", "#333344"),
    ("raster_images/AI Evolution Timeline images/gpt.png", "gpt", "800x600", "#2b4a3a"),
    ("raster_images/AI Evolution Timeline images/jacobian.png", "jacobian", "1200x600", "#333344"),
    ("raster_images/AI Evolution Timeline images/multiple_models_win_gold.png", "multiple models win gold", "960x540", "#4a2b3a"),
    ("raster_images/AI Evolution Timeline images/navier-stokes.png", "navier stokes", "1200x600", "#333344"),
    ("raster_images/AI Evolution Timeline images/non-sofic_group.png", "non sofic group", "1200x600", "#333344"),
    ("raster_images/AI Evolution Timeline images/sedol.jpg", "sedol", "800x1000", "#2b4b4a"),
    ("raster_images/AI Evolution Timeline images/unit_distance.png", "unit distance", "1200x600", "#333344"),
    ("raster_images/Dalle3_blue_1.png", "Dalle3 blue 1", "1000x1000", "#26405a"),
    ("raster_images/EiffelTower1.png", "EiffelTower1", "900x1200", "#36384a"),
    ("raster_images/IMG-9874.png", "IMG 9874", "900x1200", "#44363a"),
    ("raster_images/PiCreatureDalle3_13.png", "PiCreatureDalle3 13", "1000x1000", "#2f4552"),
    ("raster_images/PixarCampus.png", "PixarCampus", "1400x900", "#2f4535"),
    ("raster_images/ShrewMole.png", "ShrewMole", "1200x900", "#3a3a3a"),
    ("raster_images/TeddyHead.png", "TeddyHead", "1920x1080", "#4a3a2b"),
    ("raster_images/TerryTaoPaulErdos.png", "TerryTaoPaulErdos", "1200x900", "#3d3a30"),
    ("raster_images/US_color_graph.png", "US color graph", "1200x800", "#2f3a45"),
]
# Banners and thumbnails of guest_videos: the code looks them up by name in raster_images/
GUEST_COPIES = ['Aleph0Banner.png', 'WelchLabsBanner.png', 'alpha_geometry_TN.png', 'diffusion_TN.png', 'euclid_TN.png', 'incomplete_cubes_TN.png', 'phase_change_TN.png', 'vilas_winstein.png']


def main():
    for rel, label, size, bg in IMAGES:
        out = ASSETS / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        w, h = map(int, size.split("x"))
        make_image(out, label, (w, h), bg)
    for name in GUEST_COPIES:
        shutil.copy2(ASSETS / "generated/2025/guest_videos" / name, ASSETS / "raster_images" / name)
    # Pages of the IMO 2025 exam (2026/2025_p6, ProblemIntro scene)
    pages = ASSETS / "generated/2026/2025_p6"
    pages.mkdir(parents=True, exist_ok=True)
    make_page(pages / "IMO-2025-problems-eng-1.png", "IMO 2025 · Problems (p. 1)", 38, 1)
    make_page(pages / "IMO-2025-problems-eng-2.png", "IMO 2025 · Problems (p. 2)", 16, 2)


if __name__ == "__main__":
    main()
