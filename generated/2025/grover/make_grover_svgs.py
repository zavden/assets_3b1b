"""Generates the missing SVGs for the _2025/grover scenes (they lived in Grant's Dropbox) and
writes them to _lib/assets/svg_images/.

  and_gate, or_gate, not_gate      ANSI logic gates (placeholder) with their terminals
  Four_bit_adder_with_carry_lookahead
                                   diagram of a 4-bit carry-lookahead adder: gates and wires
                                   (strokes only, as used in the scenes)
  BitCircuit                       one-bit circuit: wire with a switch and two terminals (the last two
                                   submobjects are the dots, the code fills them)
  channel_support_QR_code          real QR (segno) of "3b1b.co/support": one square per data module and, at the
                                   end, 6 pieces of the 3 position eyes (ring and center), as the code indexes
  sudoku_example                   classic sudoku: 81 cells, 9 boxes, outer border and the digits as outlines
  light_switch                     light switch (plate, slot and lever)

Not generated (copied from assets the repo already ships): computer_chip <- gpu.svg,
magnifying_glass2 <- magnifying_glass.svg, BinaryFunctionCircuit <- circuit.svg.

Usage: python make_grover_svgs.py"""
import math
import random
import shutil
from pathlib import Path

OUT = Path(__file__).resolve().parents[3] / "svg_images"
K = 0.5523  # constant for approximating circles with cubics


def fmt(v):
    return f"{v:.4f}".rstrip("0").rstrip(".")


def pts(*coords):
    return " ".join(fmt(c) for c in coords)


def svg_doc(paths, width, height, margin=0.2):
    vb = f"{fmt(-margin)} {fmt(-margin)} {fmt(width + 2 * margin)} {fmt(height + 2 * margin)}"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" '
        f'width="{fmt((width + 2 * margin) * 100)}" height="{fmt((height + 2 * margin) * 100)}">\n'
        + "\n".join(paths) + "\n</svg>\n"
    )


def path(d, fill="#000000", stroke="none", sw=0.03):
    if stroke == "none":
        return f'<path fill="{fill}" stroke="none" d="{d}"/>'
    return f'<path fill="{fill}" stroke="{stroke}" stroke-width="{fmt(sw)}" d="{d}"/>'


def rect_d(x, y, w, h):
    return f"M {pts(x, y)} L {pts(x + w, y)} L {pts(x + w, y + h)} L {pts(x, y + h)} Z"


def circle_d(cx, cy, r, reverse=False):
    k = K * r
    if not reverse:
        return (f"M {pts(cx + r, cy)} C {pts(cx + r, cy + k, cx + k, cy + r, cx, cy + r)} "
                f"C {pts(cx - k, cy + r, cx - r, cy + k, cx - r, cy)} "
                f"C {pts(cx - r, cy - k, cx - k, cy - r, cx, cy - r)} "
                f"C {pts(cx + k, cy - r, cx + r, cy - k, cx + r, cy)} Z")
    return (f"M {pts(cx + r, cy)} C {pts(cx + r, cy - k, cx + k, cy - r, cx, cy - r)} "
            f"C {pts(cx - k, cy - r, cx - r, cy - k, cx - r, cy)} "
            f"C {pts(cx - r, cy + k, cx - k, cy + r, cx, cy + r)} "
            f"C {pts(cx + k, cy + r, cx + r, cy + k, cx + r, cy)} Z")


# ---------------------------------------------------------------- gates

def gate_body(kind, x, y, h, w=1.0):
    """Bodies (list of d) of a gate with upper left corner (x, y), height h and width w."""
    if kind == "and":
        rx, ry = 0.5 * w, 0.5 * h
        return [(f"M {pts(x, y)} L {pts(x + w - rx, y)} "
                 f"C {pts(x + w - rx + K * rx, y, x + w, y + ry - K * ry, x + w, y + ry)} "
                 f"C {pts(x + w, y + ry + K * ry, x + w - rx + K * rx, y + h, x + w - rx, y + h)} "
                 f"L {pts(x, y + h)} Z")]
    if kind in ("or", "xor"):
        body = (f"M {pts(x, y)} C {pts(x + .35 * w, y, x + .7 * w, y + .12 * h, x + w, y + h / 2)} "
                f"C {pts(x + .7 * w, y + .88 * h, x + .35 * w, y + h, x, y + h)} "
                f"C {pts(x + .25 * w, y + .7 * h, x + .25 * w, y + .3 * h, x, y)} Z")
        if kind == "or":
            return [body]
        e = 0.14 * w
        crescent = (f"M {pts(x - e, y)} C {pts(x - e + .25 * w, y + .3 * h, x - e + .25 * w, y + .7 * h, x - e, y + h)} "
                    f"L {pts(x - e + .04, y + h)} C {pts(x - e + .29 * w, y + .7 * h, x - e + .29 * w, y + .3 * h, x - e + .04, y)} Z")
        return [body, crescent]
    if kind == "not":
        tip = x + 0.8 * w
        r = 0.08 * h / 0.8 if h < 0.8 else 0.08
        return [f"M {pts(x, y)} L {pts(tip, y + h / 2)} L {pts(x, y + h)} Z",
                circle_d(tip + r, y + h / 2, r)]
    raise ValueError(kind)


def gate_geometry(kind, n_inputs=2):
    """(height, total width of the body including bubble, relative output x)"""
    if kind == "not":
        return 0.8, 1.0, 0.8 + 0.16
    return max(0.8, 0.4 * n_inputs), 1.0, 1.0


def gate_pins(kind, x, y, n_inputs):
    h, w, out_dx = gate_geometry(kind, n_inputs)
    n = 1 if kind == "not" else n_inputs
    ins = [(x + (0.0 if kind != "or" and kind != "xor" else 0.1 * w), y + (i + 0.5) * h / n) for i in range(n)]
    out = (x + out_dx, y + h / 2)
    return ins, out


def lead_rects(ins, out, lead=0.4, t=0.04):
    """Terminals as thin rectangles (so that they are visible with fill only)."""
    d = []
    for (px, py) in ins:
        d.append(rect_d(px - lead, py - t / 2, lead, t))
    d.append(rect_d(out[0], out[1] - t / 2, lead, t))
    return d


def make_gate_svg(kind):
    h, w, _ = gate_geometry(kind, 2)
    n = 1 if kind == "not" else 2
    ins, out = gate_pins(kind, 0, 0, n)
    paths = [path(d) for d in gate_body(kind, 0, 0, h, w)]
    paths += [path(d) for d in lead_rects(ins, out)]
    return svg_doc(paths, w + 0.8, h)


# ---------------------------------------------------------------- 4-bit adder

def make_adder():
    """Diagram of a 4-bit carry-lookahead adder, in "bus" style:
    each signal has a horizontal track; the gates are stacked in columns."""
    wires, bodies = [], []
    track_step = 0.42
    tracks = {}
    names = ["C0"] + [f"{c}{i}" for i in range(4) for c in "AB"] + \
            [f"{c}{i}" for i in range(4) for c in "PG"] + ["C1", "C2", "C3", "C4"]
    for j, name in enumerate(names):
        tracks[name] = 0.0 + j * track_step
    # sums (outputs)
    for i in range(4):
        tracks[f"S{i}"] = (len(names) + i) * track_step

    # columns: starting x of each column of gates
    col_x = {1: 3.0, 2: 6.6, 3: 10.4, 4: 14.2, 5: 18.0}
    next_y = {c: 0.0 for c in col_x}

    gates = []  # (kind, col, inputs, output)
    for i in range(4):
        gates.append(("xor", 1, [f"A{i}", f"B{i}"], f"P{i}"))
        gates.append(("and", 1, [f"A{i}", f"B{i}"], f"G{i}"))
    # carry lookahead
    gates += [
        ("and", 2, ["P0", "C0"], "t10"), ("or", 3, ["G0", "t10"], "C1"),
        ("and", 2, ["P1", "G0"], "t21"), ("and", 2, ["P1", "P0", "C0"], "t20"), ("or", 3, ["G1", "t21", "t20"], "C2"),
        ("and", 2, ["P2", "G1"], "t32"), ("and", 2, ["P2", "P1", "G0"], "t31"),
        ("and", 2, ["P2", "P1", "P0", "C0"], "t30"), ("or", 3, ["G2", "t32", "t31", "t30"], "C3"),
        ("and", 2, ["P3", "G2"], "t43"), ("and", 2, ["P3", "P2", "G1"], "t42"),
        ("and", 2, ["P3", "P2", "P1", "G0"], "t41"), ("and", 2, ["P3", "P2", "P1", "P0", "C0"], "t40"),
        ("or", 3, ["G3", "t43", "t42", "t41", "t40"], "C4"),
    ]
    # sums
    for i, src in enumerate(["C0", "C1", "C2", "C3"]):
        gates.append(("xor", 4, [f"P{i}", src], f"S{i}"))

    # temporaries: one track per intermediate signal
    extra = [g[3] for g in gates if g[3].startswith("t")]
    for j, name in enumerate(extra):
        tracks[name] = (len(names) + 4 + j) * track_step

    # gate positions (stacked in their column, in order)
    placed = []
    for kind, col, inputs, output in gates:
        h, w, _ = gate_geometry(kind, len(inputs))
        y = next_y[col]
        next_y[col] += h + 0.35
        placed.append((kind, col_x[col], y, inputs, output))

    # bodies and pins
    producer = {}  # signal -> (output pin)
    consumers = {}  # signal -> [(input pin)]
    for kind, x, y, inputs, output in placed:
        ins, out = gate_pins(kind, x, y, len(inputs))
        h, w, _ = gate_geometry(kind, len(inputs))
        for d in gate_body(kind, x, y, h, w):
            bodies.append(path(d, fill="none", stroke="#000000"))
        producer[output] = out
        for sig, pin in zip(inputs, ins):
            consumers.setdefault(sig, []).append(pin)

    # cables
    lane = [0]
    def next_lane():
        lane[0] += 1
        return 0.07 * (lane[0] % 9)

    def poly(points):
        d = "M " + " L ".join(pts(px, py) for px, py in points)
        wires.append(path(d, fill="none", stroke="#000000"))

    x_left = 0.0
    for sig, pins in consumers.items():
        ty = tracks[sig]
        xs = [p[0] for p in pins]
        if sig in producer:
            ox, oy = producer[sig]
            start_x = ox + 0.4 + next_lane()
            poly([(ox, oy), (start_x, oy), (start_x, ty)])
        else:
            start_x = x_left
            # input label: small terminal at the left of the track
        end_x = max(px - 0.3 for px in xs)
        poly([(start_x, ty), (end_x, ty)])
        for (px, py) in pins:
            sx = px - 0.3 - next_lane() * 0.5
            poly([(sx, ty), (sx, py), (px, py)])
    # outputs S_i and final carry clock C4
    for i in range(4):
        ox, oy = producer[f"S{i}"]
        ty = tracks[f"S{i}"]
        poly([(ox, oy), (ox + 0.6, oy), (ox + 0.6, ty), (ox + 1.6, ty)])
    ox, oy = producer["C4"]
    poly([(ox, oy), (ox + 0.9, oy), (ox + 0.9, tracks["C4"]), (ox + 1.6, tracks["C4"])])

    allx = [col_x[5] + 2.0]
    height = max(max(next_y.values()), max(tracks.values())) + 0.3
    return svg_doc(wires + bodies, allx[0], height)


# ---------------------------------------------------------------- one-bit circuit

def make_bit_circuit():
    wires = [
        path("M 0 0.6 L 0 0 L 0.3 0", fill="none", stroke="#000000", sw=0.03),
        path("M 0.3 0 L 0.62 -0.2", fill="none", stroke="#000000", sw=0.03),      # switch lever
        path("M 0.7 0 L 1 0 L 1 0.6", fill="none", stroke="#000000", sw=0.03),
    ]
    dots = [path(circle_d(0, 0.6, 0.07), fill="#000000"), path(circle_d(1, 0.6, 0.07), fill="#000000")]
    return svg_doc(wires + dots, 1, 0.6, margin=0.25)


# ---------------------------------------------------------------- QR

def make_qr(text="3b1b.co/support"):
    import segno
    qr = segno.make(text, version=1, error="L", boost_error=False)
    matrix = [list(row) for row in qr.matrix]
    n = len(matrix)
    in_finder = [[False] * n for _ in range(n)]
    for (r0, c0) in [(0, 0), (0, n - 7), (n - 7, 0)]:
        for r in range(r0, r0 + 7):
            for c in range(c0, c0 + 7):
                in_finder[r][c] = True
    squares, finders = [], []
    for r in range(n):
        for c in range(n):
            if matrix[r][c] and not in_finder[r][c]:
                squares.append(path(rect_d(c, r, 1, 1)))
    for (r0, c0) in [(0, 0), (0, n - 7), (n - 7, 0)]:
        # the ring's hole goes the opposite way so that it is a hole
        hole = (f"M {pts(c0 + 1, r0 + 1)} L {pts(c0 + 1, r0 + 6)} L {pts(c0 + 6, r0 + 6)} "
                f"L {pts(c0 + 6, r0 + 1)} Z")
        ring = rect_d(c0, r0, 7, 7) + " " + hole
        finders.append(path(ring))
        finders.append(path(rect_d(c0 + 2, r0 + 2, 3, 3)))
    return svg_doc(squares + finders, n, n, margin=0)


# ---------------------------------------------------------------- sudoku

PUZZLE = [
    "53..7....", "6..195...", ".98....6.", "8...6...3", "4..8.3..1", "7...2...6", ".6....28.", "...419..5", "....8..79",
]


def glyph_d(ch, cx, cy, height):
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    tp = TextPath((0, 0), ch, size=1, prop=FontProperties(family="DejaVu Sans"))
    verts, codes = tp.vertices, tp.codes
    xs, ys = verts[:, 0], verts[:, 1]
    gw, gh = xs.max() - xs.min(), ys.max() - ys.min()
    s = height / gh
    def T(v):
        return (cx + (v[0] - (xs.min() + xs.max()) / 2) * s, cy - (v[1] - (ys.min() + ys.max()) / 2) * s)
    d, i = [], 0
    while i < len(codes):
        c = codes[i]
        if c == 1:
            d.append("M " + pts(*T(verts[i]))); i += 1
        elif c == 2:
            d.append("L " + pts(*T(verts[i]))); i += 1
        elif c == 3:
            d.append("Q " + pts(*T(verts[i]), *T(verts[i + 1]))); i += 2
        elif c == 4:
            d.append("C " + pts(*T(verts[i]), *T(verts[i + 1]), *T(verts[i + 2]))); i += 3
        elif c == 79:
            d.append("Z"); i += 1
        else:
            i += 1
    return " ".join(d)


def make_sudoku():
    paths = []
    for r in range(9):
        for c in range(9):
            paths.append(path(rect_d(c, r, 1, 1), fill="none", stroke="#000000", sw=0.02))
    for r in range(3):
        for c in range(3):
            paths.append(path(rect_d(3 * c, 3 * r, 3, 3), fill="none", stroke="#000000", sw=0.04))
    paths.append(path(rect_d(0, 0, 9, 9), fill="none", stroke="#000000", sw=0.06))
    for r, row in enumerate(PUZZLE):
        for c, ch in enumerate(row):
            if ch != ".":
                paths.append(path(glyph_d(ch, c + 0.5, r + 0.5, 0.55), fill="#000000"))
    return svg_doc(paths, 9, 9, margin=0.1)


# ---------------------------------------------------------------- switch

def make_light_switch():
    plate = rect_d(0, 0, 1.2, 1.9)
    slot = (f"M {pts(0.4, 0.45)} L {pts(0.4, 1.45)} L {pts(0.8, 1.45)} L {pts(0.8, 0.45)} Z")  # hole (opposite direction)
    paths = [
        path(plate + " " + slot),
        path(rect_d(0.45, 0.5, 0.3, 0.5)),                     # lever (up)
        path(circle_d(0.6, 0.2, 0.06)),
        path(circle_d(0.6, 1.7, 0.06)),
    ]
    return svg_doc(paths, 1.2, 1.9, margin=0.05)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    files = {
        "and_gate.svg": make_gate_svg("and"),
        "or_gate.svg": make_gate_svg("or"),
        "not_gate.svg": make_gate_svg("not"),
        "Four_bit_adder_with_carry_lookahead.svg": make_adder(),
        "BitCircuit.svg": make_bit_circuit(),
        "channel_support_QR_code.svg": make_qr(),
        "sudoku_example.svg": make_sudoku(),
        "light_switch.svg": make_light_switch(),
    }
    for name, text in files.items():
        (OUT / name).write_text(text)
        print("escrito", OUT / name, len(text), "bytes")
    # Copies of assets the repo already ships under another name
    for src, dst in [("gpu.svg", "computer_chip.svg"), ("magnifying_glass.svg", "magnifying_glass2.svg"),
                     ("circuit.svg", "BinaryFunctionCircuit.svg")]:
        shutil.copyfile(OUT / src, OUT / dst)
        print("copiado", src, "->", dst)


if __name__ == "__main__":
    main()
