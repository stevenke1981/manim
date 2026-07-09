from __future__ import annotations

import json
from pathlib import Path

from manimlib import *


ROOT = Path(__file__).resolve().parent
TIMINGS_PATH = ROOT / "output" / "timings.json"
FONT = "Microsoft JhengHei"


def load_durations() -> list[float]:
    if TIMINGS_PATH.exists():
        data = json.loads(TIMINGS_PATH.read_text(encoding="utf-8-sig"))
        return [float(item["duration"]) for item in data["segments"]]
    return [6.0] * 13


class XYEqualsKTeaching(Scene):
    def make_label(self, text, size=28, color=WHITE):
        return Text(text, font=FONT, font_size=size).set_color(color)

    def caption(self, text):
        mob = Text(" ", font=FONT, font_size=1)
        mob.set_opacity(0)
        mob.to_edge(DOWN, buff=0.25)
        return mob

    def hyperbola(self, axes, k, x_min, x_max, color):
        return axes.get_graph(
            lambda x: k / x,
            x_range=(x_min, x_max, 0.05),
            color=color,
            use_smoothing=True,
        ).set_stroke(color, width=5)

    def axes_zero_graph(self, axes):
        x_axis = Line(axes.c2p(-4, 0), axes.c2p(4, 0)).set_stroke(GREEN, 7)
        y_axis = Line(axes.c2p(0, -3.2), axes.c2p(0, 3.2)).set_stroke(GREEN, 7)
        return VGroup(x_axis, y_axis)

    def timed_play(self, duration, *animations, run_time=0.8):
        run_time = min(run_time, max(duration - 0.05, 0.05))
        if animations:
            self.play(*animations, run_time=run_time)
        if duration > run_time:
            self.wait(duration - run_time)

    def update_caption(self, old_caption, new_text, duration, *animations, run_time=0.8):
        new_caption = self.caption(new_text)
        self.timed_play(
            duration,
            FadeTransform(old_caption, new_caption),
            *animations,
            run_time=run_time,
        )
        return new_caption

    def construct(self):
        durations = load_durations()

        title = self.make_label("xy = k 的三種圖形", size=36, color=YELLOW)
        nav_pos = self.make_label("k > 0", size=26, color=GREEN)
        nav_zero = self.make_label("k = 0", size=26, color=YELLOW)
        nav_neg = self.make_label("k < 0", size=26, color=RED)
        case_nav = VGroup(nav_pos, nav_zero, nav_neg).arrange(RIGHT, buff=0.55)
        case_nav.next_to(title, DOWN, buff=0.18).align_to(title, LEFT)
        title_group = VGroup(title, case_nav).to_corner(UL, buff=0.45)
        nav_pos.set_opacity(0)
        nav_zero.set_opacity(0)
        nav_neg.set_opacity(0)
        cap = self.caption("今天我們用 xy = k，看 k 的符號怎麼決定圖形。")
        self.timed_play(durations[0], FadeIn(title_group), FadeIn(cap), run_time=1.0)

        equation = self.make_label("xy = k    ->    y = k / x", size=36, color=WHITE)
        equation.next_to(title_group, DOWN, buff=0.35)
        note = self.make_label("x 不等於 0 時，是反比例曲線", size=26, color=GREY_B)
        note.next_to(equation, DOWN, buff=0.2)
        cap = self.update_caption(
            cap,
            "改寫成 y = k / x，就能看出反比例的形狀。",
            durations[1],
            FadeIn(equation),
            FadeIn(note),
            run_time=1.0,
        )

        sign_table = VGroup(
            self.make_label("同號：xy > 0", size=30, color=GREEN),
            self.make_label("異號：xy < 0", size=30, color=RED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        sign_table.to_edge(RIGHT, buff=0.7).shift(UP * 0.3)
        cap = self.update_caption(
            cap,
            "重點是乘積的符號：同號為正，異號為負。",
            durations[2],
            FadeIn(sign_table, RIGHT),
            run_time=0.9,
        )

        axes = Axes((-4, 4, 1), (-3, 3, 1), height=5.4, width=8.0)
        axes.add_coordinate_labels(font_size=18)
        axes.to_edge(LEFT, buff=0.75).shift(DOWN * 0.15)
        q1 = self.make_label("第一象限", size=21, color=GREEN).move_to(axes.c2p(2.6, 2.35))
        q3 = self.make_label("第三象限", size=21, color=GREEN).move_to(axes.c2p(-2.65, -2.35))
        pos_graph = VGroup(
            self.hyperbola(axes, 1, 0.28, 4, GREEN),
            self.hyperbola(axes, 1, -4, -0.28, GREEN),
        )
        pos_label = self.make_label("k > 0：x, y 同號", size=29, color=GREEN)
        pos_label.to_edge(RIGHT, buff=0.8).shift(UP * 1.4)
        cap = self.update_caption(
            cap,
            "k > 0 時，圖形在第一象限和第三象限。",
            durations[3],
            FadeOut(sign_table),
            FadeOut(note),
            FadeOut(equation),
            nav_pos.animate.set_opacity(1),
            FadeIn(axes),
            ShowCreation(pos_graph),
            FadeIn(VGroup(q1, q3)),
            FadeIn(pos_label),
            run_time=1.4,
        )

        asymptote_x = Line(axes.c2p(-4, 0), axes.c2p(4, 0)).set_stroke(YELLOW, 3, opacity=0.7)
        asymptote_y = Line(axes.c2p(0, -3), axes.c2p(0, 3)).set_stroke(YELLOW, 3, opacity=0.7)
        asym_label = self.make_label("x 軸、y 軸是漸近線", size=25, color=YELLOW)
        asym_label.to_edge(RIGHT, buff=0.8).shift(UP * 0.45)
        cap = self.update_caption(
            cap,
            "曲線會靠近座標軸，但不會碰到它們。",
            durations[4],
            ShowCreation(VGroup(asymptote_x, asymptote_y)),
            FadeIn(asym_label),
            run_time=0.9,
        )

        bigger_pos = VGroup(
            self.hyperbola(axes, 2, 0.5, 4, BLUE),
            self.hyperbola(axes, 2, -4, -0.5, BLUE),
        )
        bigger_label = self.make_label("k 變大：離原點更遠", size=25, color=BLUE)
        bigger_label.next_to(asym_label, DOWN, buff=0.3)
        cap = self.update_caption(
            cap,
            "k 變大會把曲線推遠，但正負象限不變。",
            durations[5],
            ShowCreation(bigger_pos),
            FadeIn(bigger_label),
            run_time=1.0,
        )

        zero_graph = self.axes_zero_graph(axes)
        zero_label = self.make_label("k = 0：x = 0 或 y = 0", size=29, color=GREEN)
        zero_label.to_edge(RIGHT, buff=0.8).shift(UP * 1.4)
        zero_equation = self.make_label("xy = 0  ->  x = 0  或  y = 0", size=30, color=WHITE)
        zero_equation.to_edge(RIGHT, buff=0.55).shift(DOWN * 0.15)
        cap = self.update_caption(
            cap,
            "k = 0 時，xy = 0 代表 x = 0 或 y = 0。",
            durations[6],
            FadeOut(pos_graph),
            FadeOut(bigger_pos),
            FadeOut(VGroup(q1, q3, pos_label, asym_label, bigger_label)),
            nav_zero.animate.set_opacity(1),
            FadeIn(zero_graph),
            FadeIn(zero_equation),
            FadeIn(zero_label),
            run_time=1.2,
        )

        zero_note = self.make_label("兩條座標軸全部成立", size=26, color=GREEN)
        zero_note.next_to(zero_label, DOWN, buff=0.35)
        cap = self.update_caption(
            cap,
            "所以這一格的圖形，是兩條座標軸。",
            durations[7],
            Indicate(zero_graph),
            FadeIn(zero_note),
            run_time=0.9,
        )

        neg_graph = VGroup(
            self.hyperbola(axes, -1, -4, -0.28, RED),
            self.hyperbola(axes, -1, 0.28, 4, RED),
        )
        q2 = self.make_label("第二象限", size=21, color=RED).move_to(axes.c2p(-2.65, 2.35))
        q4 = self.make_label("第四象限", size=21, color=RED).move_to(axes.c2p(2.6, -2.35))
        neg_label = self.make_label("k < 0：x, y 異號", size=29, color=RED)
        neg_label.to_edge(RIGHT, buff=0.8).shift(UP * 1.4)
        cap = self.update_caption(
            cap,
            "k < 0 時，x 和 y 必須異號。",
            durations[8],
            FadeOut(zero_graph),
            FadeOut(VGroup(zero_label, zero_note, zero_equation)),
            nav_neg.animate.set_opacity(1),
            ShowCreation(neg_graph),
            FadeIn(VGroup(q2, q4)),
            FadeIn(neg_label),
            run_time=1.1,
        )

        neg_note = self.make_label("每一點都滿足 xy < 0", size=26, color=RED)
        neg_note.next_to(neg_label, DOWN, buff=0.35)
        cap = self.update_caption(
            cap,
            "因此曲線在第二象限和第四象限。",
            durations[9],
            FadeIn(neg_note),
            run_time=0.7,
        )

        summary = VGroup(
            self.make_label("k > 0：第一、第三象限", size=28, color=GREEN),
            self.make_label("k = 0：x 軸和 y 軸", size=28, color=YELLOW),
            self.make_label("k < 0：第二、第四象限", size=28, color=RED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        summary.to_edge(RIGHT, buff=0.6).shift(UP * 1.25)
        cap = self.update_caption(
            cap,
            "三種情況合起來看，差別只在 k 的符號。",
            durations[10],
            FadeOut(VGroup(q2, q4, neg_label, neg_note)),
            FadeIn(summary),
            run_time=0.9,
        )

        memory = VGroup(
            self.make_label("看 k 的符號 -> 看 xy 的符號", size=25, color=BLUE),
            self.make_label("-> 看象限", size=25, color=BLUE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        memory.next_to(summary, DOWN, buff=0.4).align_to(summary, LEFT)
        cap = self.update_caption(
            cap,
            "記法：看 k 的符號，就知道點會落在哪些象限。",
            durations[11],
            FadeIn(memory),
            run_time=0.8,
        )

        final_note = VGroup(
            self.make_label("注意：k = 0 要回到原式", size=24, color=YELLOW),
            self.make_label("xy = 0 判斷", size=24, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        final_note.next_to(memory, DOWN, buff=0.32).align_to(memory, LEFT)
        cap = self.update_caption(
            cap,
            "最後要小心，k = 0 的時候，要回到原式 xy = 0。",
            durations[12],
            FadeIn(final_note),
            run_time=0.8,
        )
        self.play(FadeOut(cap), run_time=0.4)
