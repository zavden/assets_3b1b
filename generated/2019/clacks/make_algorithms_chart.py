"""Recreate the mathematical comparison chart without private screenshots."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ASSETS = Path(__file__).resolve().parents[3]
OUTPUT = ASSETS / "raster_images/CX19PiAlgorithmsChart.png"


def main():
    plt.rcParams.update({"font.family": "DejaVu Serif", "mathtext.fontset": "cm"})
    figure = plt.figure(figsize=(14, 8), dpi=100, facecolor="black")
    axes = figure.add_axes([.09, .16, .86, .7], facecolor="black")
    axes.set(xlim=(-.2, 9.5), ylim=(-.1, 5.3))
    axes.axis("off")
    for end in ((9.3, 0), (0, 5.15)):
        axes.annotate("", xy=end, xytext=(0, 0),
                      arrowprops={"arrowstyle": "->", "color": "white", "lw": 1.5})
    axes.text(4.5, -.6, "Elegance", ha="center", color="white", fontsize=20)
    axes.text(-.7, 2.6, "Efficiency", rotation=90, ha="center", va="center",
              color="white", fontsize=20)
    figure.text(.5, .94, r"Algorithms for computing $\pi$", ha="center",
                color="white", fontsize=24)
    methods = [
        (1, 4.5, r"$\frac{\pi}{4}=12\arctan\frac{1}{49}+32\arctan\frac{1}{57}"
         r"-5\arctan\frac{1}{239}+12\arctan\frac{1}{110443}$"),
        (3, 3.5, r"$\frac{2}{\pi}=\frac{\sqrt{2}}{2}\cdot"
         r"\frac{\sqrt{2+\sqrt{2}}}{2}\cdot"
         r"\frac{\sqrt{2+\sqrt{2+\sqrt{2}}}}{2}\cdots$"),
        (.5, 1, "Measuring tape"),
        (2, .2, "Monte Carlo"),
        (6, 1, r"$\frac{\pi^2}{6}=\sum_{n=1}^{\infty}\frac{1}{n^2}$"),
        (8, .1, "Colliding blocks"),
    ]
    labels = []
    for x, y, label in methods:
        axes.plot(x, y, marker="x", markersize=9, color="#FC6255", mew=2)
        labels.append(axes.annotate(label, (x, y), xytext=(8, 14),
                                     textcoords="offset points", color="white", fontsize=15))
    figure.canvas.draw()
    renderer = figure.canvas.get_renderer()
    for label in labels:
        right = label.get_window_extent(renderer).x1
        if right > figure.bbox.width - 24:
            label.set_position((8 - (right - figure.bbox.width + 24) * 72 / figure.dpi, 14))
    figure.text(.1, .035, "Recreated diagram", color="#888888", fontsize=10)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, facecolor="black", dpi=100)
    plt.close(figure)
    print(OUTPUT)


if __name__ == "__main__":
    main()
