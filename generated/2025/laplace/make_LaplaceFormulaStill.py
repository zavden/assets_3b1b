# Generates LaplaceFormulaStill.png (background of DampedSpringSolutionsOnSPlane, laplace/shm.py). It
# is reconstructed as the quadratic formula for the roots of m s^2 + mu s + k, which is what the
# points on the s plane show: the code's point s_rhs_point (-4.09, -1.0) is the start of the
# right-hand side of "s = ...". Colors of m, mu and k as those of the sliders. It is rendered as a
# static scene with _tools/render.py (it saves the last frame as PNG).
from manim_imports_ext import *


class LaplaceFormulaStill(InteractiveScene):
    def construct(self):
        colors = [interpolate_color_by_hsl(RED, TEAL, a) for a in np.linspace(0, 1, 3)]
        t2c = {"s": YELLOW, "m": colors[0], R"\mu": colors[1], "k": colors[2]}
        rhs = Tex(R"{-\mu \pm \sqrt{\mu^2 - 4mk} \over 2m}", t2c=t2c, font_size=60)
        lhs = Tex(R"s =", t2c=t2c, font_size=60)
        rhs.move_to((-4.09, -1.0, 0), LEFT)
        lhs.next_to(rhs, LEFT, buff=0.2)
        self.add(lhs, rhs)
