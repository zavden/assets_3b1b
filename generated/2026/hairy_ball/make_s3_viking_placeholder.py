"""Generates a placeholder 3D model (small airplane) to replace `s3_viking/s3.obj`, the model of the
Lockheed S-3 Viking that lived in Grant's Dropbox (hairy_ball/model3d.py::OrientAModel).

Writes to _lib/assets/models/s3_viking/: s3.obj, texture.png
Convention of the original model (the one S3Viking assumes in model3d.py): in the raw OBJ the
nose points to -x, "up" is +y and the wings go along z. S3Viking rotates it so that
the nose ends up at +x, the wings at y and up at z.

Usage: python make_s3_viking_placeholder.py"""
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parents[3] / "models" / "s3_viking"
OUT.mkdir(parents=True, exist_ok=True)


def box(extents, center):
    m = trimesh.creation.box(extents=extents)
    m.apply_translation(center)
    return m


# Fuselage: cylinder along x, with a cone at the nose (-x)
fus_r, fus_len = 0.18, 2.4
fuselage = trimesh.creation.cylinder(radius=fus_r, height=fus_len, sections=24)
fuselage.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))  # z axis -> x axis
nose = trimesh.creation.cone(radius=fus_r, height=0.7, sections=24)
nose.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))      # tip toward +x
nose.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [0, 1, 0]))          # tip toward -x
nose.apply_translation([-fus_len / 2 - 0.35 + 0.0, 0, 0])
# Wings (along z), vertical tail (y) and horizontal stabilizer (z)
wings = box([0.7, 0.05, 3.2], [0.1, -0.02, 0])
fin = box([0.55, 0.7, 0.05], [fus_len / 2 - 0.2, 0.4, 0])
stab = box([0.35, 0.04, 1.1], [fus_len / 2 - 0.1, 0.05, 0])
# Two engines under the wings
eng1 = trimesh.creation.cylinder(radius=0.09, height=0.7, sections=16)
eng1.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
eng2 = eng1.copy()
eng1.apply_translation([-0.1, -0.15, 0.7])
eng2.apply_translation([-0.1, -0.15, -0.7])

plane = trimesh.util.concatenate([fuselage, nose, wings, fin, stab, eng1, eng2])
v = plane.vertices
# UV: flat projection onto the (x, z) plane, with a texture that distinguishes the two wings
u = (v[:, 0] - v[:, 0].min()) / np.ptp(v[:, 0])
w = (v[:, 2] - v[:, 2].min()) / np.ptp(v[:, 2])
uv = np.stack([u, w], axis=1)

# Texture: bluish gray, left wing (z<0) red and right (z>0) green at the tips, central stripe
S = 512
img = Image.new("RGB", (S, S), (150, 160, 175))
d = ImageDraw.Draw(img)
d.rectangle([0, 0, S, int(S * 0.18)], fill=(200, 60, 60))
d.rectangle([0, int(S * 0.82), S, S], fill=(60, 170, 90))
d.rectangle([0, int(S * 0.46), S, int(S * 0.54)], fill=(235, 235, 235))
for x in range(0, S, 64):
    d.line([x, 0, x, S], fill=(130, 140, 155), width=2)
img.save(OUT / "texture.png")

# Hand-written OBJ (with texture coordinates), a single object
with open(OUT / "s3.obj", "w") as f:
    f.write("# Modelo de relleno (avioncito) generado por make_s3_viking_placeholder.py\n")
    for p in plane.vertices:
        f.write(f"v {p[0]:.5f} {p[1]:.5f} {p[2]:.5f}\n")
    for t in uv:
        f.write(f"vt {t[0]:.5f} {t[1]:.5f}\n")
    for tri in plane.faces + 1:
        f.write("f " + " ".join(f"{i}/{i}" for i in tri) + "\n")
print("ok", OUT, len(plane.vertices), "vértices", len(plane.faces), "caras")
