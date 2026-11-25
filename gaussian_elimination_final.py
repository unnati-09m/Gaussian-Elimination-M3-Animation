"""
Gaussian Elimination - M3 Animation Video Project (final version)
Author: Unnati Mehatkar

Render (silent 1080p / 30 fps):
    manim -r 1920,1080 --fps 30 gaussian_elimination_final.py GaussianElimination
Fast preview (480p):
    manim -ql gaussian_elimination_final.py GaussianElimination

While rendering, the scene logs the REAL start/end time of every segment and writes
  GaussianElimination_Scene_Timestamps.txt
  GaussianElimination_Voiceover_Script.txt
next to this file, so the narration timestamps always match the video that was actually rendered.
Every self.play() has an explicit run_time, so the timeline is deterministic.
"""
from manim import *
import numpy as np
import re
from pathlib import Path

config.background_color = "#FBFAF7"

# ---------------------------------------------------------------- palette
BG, NAVY = "#FBFAF7", "#14213D"
BLUE, TEAL, ORANGE = "#2563EB", "#0D9488", "#EA7A12"      # equations / planes 1, 2, 3
PURPLE = "#7C3AED"                                         # pivots & highlights
GREY, GREEN, RED = "#6B7280", "#15803D", "#B91C1C"
EQC = [BLUE, TEAL, ORANGE]

# ---------------------------------------------------------------- segments: (id, title, planned seconds, narration)
SEG = [
 ("S01","Title and introduction",32,"Hi, I'm Unnati Mehatkar, and today we'll learn Gaussian elimination. What problem are we solving? Finding values that satisfy several equations together. Why is it hard? Unknowns are tangled together, so guessing gets messy. Why a systematic method? Fixed steps work on any system, without guessing. How does it help? It removes unknowns one by one until the answer is clear."),
 ("S02","The problem: three equations",15,"Here is our system: three equations in three unknowns, x, y, and z. Our goal: find values that make all three true at the same time."),
 ("S03","Concept: what is Gaussian elimination",22,"This is a system of linear equations. Gaussian elimination changes it to an equivalent system with exactly the same solutions. [PAUSE 1s] Forward elimination makes zeros below the pivots. Back substitution then finds the unknowns from the bottom up."),
 ("S04","Two variables: three cases",20,"First, two variables. Two lines that cross give exactly one solution. [PAUSE 1s] Distinct parallel lines never meet, so there is no solution. [PAUSE 1s] Coincident lines share every point, so there are infinitely many solutions."),
 ("S05","3D case 1: one point",9,"Now three variables. Three planes meeting at exactly one point give a unique solution."),
 ("S06","3D case 2: common line",10,"Three planes can share a common line. Every point on it is a solution, so there are infinitely many."),
 ("S07","3D case 3: coincident planes",9,"If two planes coincide and a third cuts through, the solutions again form a line."),
 ("S08","3D case 4: parallel planes",9,"Distinct parallel planes never meet, so there is no solution."),
 ("S09","3D case 5: pairwise only",12,"Planes can meet in pairs yet share no common point: no solution again. So only three outcomes exist: one, infinitely many, or none."),
 ("S10","Augmented matrix",18,"Writing x, y, z again and again is tiring, so we keep only the numbers: the augmented matrix. Coefficients on the left, constants on the right, one row per equation. Then each step is simple row arithmetic."),
 ("S11","Three row operations",32,"Three row operations are allowed. One: swap two rows. Two: multiply a row by a non-zero number. Three: add a multiple of one row to another. [PAUSE 1s] None of them changes the solution: swapping only reorders equations, scaling treats both sides equally, and adding equals to equals keeps equality. Here x equals two, y equals one stays true."),
 ("S12","Pivot",13,"A pivot is the first non-zero entry of a row; its place is a pivot position. [PAUSE 1s] We use it to make zeros below."),
 ("S13","Row operation 1: R2 - 2R1",16,"Replace row two with row two minus two times row one. [PAUSE 1s] That gives zero, minus one, one, and one. Notice the first entry of row two is now zero."),
 ("S14","Row operation 2: R3 - R1",13,"We repeat the same process for row three. Replace row three with row three minus row one. [PAUSE 1s] That gives zero, one, zero, and two."),
 ("S15","Row operation 3: R3 + R2",14,"Now the second pivot is minus one. Replace row three with row three plus row two. [PAUSE 1s] That gives zero, zero, one, and three."),
 ("S16","Row-echelon form",19,"Now the matrix is in row-echelon form. Zero rows sit at the bottom, each pivot is to the right of the one above, and entries below pivots are zero. This is the form created by forward elimination."),
 ("S17","Back substitution",22,"Back substitution starts at the last row, which has only z. So z equals three. [PAUSE 1s] Then minus y plus three equals one, so y equals two. [PAUSE 1s] Finally x plus two plus three equals six, so x equals one."),
 ("S18","Verification",16,"Let's verify in the original equations. One plus two plus three is six. Two plus two plus nine is thirteen. One plus four plus three is eight. [PAUSE 1s] All three hold."),
 ("S19","Case 1: unique solution",13,"Our final matrix has a pivot in every variable column and no contradictory row. So the system is consistent, with no free variables: exactly one solution."),
 ("S20","Case 2: infinitely many solutions",22,"Two pivots, three variables, so z is free. Call it t. [PAUSE 1s] Row two gives y equals one plus t. Row one gives x equals one minus three t. Every t gives a solution: infinitely many."),
 ("S21","Case 3: no solution; zero row vs contradiction",21,"A row zero, zero, zero, five says zero equals five. Impossible: the system is inconsistent, so there is no solution. [PAUSE 1s] A row of all zeros says zero equals zero. That is only a redundant equation, not a contradiction."),
 ("S22","Pivots, rank and consistency",16,"The system is consistent exactly when rank A equals the rank of the augmented matrix. If that rank equals the number of variables, there is one solution; if smaller, infinitely many."),
 ("S23","Geometry of the worked example",16,"What does our answer mean? Each equation is a plane, and these three planes meet at exactly one point: one, two, three. Elimination found that point."),
 ("S24","Summary and credits",20,"To recap: row operations never change the solutions. Make zeros below the pivots, then back substitute. A contradictory row means no solution; free variables mean infinitely many; otherwise exactly one. Thanks for watching!"),
]
IDX = {s[0]: i for i, s in enumerate(SEG)}
WORDS_PER_SEC = 2.1    # about 126 words per minute

# Twelve recording blocks keep the voice-over practical while preserving the
# scene-level timings needed to sync every line to the rendered video.
VOICE_GROUPS = [
    ("Introduction and problem", ["S01", "S02"]),
    ("Method and equivalent systems", ["S03", "S04"]),
    ("3D solutions: point and line", ["S05", "S06"]),
    ("3D solutions: overlapping and no common point", ["S07", "S08", "S09"]),
    ("Augmented matrix and row operations", ["S10", "S11"]),
    ("Pivots and forward elimination", ["S12", "S13", "S14", "S15"]),
    ("Row-echelon form and back substitution", ["S16", "S17"]),
    ("Verification and unique solution", ["S18", "S19"]),
    ("Infinite and no-solution cases", ["S20", "S21"]),
    ("Solution-classification flowchart", ["S22"]),
    ("Worked-example geometry", ["S23"]),
    ("Summary and credits", ["S24"]),
]

# ---------------------------------------------------------------- small helpers
def T(s, size=32, color=NAVY, **kw):
    return Text(s, font_size=size, color=color, **kw)

def M(s, size=44, color=NAVY):
    return MathTex(s, color=color).scale(size / 48)

def eq_line(lhs, rhs, color, size=44):
    """One equation with the '=' sign at x = 0 so stacked equations line up."""
    e = M("=", size, color); a = M(lhs, size, color); b = M(rhs, size, color)
    a.next_to(e, LEFT, buff=0.2); b.next_to(e, RIGHT, buff=0.2)
    return VGroup(a, e, b)

def eq_block(rows, colors, size=44, gap=0.9):
    lines = []
    for i, ((l, r), c) in enumerate(zip(rows, colors)):
        ln = eq_line(l, r, c, size); ln.shift(DOWN * i * gap); lines.append(ln)
    return VGroup(*lines)

ORIG = [("x + y + z", "6"), ("2x + y + 3z", "13"), ("x + 2y + z", "8")]

class AugMat:
    """Augmented matrix built from MathTex entries, so every entry can be animated and highlighted."""
    def __init__(self, rows, ncoef=None, cw=1.1, rh=0.85, fs=40, gap=0.45, labels=True):
        self.vals = [list(r) for r in rows]
        self.n, self.m = len(rows), len(rows[0])
        self.ncoef = self.m - 1 if ncoef is None else ncoef
        self.cw, self.rh, self.fs = cw, rh, fs
        xs = [j * cw + (gap if j >= self.ncoef else 0) for j in range(self.m)]
        ys = [-i * rh for i in range(self.n)]
        self.ent = [[M(str(v), fs).move_to([xs[j], ys[i], 0]) for j, v in enumerate(r)]
                    for i, r in enumerate(rows)]
        bx = (xs[self.ncoef - 1] + xs[self.ncoef]) / 2
        top, bot = ys[0] + rh / 2 + 0.05, ys[-1] - rh / 2 - 0.05
        bar = DashedLine([bx, top, 0], [bx, bot, 0], color=GREY, stroke_width=3, dash_length=0.12)
        l, r_ = xs[0] - cw / 2 - 0.1, xs[-1] + cw / 2 + 0.1
        lb = VMobject(stroke_color=NAVY, stroke_width=5, fill_opacity=0).set_points_as_corners(
            [[l + 0.18, top, 0], [l, top, 0], [l, bot, 0], [l + 0.18, bot, 0]])
        rb = VMobject(stroke_color=NAVY, stroke_width=5, fill_opacity=0).set_points_as_corners(
            [[r_ - 0.18, top, 0], [r_, top, 0], [r_, bot, 0], [r_ - 0.18, bot, 0]])
        self.frame = VGroup(lb, rb, bar)
        self.rowlab = VGroup()
        if labels:
            for i in range(self.n):
                self.rowlab.add(T(f"R{i+1}", 28, EQC[i % 3]).move_to([l - 0.55, ys[i], 0]))
        self.group = VGroup(self.frame, self.rowlab, *[e for r in self.ent for e in r])

    def row(self, i):  return VGroup(*self.ent[i])
    def row_box(self, i, color, buff=0.1):
        return SurroundingRectangle(self.row(i), color=color, buff=buff, stroke_width=4, corner_radius=0.1)
    def box(self, i, j, color=PURPLE):
        return SurroundingRectangle(self.ent[i][j], color=color, buff=0.14, stroke_width=5, corner_radius=0.08)
    def set_row(self, i, vals):
        """Animations that rewrite the changed entries of row i."""
        out = []
        for j, v in enumerate(vals):
            if self.vals[i][j] == v: continue
            old = self.ent[i][j]
            new = M(str(v), self.fs).move_to(old.get_center())
            out.append(ReplacementTransform(old, new))
            self.group.remove(old); self.group.add(new)
            self.ent[i][j] = new; self.vals[i][j] = v
        return out

def calc_panel(lines, colors, size=36, buff=0.35):
    g = VGroup(*[M(s, size, c) for s, c in zip(lines, colors)]).arrange(DOWN, aligned_edge=LEFT, buff=buff)
    return g


class GaussianElimination(ThreeDScene):
    # ============================================================ timeline helpers
    def now(self):
        return self.renderer.time

    def p(self, *anims, rt=1.0, **kw):
        self.play(*anims, run_time=rt, **kw)

    def w(self, d):
        if d > 0.001: self.wait(d)

    def seg_begin(self, sid):
        i = IDX[sid]
        self.cur = (sid, SEG[i][1], self.now(), SEG[i][2])

    def seg_end(self):
        sid, title, t0, dur = self.cur
        t = self.now()
        if t > t0 + dur + 0.05:
            self.overruns.append((sid, round(t - t0 - dur, 2)))
        else:
            self.w(t0 + dur - t)
        self.log.append((sid, title, t0, self.now()))

    def fade_all(self, rt=0.6):
        ms = list(self.mobjects)
        if ms: self.p(*[FadeOut(m) for m in ms], rt=rt)
        self.section_group = None

    def section(self, title):
        """Compact consistent heading, kept in the screen-safe top margin."""
        previous = getattr(self, "section_group", None)
        if previous is not None:
            self.p(FadeOut(previous), rt=0.25)
        label = T(title, 22, NAVY, weight=BOLD).to_corner(UL, buff=0.35)
        self.add_fixed_in_frame_mobjects(label)
        self.p(FadeIn(label), rt=0.35)
        self.section_group = VGroup(label)
        return self.section_group

    def construct(self):
        self.log, self.overruns, self.prev3d = [], [], []
        self.camera.background_color = BG
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES)
        for fn in (self.s01, self.s02, self.s03, self.s04, self.s05, self.s06, self.s07, self.s08, self.s09,
                   self.s10, self.s11, self.s12, self.s13, self.s14, self.s15, self.s16, self.s17, self.s18,
                   self.s19, self.s20, self.s21, self.s22, self.s23, self.s24):
            fn()
        self.write_files()

    # ============================================================ S01 title + introduction
    def s01(self):
        self.seg_begin("S01")
        t0 = self.cur[2]
        t = T("Gaussian Elimination", 62, NAVY, weight=BOLD)
        s = T("Solving systems of simultaneous linear equations", 32, GREY)
        goal = T("Goal: solve a 3 x 3 system and classify its solutions", 28, TEAL)
        who = T("Unnati Mehatkar    |    URN: E25B070765", 30, NAVY)
        c = T("M3: Linear Algebra and Calculus  -  Animation Video Project", 26, GREY)
        VGroup(t, s, goal, who, c).arrange(DOWN, buff=0.42).move_to(ORIGIN)
        self.p(FadeIn(t, shift=UP * 0.2), rt=1.2)
        self.p(FadeIn(s), rt=0.8)
        self.p(FadeIn(goal), FadeIn(who), FadeIn(c), rt=1.0)
        self.w(1.8)
        # title moves to the top; the four introduction questions appear one by one
        self.p(FadeOut(goal), FadeOut(who), FadeOut(c),
               t.animate.scale(0.6).move_to([0, 3.05, 0]), s.animate.scale(0.8).move_to([0, 2.35, 0]), rt=1.0)
        qa = [("What problem are we solving?", "Finding values of x, y, z that satisfy several equations at once."),
              ("Why can it be difficult?", "Unknowns are tangled together, so guessing gets messy and error-prone."),
              ("Why do we need a systematic method?", "Fixed steps work on any system, without guessing."),
              ("How does Gaussian elimination help?", "It removes unknowns one by one until the answer is easy to read.")]
        items = VGroup(*[VGroup(T(q, 30, PURPLE, weight=BOLD), T(a, 26, NAVY)).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
                         for q, a in qa]).arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        if items.width > 12.0:
            items.scale_to_fit_width(12.0)
        items.move_to([0, -0.55, 0])
        starts = [6.0, 12.25, 18.5, 24.75]          # seconds after the start of S01 (see voice-over script)
        for k, item in enumerate(items):
            self.w(t0 + starts[k] - self.now())
            dim = [items[k - 1].animate.set_opacity(0.45)] if k > 0 else []
            self.p(FadeIn(item[0], shift=RIGHT * 0.3), *dim, rt=0.7)
            self.p(FadeIn(item[1]), rt=0.8)
        self.seg_end()

    # ============================================================ S02 the problem
    def s02(self):
        self.seg_begin("S02")
        self.fade_all()
        label = T("The Problem: Solving Simultaneous Equations", 26, NAVY, weight=BOLD).to_corner(UL, buff=0.5)
        self.add_fixed_in_frame_mobjects(label)
        self.p(FadeIn(label), rt=0.35)
        self.section_group = VGroup(label)          # S03 fades this heading out, exactly as before
        self.w(0.65)
        blk = eq_block(ORIG, EQC, size=54, gap=1.1).move_to([0, 0.15, 0])      # centred on the screen
        for ln in blk:
            self.p(Write(ln), rt=1.2)
            self.w(0.6)
        capA = T("A system of three linear equations in three unknowns: x, y, z", 28, NAVY).move_to([0, -3.0, 0])
        self.p(FadeIn(capA), rt=0.8)
        self.w(1.4)
        q = T("Goal: find x, y, z that satisfy ALL three equations at the same time", 28, PURPLE).move_to([0, -3.0, 0])
        if q.width > 12.4:
            q.scale_to_fit_width(12.4)
        self.p(FadeOut(capA), FadeIn(q), rt=0.8)
        self.q_hook, self.blk_hook = q, blk         # used unchanged by S03
        self.seg_end()

    # ============================================================ S03 concept: what is Gaussian elimination
    def s03(self):
        self.seg_begin("S03")
        self.section("What Is Gaussian Elimination?")
        self.p(FadeOut(self.q_hook), self.blk_hook.animate.scale(0.62).move_to([-4.0, 1.9, 0]), rt=1.0)
        sys_lab = T("system of linear equations", 22, GREY).move_to([-4.0, 2.88, 0])
        tri = eq_block([("x + y + z", "6"), ("-y + z", "1"), ("z", "3")], EQC, size=34, gap=0.7).move_to([4.0, 1.9, 0])
        tri_lab = T("equivalent system", 22, GREY).move_to([4.0, 2.88, 0])
        arrow = Arrow([-1.5, 1.9, 0], [1.5, 1.9, 0], color=PURPLE, stroke_width=6, buff=0)
        eqlab = T("same solutions", 26, PURPLE).next_to(arrow, UP, buff=0.15)
        self.p(FadeIn(sys_lab), GrowArrow(arrow), FadeIn(eqlab), FadeIn(tri), FadeIn(tri_lab), rt=1.6)
        ph1 = VGroup(T("Forward elimination", 28, NAVY, weight=BOLD),
                     T("Create zeros below pivots; reach row-echelon form.", 21, GREY)
                     ).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        ph2 = VGroup(T("Back substitution", 28, NAVY, weight=BOLD),
                     T("Solve from the bottom row upward.", 21, GREY)
                     ).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        both = VGroup(ph1, ph2).arrange(DOWN, aligned_edge=LEFT, buff=0.55).move_to([0, -1.8, 0])
        ph2.set_opacity(0)
        self.w(7.0)
        self.p(FadeIn(ph1, shift=RIGHT * 0.3), rt=1.2)
        self.w(2.6)
        ph2.set_opacity(1)
        self.section("Equivalent Systems")
        self.p(FadeIn(ph2, shift=RIGHT * 0.3), rt=1.2)
        self.seg_end()
    # ============================================================ S04 two variables
    def s04(self):
        self.seg_begin("S04")
        self.fade_all()
        self.section("Geometric Interpretation of Solutions")
        ax = Axes(x_range=[-1, 6, 1], y_range=[-1, 5, 1], x_length=7, y_length=6,
                  axis_config={"color": NAVY, "stroke_width": 3, "include_tip": False,
                               "include_numbers": True, "font_size": 24, "decimal_number_config": {"color": NAVY, "num_decimal_places": 0}}
                  ).move_to([-3.4, -0.2, 0])
        xl = M("x", 34).next_to(ax.c2p(6, 0), UP, buff=0.1); yl = M("y", 34).next_to(ax.c2p(0, 5), RIGHT, buff=0.1)
        self.p(Create(ax), FadeIn(xl), FadeIn(yl), rt=1.0)
        L = lambda f, a, b, col: ax.plot(f, x_range=[a, b], color=col, stroke_width=6)
        # case 1 -------------------------------------------------------------
        e1 = VGroup(M(r"x + y = 3", 40, BLUE), M(r"x - y = 1", 40, TEAL)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([4.0, 2.2, 0])
        l1, l2 = L(lambda x: 3 - x, -1, 4, BLUE), L(lambda x: x - 1, 0, 5, TEAL)
        pt = Dot(ax.c2p(2, 1), color=PURPLE, radius=0.13)
        ptl = M("(2,\\,1)", 36, PURPLE).next_to(pt, UR, buff=0.15)
        v1 = T("Exactly one solution", 30, PURPLE, weight=BOLD).move_to([3.9, -2.2, 0])
        self.p(FadeIn(e1), Create(l1), rt=1.0)
        self.p(Create(l2), rt=1.0)
        self.p(FadeIn(pt, scale=2), FadeIn(ptl), FadeIn(v1), rt=1.0)
        self.w(2.6)
        self.p(*[FadeOut(m) for m in (e1, l1, l2, pt, ptl, v1)], rt=0.5)
        # case 2 -------------------------------------------------------------
        e2 = VGroup(M(r"x + y = 3", 40, BLUE), M(r"x + y = 5", 40, TEAL)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([4.0, 2.2, 0])
        l3, l4 = L(lambda x: 3 - x, -1, 4, BLUE), L(lambda x: 5 - x, 0, 6, TEAL)
        v2 = T("No solution", 30, RED, weight=BOLD).move_to([3.9, -2.2, 0])
        w2 = T("parallel lines never meet", 26, GREY).next_to(v2, DOWN, buff=0.2)
        self.p(FadeIn(e2), Create(l3), rt=1.0)
        self.p(Create(l4), rt=1.0)
        self.p(FadeIn(v2), FadeIn(w2), rt=0.8)
        self.w(2.4)
        self.p(*[FadeOut(m) for m in (e2, l3, l4, v2, w2)], rt=0.5)
        # case 3 -------------------------------------------------------------
        e3 = VGroup(M(r"x + y = 3", 40, BLUE), M(r"2x + 2y = 6", 40, TEAL)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([4.0, 2.2, 0])
        l5 = L(lambda x: 3 - x, -1, 4, BLUE)
        l6 = ax.plot(lambda x: 3 - x, x_range=[-1, 4], color=TEAL, stroke_width=11, stroke_opacity=0.45)
        v3 = T("Infinitely many solutions", 30, PURPLE, weight=BOLD).move_to([3.9, -2.2, 0])
        w3 = T("every point on the line works", 26, GREY).next_to(v3, DOWN, buff=0.2)
        self.p(FadeIn(e3), Create(l6), Create(l5), rt=1.2)
        self.p(FadeIn(v3), FadeIn(w3), rt=0.8)
        self.seg_end()

    # ============================================================ 3D helpers
    def setup3d(self):
        self.fade_all(0.5)
        self.set_camera_orientation(phi=68 * DEGREES, theta=-62 * DEGREES)
        ax = ThreeDAxes(x_range=[-3, 3, 1], y_range=[-3, 3, 1], z_range=[-3, 3, 1],
                        x_length=5.4, y_length=5.4, z_length=5.4,
                        axis_config={"color": NAVY, "stroke_width": 2.5, "include_tip": False})
        self.ax = ax
        labs = [M(s, 36, NAVY).move_to(ax.c2p(*pos)) for s, pos in
                (("x", (3.5, 0, 0)), ("y", (0, 3.5, 0)), ("z", (0, 0, 3.5)))]
        self.add_fixed_orientation_mobjects(*labs)
        self.p(Create(ax), *[FadeIn(l) for l in labs], rt=1.0)
        self.begin_ambient_camera_rotation(rate=0.045)

    def plane(self, f, col, op=0.40):
        return Surface(lambda u, v: self.ax.c2p(*f(u, v)), u_range=[-2.4, 2.4], v_range=[-2.4, 2.4],
                       resolution=(6, 6), fill_opacity=op, stroke_width=1, stroke_color=col,
                       checkerboard_colors=[col, col])

    def config3d(self, sid, planes, eqs, highlight, verdict, vcol, note=None, first=False):
        """planes: list of (func, colour); eqs: tex strings; highlight: list of mobjects drawn in 3D."""
        self.seg_begin(sid)
        heading = {
            "S05": "Geometric Interpretation: Three Planes",
            "S06": "Geometric Interpretation: Three Planes",
            "S07": "Geometric Interpretation: Three Planes",
            "S08": "Geometric Interpretation: Three Planes",
            "S09": "Geometric Interpretation: Three Planes",
        }[sid]
        self.section(heading)
        if first:
            self.setup3d()
        if self.prev3d:
            self.p(*[FadeOut(m) for m in self.prev3d], rt=0.5)
        highlight = highlight() if callable(highlight) else highlight
        surf = [self.plane(f, c) for f, c in planes]
        cap = VGroup(*[M(s, 34, c) for s, (f, c) in zip(eqs, planes)]).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        cap.to_corner(UL, buff=0.5).shift(DOWN * 0.55)
        ver = T(verdict, 34, vcol, weight=BOLD).to_edge(DOWN, buff=0.45)
        objs = [cap, ver]
        if note:
            nt = T(note, 26, GREY).next_to(ver, UP, buff=0.15); objs.append(nt)
        self.add_fixed_in_frame_mobjects(*objs)
        self.p(LaggedStart(*[FadeIn(s) for s in surf], lag_ratio=0.35), FadeIn(cap), rt=2.0)
        self.p(*[Create(h) if isinstance(h, Line3D) else FadeIn(h, scale=2) for h in highlight], FadeIn(ver),
               *( [FadeIn(nt)] if note else [] ), rt=1.0)
        self.prev3d = surf + list(highlight) + objs
        self.seg_end()

    def hl_point(self, p):  return Dot3D(self.ax.c2p(*p), radius=0.13, color=PURPLE)
    def hl_line(self, a, b): return Line3D(self.ax.c2p(*a), self.ax.c2p(*b), color=PURPLE, thickness=0.045)

    # ---- the five 3D configurations (each verified in verify_math.py)
    def s05(self):
        self.config3d("S05",
            [(lambda u, v: (0, u, v), BLUE), (lambda u, v: (u, 0, v), TEAL), (lambda u, v: (u, v, 0), ORANGE)],
            ["x = 0", "y = 0", "z = 0"], lambda: [self.hl_point((0, 0, 0))],
            "Unique solution: (0, 0, 0)", PURPLE, first=True)

    def s06(self):
        self.config3d("S06",
            [(lambda u, v: (0, u, v), BLUE), (lambda u, v: (u, v, 0), TEAL), (lambda u, v: (u, v, -u), ORANGE)],
            ["x = 0", "z = 0", "x + z = 0"], lambda: [self.hl_line((0, -3, 0), (0, 3, 0))],
            "Infinitely many solutions (y is free)", PURPLE, note="common line: the y-axis")

    def s07(self):
        self.config3d("S07",
            [(lambda u, v: (u, v, 0), BLUE), (lambda u, v: (0, u, v), ORANGE)],
            [r"z = 0 \ \text{and}\ 2z = 0 \ \text{(same plane)}", "x = 0"], lambda: [self.hl_line((0, -3, 0), (0, 3, 0))],
            "Infinitely many solutions (y is free)", PURPLE, note="coincident planes count as one plane")

    def s08(self):
        self.config3d("S08",
            [(lambda u, v: (u, v, -1), BLUE), (lambda u, v: (u, v, 0), TEAL), (lambda u, v: (u, v, 1), ORANGE)],
            ["z = -1", "z = 0", "z = 1"], [],
            "No solution", RED, note="no point lies on all three planes")

    def s09(self):
        self.config3d("S09",
            [(lambda u, v: (0, u, v), BLUE), (lambda u, v: (u, 0, v), TEAL), (lambda u, v: (u, 1 - u, v), ORANGE)],
            ["x = 0", "y = 0", "x + y = 1"],
            lambda: [self.hl_line((0, 0, -3), (0, 0, 3)), self.hl_line((0, 1, -3), (0, 1, 3)), self.hl_line((1, 0, -3), (1, 0, 3))],
            "No solution", RED, note="pairs meet in lines, but there is no common point")
        self.stop_ambient_camera_rotation()

    # ============================================================ S10 augmented matrix
    def s10(self):
        self.seg_begin("S10")
        self.fade_all()
        self.section("Augmented Matrix")
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES)
        blk = eq_block(ORIG, EQC, size=38, gap=0.95).move_to([-3.9, 0.2, 0])
        mat = AugMat([[1, 1, 1, 6], [2, 1, 3, 13], [1, 2, 1, 8]], cw=1.15, fs=42)
        mat.group.move_to([3.4, 0.2, 0])
        self.p(FadeIn(blk), rt=1.0)
        arrow = Arrow([-1.4, 0.2, 0], [0.3, 0.2, 0], color=PURPLE, stroke_width=6, buff=0)
        self.p(GrowArrow(arrow), FadeIn(mat.group), rt=1.6)
        self.w(4.2)
        hdr = VGroup(*[M(s, 36, NAVY).next_to(mat.ent[0][j], UP, buff=0.55) for j, s in enumerate(["x", "y", "z", "b"])])
        b1 = Brace(VGroup(*[mat.ent[i][j] for i in range(3) for j in range(3)]), DOWN, color=GREY, buff=0.35)
        b1l = T("coefficients", 26, GREY).next_to(b1, DOWN, buff=0.1)
        b2 = Brace(VGroup(*[mat.ent[i][3] for i in range(3)]), DOWN, color=GREY, buff=0.35)
        b2l = T("constants", 26, GREY).next_to(b2, DOWN, buff=0.1)
        self.p(FadeIn(hdr), FadeIn(b1), FadeIn(b1l), FadeIn(b2), FadeIn(b2l), rt=1.4)
        self.w(2.0)
        r2 = mat.row_box(1, TEAL); e2 = SurroundingRectangle(blk[1], color=TEAL, buff=0.15, stroke_width=4, corner_radius=0.1)
        cap = M(r"\text{Row 2 means:}\quad 2x + y + 3z = 13", 36, TEAL).move_to([0, -3.2, 0])
        self.p(Create(r2), Create(e2), FadeIn(cap), rt=1.2)
        self.seg_end()

    # ============================================================ S11 three row operations (animated demos)
    def s11(self):
        self.seg_begin("S11")
        self.fade_all()
        self.section("Elementary Row Operations")
        mat = AugMat([[1, 1, 3], [1, -1, 1]], ncoef=2, cw=1.3, rh=1.0, fs=48)
        mat.group.move_to([-3.6, 0.5, 0])
        start = M(r"\text{start: } x+y=3,\ \ x-y=1", 32, GREY).move_to([-3.6, -1.6, 0])
        self.p(FadeIn(mat.group), FadeIn(start), rt=1.0)
        sol = M(r"(x,\,y)=(2,\,1)\ \checkmark", 44, GREEN).move_to([3.6, -1.2, 0])
        solcap = T("solution unchanged", 26, GREY).next_to(sol, DOWN, buff=0.25)
        self.p(FadeIn(sol), FadeIn(solcap), rt=0.8)

        def show(note_tex, name, why, col):
            n = M(note_tex, 46, PURPLE).move_to([3.6, 2.7, 0])
            nm = T(name, 28, col, weight=BOLD).next_to(n, DOWN, buff=0.25)
            wy = T(why, 25, NAVY).next_to(nm, DOWN, buff=0.35)
            self.p(FadeIn(n), FadeIn(nm), rt=0.8)
            return VGroup(n, nm), wy

        # 1) interchange
        hd, wy = show(r"R_1 \leftrightarrow R_2", "1. Interchange two rows", "Same equations, new order.", TEAL)
        r0, r1 = mat.row(0), mat.row(1)
        self.p(r0.animate.shift(DOWN * mat.rh), r1.animate.shift(UP * mat.rh), rt=1.4)
        mat.ent[0], mat.ent[1] = mat.ent[1], mat.ent[0]
        mat.vals[0], mat.vals[1] = mat.vals[1], mat.vals[0]
        self.p(Indicate(sol, color=GREEN), FadeIn(wy), rt=1.0)
        self.w(2.6)
        self.p(FadeOut(hd), FadeOut(wy), rt=0.6)
        # 2) scale
        hd, wy = show(r"R_1 \to 2R_1", "2. Multiply a row by k (k not 0)", "Both sides get the same factor.", BLUE)
        self.p(*mat.set_row(0, [2, -2, 2]), rt=1.3)
        wy2 = T("(k = 0 would destroy the equation.)", 22, GREY).next_to(wy, DOWN, buff=0.2)
        self.p(Indicate(sol, color=GREEN), FadeIn(wy), FadeIn(wy2), rt=1.0)
        self.w(2.6)
        self.p(FadeOut(hd), FadeOut(wy), FadeOut(wy2), rt=0.6)
        # 3) replace
        hd, wy = show(r"R_2 \to R_2 + R_1", "3. Add a multiple of a row", "Equals added to equals stay equal.", ORANGE)
        self.p(*mat.set_row(1, [3, -1, 5]), rt=1.3)
        self.p(Indicate(sol, color=GREEN), FadeIn(wy), rt=1.0)
        self.w(2.0)
        self.seg_end()
    # ============================================================ S12 pivot
    def s12(self):
        self.seg_begin("S12")
        self.fade_all()
        self.section("Understanding Pivot Positions")
        self.mat = AugMat([[1, 1, 1, 6], [2, 1, 3, 13], [1, 2, 1, 8]], cw=1.1, fs=42)
        self.mat.group.move_to([-3.6, 0.0, 0])
        self.p(FadeIn(self.mat.group), rt=1.2)
        self.pivbox = self.mat.box(0, 0)
        self.p(Create(self.pivbox), rt=0.8)
        d1 = T("Pivot = first non-zero\nentry of a row", 34, PURPLE, weight=BOLD)
        d1b = T("its place = pivot position", 24, GREY)
        d1 = VGroup(d1, d1b).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        d2 = T("Use the pivot to make the entries\nbelow it zero.", 28, NAVY)
        d3 = M(r"R_i \to R_i + k\,R_j", 40, NAVY)
        VGroup(d1, d2, d3).arrange(DOWN, aligned_edge=LEFT, buff=0.4).move_to([3.6, 0.3, 0])
        d1.move_to([3.6, 1.2, 0]); d2.next_to(d1, DOWN, buff=0.4, aligned_edge=LEFT); d3.next_to(d2, DOWN, buff=0.4, aligned_edge=LEFT)
        self.p(FadeIn(d1, shift=LEFT * 0.2), rt=1.0)
        self.w(2.0)
        self.p(FadeIn(d2, shift=LEFT * 0.2), rt=1.0)
        self.w(1.5)
        self.p(FadeIn(d3), rt=0.8)
        self.panel12 = VGroup(d1, d2, d3)
        self.seg_end()

    def op_scene(self, sid, banner_tex, row_i, row_j, lines, colors, entry_calc, new_vals, pivot_to=None):
        self.seg_begin(sid)
        self.section("Forward Elimination")
        mat = self.mat
        if getattr(self, "panel12", None) is not None:
            self.p(FadeOut(self.panel12), rt=0.5); self.panel12 = None
        elif getattr(self, "op_stuff", None) is not None:
            self.p(FadeOut(self.op_stuff), rt=0.5)
        if pivot_to is not None:
            nb = mat.box(*pivot_to)
            self.p(ReplacementTransform(self.pivbox, nb), rt=0.7); self.pivbox = nb
        # Place each row operation directly above the matrix it transforms.
        ban = M(banner_tex, 46, PURPLE).move_to([-3.6, 2.65, 0])
        ri, rj = mat.row_box(row_i, EQC[row_i]), mat.row_box(row_j, EQC[row_j])
        self.p(Write(ban), Create(ri), Create(rj), rt=1.2)
        panel = calc_panel(lines, colors).move_to([3.6, 0.5, 0])
        for k in range(len(lines)):
            self.p(Write(panel[k]), rt=1.2)
            self.w(0.8)
        ec = M(entry_calc, 30, GREY).next_to(panel, DOWN, buff=0.45)
        self.p(FadeIn(ec), rt=0.8)
        self.w(0.6)
        anims = mat.set_row(row_i, new_vals)
        self.p(*anims, rt=1.2)
        zero_j = [j for j in range(mat.m) if new_vals[j] == 0 and j < 3]
        self.p(*[Indicate(mat.ent[row_i][j], color=GREEN, scale_factor=1.7) for j in zero_j[:1]], rt=1.2)
        self.op_stuff = VGroup(ban, ri, rj, panel, ec)
        return

    def s13(self):
        self.op_scene("S13", r"R_2 \to R_2 - 2R_1", 1, 0,
            [r"R_2 = [\,2\ \ \ 1\ \ \ 3\ |\ 13\,]", r"2R_1 = [\,2\ \ \ 2\ \ \ 2\ |\ 12\,]",
             r"R_2 - 2R_1 = [\,0\ \ {-1}\ \ \ 1\ |\ 1\,]"], [TEAL, BLUE, GREEN],
            r"2-2(1)=0,\ \ 1-2(1)=-1 \\ 3-2(1)=1,\ \ 13-2(6)=1", [0, -1, 1, 1])
        self.seg_end()

    def s14(self):
        self.op_scene("S14", r"R_3 \to R_3 - R_1", 2, 0,
            [r"R_3 = [\,1\ \ \ 2\ \ \ 1\ |\ 8\,]", r"R_1 = [\,1\ \ \ 1\ \ \ 1\ |\ 6\,]",
             r"R_3 - R_1 = [\,0\ \ \ 1\ \ \ 0\ |\ 2\,]"], [ORANGE, BLUE, GREEN],
            r"1-1=0,\ \ 2-1=1 \\ 1-1=0,\ \ 8-6=2", [0, 1, 0, 2])
        self.seg_end()

    def s15(self):
        self.op_scene("S15", r"R_3 \to R_3 + R_2", 2, 1,
            [r"R_3 = [\,0\ \ \ 1\ \ \ 0\ |\ 2\,]", r"R_2 = [\,0\ \ {-1}\ \ \ 1\ |\ 1\,]",
             r"R_3 + R_2 = [\,0\ \ \ 0\ \ \ 1\ |\ 3\,]"], [ORANGE, TEAL, GREEN],
            r"0+0=0,\ \ 1+(-1)=0 \\ 0+1=1,\ \ 2+1=3", [0, 0, 1, 3], pivot_to=(1, 1))
        self.seg_end()

    # ============================================================ S16 echelon form
    def s16(self):
        self.seg_begin("S16")
        self.section("Row-Echelon Form")
        self.p(FadeOut(self.op_stuff), FadeOut(self.pivbox), rt=0.5)
        mat = self.mat
        piv = [mat.box(i, i) for i in range(3)]
        zer = [SurroundingRectangle(mat.ent[i][j], color=GREEN, buff=0.12, stroke_width=3, corner_radius=0.08)
               for (i, j) in ((1, 0), (2, 0), (2, 1))]
        cx = [mat.ent[0][j].get_center()[0] for j in range(3)]
        cy = [mat.ent[i][0].get_center()[1] for i in range(3)]
        hw, hh = mat.cw / 2, mat.rh / 2
        stair = VMobject(stroke_color=PURPLE, stroke_width=6, fill_opacity=0).set_points_as_corners(
            [[cx[0] - hw, cy[0] - hh, 0], [cx[1] - hw, cy[0] - hh, 0], [cx[1] - hw, cy[1] - hh, 0],
             [cx[2] - hw, cy[1] - hh, 0], [cx[2] - hw, cy[2] - hh, 0], [cx[2] + hw, cy[2] - hh, 0]])
        title = T("Row-echelon form", 40, PURPLE, weight=BOLD).move_to([3.5, 2.7, 0])
        p1 = T("1. Non-zero rows are above zero rows", 22, NAVY)
        p2 = T("2. Each pivot is to the right of the\n    pivot in the row above (staircase)", 22, NAVY)
        p3 = T("3. All entries below a pivot are zero", 22, NAVY)
        props = VGroup(p1, p2, p3).arrange(DOWN, aligned_edge=LEFT, buff=0.4).next_to(title, DOWN, buff=0.5)
        props.set_x(3.5)
        note = T("Forward elimination stops at row-echelon form.", 20, GREY).move_to([3.5, -2.6, 0])
        self.p(FadeIn(title), rt=0.8)
        self.p(FadeIn(p1), rt=0.8); self.w(1.0)
        self.p(FadeIn(p2), Create(stair), *[Create(b) for b in piv], rt=1.4); self.w(1.0)
        self.p(FadeIn(p3), *[Create(z) for z in zer], rt=1.4); self.w(1.5)
        self.p(FadeIn(note), rt=0.8)
        self.s16_stuff = VGroup(*piv, *zer, stair, title, props, note)
        self.seg_end()
    # ============================================================ S17 back substitution
    def s17(self):
        self.seg_begin("S17")
        self.section("Back Substitution")
        mat = self.mat
        self.p(FadeOut(self.s16_stuff), mat.group.animate.scale(0.85).move_to([-4.6, 0.8, 0]), rt=1.0)
        rows = eq_block([("x + y + z", "6"), ("-y + z", "1"), ("z", "3")], EQC, size=38, gap=0.7).move_to([2.6, 2.3, 0])
        self.p(FadeIn(rows), rt=0.8)
        z_ln = M(r"z = 3", 44, ORANGE)
        y_ln = M(r"-y + (3) = 1 \;\Rightarrow\; y = 2", 36, TEAL)
        x_ln = M(r"x + (2) + (3) = 6 \;\Rightarrow\; x = 1", 29, BLUE)
        sol = VGroup(z_ln, y_ln, x_ln).arrange(DOWN, aligned_edge=LEFT, buff=0.5).move_to([2.8, -0.4, 0])
        hint = T("start at the bottom row:\nit has only one unknown, z", 24, GREY).move_to([-4.6, -2.3, 0])
        rb = mat.row_box(2, PURPLE)
        self.p(Create(rb), FadeIn(hint), Write(z_ln), rt=1.6)
        self.w(2.4)
        rb2 = mat.row_box(1, PURPLE)
        self.p(ReplacementTransform(rb, rb2), Write(y_ln), rt=2.0)
        self.w(2.4)
        rb3 = mat.row_box(0, PURPLE)
        self.p(ReplacementTransform(rb2, rb3), Write(x_ln), rt=2.0)
        ans = M(r"(x,\,y,\,z) = (1,\,2,\,3)", 50, PURPLE).move_to([3.0, -2.9, 0])
        ansbox = SurroundingRectangle(ans, color=PURPLE, buff=0.25, stroke_width=5, corner_radius=0.12)
        self.p(Write(ans), Create(ansbox), rt=1.4)
        self.back_stuff = VGroup(mat.group, rows, sol, hint, rb3, ans, ansbox)
        self.seg_end()

    # ============================================================ S18 verification
    def s18(self):
        self.seg_begin("S18")
        self.section("Verifying the Solution")
        self.p(FadeOut(self.back_stuff), rt=0.6)
        t = T("Substitute (1, 2, 3) in the original equations", 30, NAVY, weight=BOLD).move_to([0, 2.65, 0])
        self.p(FadeIn(t), rt=0.8)
        subs = [r"1+2+3=6", r"2(1)+2+3(3)=2+2+9=13", r"1+2(2)+3=1+4+3=8"]
        origs = [r"x+y+z=6", r"2x+y+3z=13", r"x+2y+z=8"]
        for n in range(3):
            a = M(origs[n], 38, EQC[n]).move_to([-4.7, 1.4 - 1.5 * n, 0])
            arr = M(r"\Rightarrow", 38, GREY).move_to([-1.9, 1.4 - 1.5 * n, 0])
            b = M(subs[n], 36, EQC[n]).move_to([2.5, 1.4 - 1.5 * n, 0])
            tick = M(r"\checkmark", 56, GREEN).move_to([6.5, 1.4 - 1.5 * n, 0])
            self.p(FadeIn(a), rt=0.6)
            self.p(FadeIn(arr), Write(b), rt=1.5)
            self.p(FadeIn(tick, scale=1.6), rt=0.6)
            self.w(1.4)
        fin = T("All three equations are satisfied", 32, GREEN, weight=BOLD).move_to([0, -3.2, 0])
        self.p(FadeIn(fin), rt=0.8)
        self.seg_end()

    # ============================================================ S19 case 1: unique solution
    def s19(self):
        self.seg_begin("S19")
        self.fade_all()
        self.section("Classifying Solutions")
        ttl = T("Case 1: Unique solution", 40, TEAL, weight=BOLD).to_edge(UP, buff=0.6)
        m = AugMat([[1, 1, 1, 6], [0, -1, 1, 1], [0, 0, 1, 3]], cw=1.15, fs=44, labels=False)
        m.group.move_to([-3.6, 0.5, 0])
        self.p(FadeIn(ttl), FadeIn(m.group), rt=1.0)
        piv = [m.box(i, i) for i in range(3)]
        self.p(*[Create(b) for b in piv], rt=1.0)
        pts = VGroup(T("A pivot in every variable column", 25, NAVY),
                     T("3 pivots, 3 variables: no free variables", 25, NAVY),
                     T("No contradictory row: consistent", 25, NAVY)).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to([3.3, 1.0, 0])
        for t in pts:
            self.p(FadeIn(t, shift=RIGHT * 0.2), rt=0.9)
        res = M(r"\text{exactly one solution: } (1,\,2,\,3)", 38, PURPLE).move_to([3.4, -1.3, 0])
        self.p(Write(res), rt=1.2)
        self.seg_end()

    # ============================================================ S20 case 2: infinitely many solutions
    def s20(self):
        self.seg_begin("S20")
        self.fade_all()
        self.section("Classifying Solutions")
        ttl = T("Case 2: Infinitely many solutions", 40, PURPLE, weight=BOLD).to_edge(UP, buff=0.6)
        m = AugMat([[1, 2, 1, 3], [0, 1, -1, 1], [0, 0, 0, 0]], cw=1.1, fs=44, labels=False)
        m.group.move_to([-3.9, 1.0, 0])
        self.p(FadeIn(ttl), FadeIn(m.group), rt=1.0)
        piv = [m.box(0, 0), m.box(1, 1)]
        self.p(*[Create(b) for b in piv], rt=0.8)
        fr = SurroundingRectangle(VGroup(*[m.ent[i][2] for i in range(3)]), color=ORANGE, buff=0.12, stroke_width=4, corner_radius=0.1)
        frl = T("z is free: no pivot in its column", 24, ORANGE).next_to(m.group, DOWN, buff=0.55)
        zr = m.row_box(2, GREY)
        zl = T("0 = 0: redundant equation", 24, GREY).next_to(frl, DOWN, buff=0.25)
        self.p(Create(fr), FadeIn(frl), rt=1.0)
        self.p(Create(zr), FadeIn(zl), rt=0.8)
        zt = M(r"z = t", 40, ORANGE)
        yt = M(r"y - z = 1 \;\Rightarrow\; y = 1 + t", 34, TEAL)
        xt = M(r"x + 2(1+t) + t = 3 \;\Rightarrow\; x = 1 - 3t", 34, BLUE)
        g = VGroup(zt, yt, xt).arrange(DOWN, aligned_edge=LEFT, buff=0.45).move_to([3.3, 1.3, 0])
        self.p(Write(zt), rt=1.0); self.w(1.2)
        self.p(Write(yt), rt=1.3); self.w(1.0)
        self.p(Write(xt), rt=1.3)
        ans = M(r"(x,\,y,\,z) = (1-3t,\ 1+t,\ t)", 42, PURPLE).move_to([2.8, -1.7, 0])
        cap = T("every real number t gives a solution", 26, GREY).next_to(ans, DOWN, buff=0.3)
        abox = SurroundingRectangle(ans, color=PURPLE, buff=0.2, stroke_width=4, corner_radius=0.1)
        self.p(Write(ans), Create(abox), FadeIn(cap), rt=1.4)
        self.seg_end()

    # ============================================================ S21 case 3: no solution, zero row vs contradiction
    def s21(self):
        self.seg_begin("S21")
        self.fade_all()
        self.section("Classifying Solutions")
        ttl = T("Case 3: No solution", 40, RED, weight=BOLD).to_edge(UP, buff=0.4)
        lt = T("Contradictory row", 28, RED, weight=BOLD).move_to([-3.6, 2.5, 0])
        mR = AugMat([[1, 1, 1, 6], [0, -1, 1, 1], [0, 0, 0, 5]], cw=1.0, rh=0.85, fs=40, labels=False)
        mR.group.move_to([-3.6, 1.0, 0])
        self.p(FadeIn(ttl), FadeIn(lt), FadeIn(mR.group), rt=1.0)
        rb = mR.row_box(2, RED)
        eq = M(r"0x+0y+0z=5 \;\Rightarrow\; 0 = 5", 34, RED).next_to(mR.group, DOWN, buff=0.5)
        v1 = T("Impossible: system is inconsistent", 23, RED, weight=BOLD).next_to(eq, DOWN, buff=0.25)
        self.p(Create(rb), Write(eq), rt=1.4)
        self.p(FadeIn(v1), rt=0.8)
        self.w(3.0)
        rt_ = T("Zero row (for comparison)", 28, GREY, weight=BOLD).move_to([3.6, 2.5, 0])
        mZ = AugMat([[1, 0, 2], [0, 1, 3], [0, 0, 0]], cw=1.0, rh=0.85, fs=40, labels=False)
        mZ.group.move_to([3.6, 1.0, 0])
        self.p(FadeIn(rt_), FadeIn(mZ.group), rt=1.0)
        zb = mZ.row_box(2, GREY)
        eq2 = M(r"0 = 0", 34, GREY).next_to(mZ.group, DOWN, buff=0.5)
        v2 = VGroup(T("Only a redundant equation.", 23, NAVY), T("Here still ONE solution: x = 2, y = 3", 23, TEAL)).arrange(DOWN, buff=0.12).next_to(eq2, DOWN, buff=0.25)
        self.p(Create(zb), Write(eq2), rt=1.3)
        self.p(FadeIn(v2), rt=0.8)
        self.w(2.0)
        foot = T("Consistent = at least one solution.   Inconsistent = none.", 25, NAVY).move_to([0, -3.4, 0])
        self.p(FadeIn(foot), rt=0.8)
        self.seg_end()

    # ============================================================ S22 pivots, rank and consistency
    def node(self, txt, col, w, h, pos, size=26):
        r = RoundedRectangle(width=w, height=h, corner_radius=0.15, color=col, stroke_width=4).move_to(pos)
        t = T(txt, size, NAVY).move_to(pos)
        return VGroup(r, t)

    def s22(self):
        self.seg_begin("S22")
        self.fade_all()
        self.section("Classifying Solutions")
        dx = -2.4
        top = self.node("Row-reduce  [A | b]  to echelon form", NAVY, 6.4, 0.8, [dx, 2.65, 0])
        q1 = self.node("Row like  [0 0 0 | 5]  ?", ORANGE, 5.2, 0.8, [dx, 1.25, 0])
        a1 = self.node("YES: no solution", RED, 4.0, 0.8, [4.3, 1.25, 0], 24)
        q2 = self.node("Pivot in every variable column?", ORANGE, 6.4, 0.8, [dx, -0.25, 0])
        a2 = self.node("YES: exactly one solution", TEAL, 4.6, 0.8, [4.3, -0.25, 0], 22)
        a3 = self.node("NO: free variables, infinitely many", PURPLE, 6.8, 0.8, [dx, -1.85, 0], 24)
        ar = lambda a, b: Arrow(a, b, color=GREY, stroke_width=4, buff=0.05, max_tip_length_to_length_ratio=0.25)
        self.p(FadeIn(top), rt=0.8)
        self.p(GrowArrow(ar([dx, 2.25, 0], [dx, 1.65, 0])), FadeIn(q1), rt=0.8)
        self.p(GrowArrow(ar([dx + 2.7, 1.25, 0], [2.0, 1.25, 0])), FadeIn(a1), rt=0.8)
        self.p(GrowArrow(ar([dx, 0.85, 0], [dx, 0.15, 0])), FadeIn(q2), rt=0.8)
        self.p(GrowArrow(ar([dx + 3.3, -0.25, 0], [2.0, -0.25, 0])), FadeIn(a2), rt=0.8)
        self.p(GrowArrow(ar([dx, -0.65, 0], [dx, -1.45, 0])), FadeIn(a3), rt=0.8)
        self.w(1.0)
        rk = M(r"\operatorname{rank} = \text{number of pivots}", 34, NAVY).move_to([0, -2.6, 0])
        rl = M(r"\text{consistent} \iff \operatorname{rank}A = \operatorname{rank}[A\,|\,b]", 36, PURPLE).move_to([0, -3.4, 0])
        self.p(FadeIn(rk), rt=0.8)
        self.p(FadeIn(rl), rt=0.8)
        self.seg_end()

    # ============================================================ S23 geometry of the worked example
    def s23(self):
        self.seg_begin("S23")
        self.fade_all(0.5)
        self.section("Geometric Interpretation of Solutions")
        self.set_camera_orientation(phi=62 * DEGREES, theta=15 * DEGREES)
        ax = ThreeDAxes(x_range=[0, 4, 1], y_range=[0, 4, 1], z_range=[0, 5, 1],
                        x_length=3.8, y_length=3.8, z_length=4.4,
                        axis_config={"color": NAVY, "stroke_width": 2.5, "include_tip": False})
        ax.shift(-ax.c2p(1.5, 1.5, 2.0) + 0.0 * OUT)          # centre the scene on the region that matters
        self.ax = ax
        labs = [M(s, 36, NAVY).move_to(ax.c2p(*pos)) for s, pos in
                (("x", (4.4, 0, 0)), ("y", (0, 4.4, 0)), ("z", (0, 0, 5.4)))]
        self.add_fixed_orientation_mobjects(*labs)
        self.p(Create(ax), *[FadeIn(l) for l in labs], rt=1.0)
        P = np.array([1.0, 2.0, 3.0])
        def pl(n, col):
            n = np.array(n, float); n /= np.linalg.norm(n)
            a = np.cross(n, [0, 0, 1.0]) if abs(n[2]) < 0.9 else np.cross(n, [1.0, 0, 0])
            a /= np.linalg.norm(a); b = np.cross(n, a)
            return Surface(lambda u, v: ax.c2p(*(P + u * a + v * b)), u_range=[-1.5, 1.5], v_range=[-1.5, 1.5],
                           resolution=(6, 6), fill_opacity=0.40, stroke_width=1, stroke_color=col,
                           checkerboard_colors=[col, col])
        surf = [pl((1, 1, 1), BLUE), pl((2, 1, 3), TEAL), pl((1, 2, 1), ORANGE)]
        cap = VGroup(*[M(s, 34, c) for s, c in zip(["x+y+z=6", "2x+y+3z=13", "x+2y+z=8"], EQC)]).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        cap.to_corner(UL, buff=0.5).shift(DOWN * 0.55)
        ver = T("Unique solution: (1, 2, 3)", 34, PURPLE, weight=BOLD).to_edge(DOWN, buff=0.7)
        note = T("the point where all three planes meet", 26, GREY).next_to(ver, UP, buff=0.15)
        self.add_fixed_in_frame_mobjects(cap, ver, note)
        self.remove(cap, ver, note)
        self.begin_ambient_camera_rotation(rate=0.05)
        self.p(LaggedStart(*[FadeIn(s) for s in surf], lag_ratio=0.35), FadeIn(cap), rt=2.4)
        dot = Dot3D(ax.c2p(*P), radius=0.13, color=PURPLE)
        self.p(FadeIn(dot, scale=2), FadeIn(ver), FadeIn(note), rt=1.2)
        self.seg_end()
        self.stop_ambient_camera_rotation()

    # ============================================================ S24 summary and credits
    def s24(self):
        self.seg_begin("S24")
        self.fade_all()
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES)
        self.section("Summary and Credits")
        h = T("Three takeaways", 46, PURPLE, weight=BOLD).to_edge(UP, buff=0.9)
        tk = VGroup(
            T("1.  Elementary row operations preserve the solution set.", 30, NAVY),
            T("2.  Forward elimination makes zeros below pivots and forms row-echelon form.", 27, NAVY),
            T("3.  Back substitution solves from the bottom row upwards.", 30, NAVY),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.45).move_to([0, 0.4, 0])
        self.p(FadeIn(h), rt=0.8)
        for t in tk:
            self.p(FadeIn(t, shift=RIGHT * 0.3), rt=1.0)
            self.w(1.0)
        self.w(0.6)
        cr = VGroup(
            T("Gaussian Elimination  -  M3 Animation Video Project", 30, NAVY, weight=BOLD),
            M(r"(x,\,y,\,z) = (1,\,2,\,3)", 46, PURPLE),
            T("Unnati Mehatkar    |    URN: E25B070765", 28, NAVY),
            T("Batch: Neumann    |    Lab: Architecture", 28, NAVY),
            T("Animation: Manim Community Edition (Python)", 26, NAVY),
            T("AI assistance: Claude and OpenAI Codex supported code, scripts and review.", 22, NAVY),
            T("Voice-over: recorded by the student.    Music: none", 24, GREY),
        ).arrange(DOWN, buff=0.35).move_to(ORIGIN)
        self.p(FadeOut(h), FadeOut(tk), FadeIn(cr), rt=0.8)
        self.seg_end()

    # ============================================================ output files (real timeline)
    def write_files(self):
        def ts(t): return f"{int(t // 60)}:{t % 60:05.2f}"
        out = Path(__file__).resolve().parent
        total = self.log[-1][3]
        L = ["GAUSSIAN ELIMINATION - SCENE TIMESTAMPS (taken from the render timeline)",
             f"Total duration: {ts(total)}  ({total:.1f} s)", ""]
        for sid, title, t0, t1 in self.log:
            L.append(f"{sid}  {ts(t0)} - {ts(t1)}  ({t1 - t0:.1f} s)  {title}")
        if self.overruns:
            L += ["", "WARNING - animation longer than planned in: " + ", ".join(f"{a} (+{b}s)" for a, b in self.overruns)]
        (out / "GaussianElimination_Scene_Timestamps.txt").write_text("\n".join(L) + "\n")
        V = ["GAUSSIAN ELIMINATION - VOICE-OVER SCRIPT (12 recording segments)",
             "Record each numbered block as one manageable take. Scene timestamps are taken from the final render.",
             "[PAUSE n s] = stay silent during the displayed calculation. Speak only what is on screen.",
             f"Total video length: {ts(total)}", "=" * 78, ""]
        by_id = {sid: (title, t0, t1, SEG[i][3]) for i, (sid, title, t0, t1) in enumerate(self.log)}
        for number, (group_title, ids) in enumerate(VOICE_GROUPS, 1):
            first, last = by_id[ids[0]], by_id[ids[-1]]
            group_text, group_words, group_pauses = [], 0, 0.0
            V.append(f"RECORDING SEGMENT {number:02d} — {group_title} [{ts(first[1])} - {ts(last[2])}]")
            for sid in ids:
                title, t0, t1, narration = by_id[sid]
                pauses = sum(float(x) for x in re.findall(r"\[PAUSE (\d+(?:\.\d+)?)s\]", narration))
                spoken = re.sub(r"\[PAUSE[^\]]*\]", "", narration)
                words = len(spoken.split())
                group_words += words
                group_pauses += pauses
                group_text.append(narration)
                V += [f"  [{ts(t0)} - {ts(t1)}] {sid} — {title}", f"  {narration}"]
            approx = group_words / WORDS_PER_SEC + group_pauses
            V += [f"  Segment total: {group_words} words; about {approx:.0f} s speech and pauses in a {last[2] - first[1]:.0f} s window.", ""]
        (out / "GaussianElimination_Voiceover_Script.txt").write_text("\n".join(V) + "\n")
        print("TOTAL", ts(total), "OVERRUNS", self.overruns)
