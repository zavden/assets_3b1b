"""Own replacement of the 16 screenshots that lost_lecture::ShowFullStory tiles on screen.

Grant's scene loads `<MEDIA_DIR>/animations/active_projects/lost_lecture/images/<Name>.png`: last frames of the scenes of
that video, kept on his disk (never in the repo). They are regenerated here from OUR renders of the same scenes
(`converted/renders/2018/lost_lecture/<Scene>.mp4|.png`, last frame). A scene with no render (or that is not a scene of
this video) gets a plain dark frame with its name, drawn with PIL. Nothing is copied from Grant's files.

  python make_fullstory_frames.py [--out DIR]   (default: _lib/assets/raster_images/)
"""
import argparse
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

ASSETS = Path(__file__).resolve().parents[3]            # .../converted/_lib/assets
RENDERS = ASSETS.parents[1] / "renders" / "2018" / "lost_lecture"
# image name used by ShowFullStory -> scene whose render stands in for it
NAMES = {
    "ShowEmergingEllipse": "ShowEmergingEllipse",
    "ShowFullStory": None,
    "FeynmanFameStart": "FeynmanFame",
    "TheMotionOfPlanets": "TheMotionOfPlanets",
    "FeynmanElementaryQuote": "FeynmanElementaryQuote",
    "DrawingEllipse": "DrawEllipseOverlay",
    "ShowEllipseDefiningProperty": "ShowEllipseDefiningProperty",
    "ProveEllipse": "ProveEllipse",
    "KeplersSecondLaw": "KeplersSecondLaw",
    "AngularMomentumArgument": "AngularMomentumArgument",
    "HistoryOfAngularMomentum": "HistoryOfAngularMomentum",
    "FeynmanRecountingNewton": "FeynmanRecountingNewton",
    "IntroduceShapeOfVelocities": "IntroduceShapeOfVelocities",
    "ShowEqualAngleSlices": "ShowEqualAngleSlices",
    "PonderOverOffCenterDiagram": "PonderOverOffCenterDiagram",
    "UseVelocityDiagramToDeduceCurve": "UseVelocityDiagramToDeduceCurve",
}
SIZE = (1280, 720)


def last_frame(scene, dest):
    mp4, png = RENDERS / f"{scene}.mp4", RENDERS / f"{scene}.png"
    if mp4.exists():
        r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-sseof", "-0.2", "-i", str(mp4), "-frames:v", "1", str(dest)])
        return r.returncode == 0 and dest.exists()
    if png.exists():
        Image.open(png).convert("RGB").save(dest)
        return True
    return False


def placeholder(name, dest):
    img = Image.new("RGB", SIZE, (20, 20, 20))
    d = ImageDraw.Draw(img)
    d.text((SIZE[0] // 2 - 4 * len(name), SIZE[1] // 2), name, fill=(200, 200, 200))
    img.save(dest)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ASSETS / "raster_images")
    out = ap.parse_args().out
    out.mkdir(parents=True, exist_ok=True)
    for name, scene in NAMES.items():
        dest = out / f"{name}.png"
        if not (scene and last_frame(scene, dest)):
            placeholder(name, dest)
            print("placeholder:", name)
        else:
            print("frame:", name, "<-", scene)


if __name__ == "__main__":
    main()
