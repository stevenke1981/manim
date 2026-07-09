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
    return [6.0] * 15


class FactoringQuadraticTeaching(Scene):
    def make_text(self, text, size=30, color=WHITE):
        return Text(text, font=FONT, font_size=size).set_color(color)

    def hidden_caption(self):
        mob = Text(" ", font=FONT, font_size=1)
        mob.set_opacity(0)
        return mob

    def timed_play(self, duration, *animations, run_time=0.8):
        run_time = min(run_time, max(duration - 0.05, 0.05))
        if animations:
            self.play(*animations, run_time=run_time)
        if duration > run_time:
            self.wait(duration - run_time)

    def update_step(self, old_caption, duration, *animations, run_time=0.8):
        new_caption = self.hidden_caption()
        self.timed_play(duration, FadeTransform(old_caption, new_caption), *animations, run_time=run_time)
        return new_caption

    def line_group(self, lines, size=30, colors=None, buff=0.26):
        items = []
        for i, text in enumerate(lines):
            color = colors[i] if colors and i < len(colors) else WHITE
            items.append(self.make_text(text, size=size, color=color))
        return VGroup(*items).arrange(DOWN, aligned_edge=LEFT, buff=buff)

    def place_left(self, mob, y=0.2):
        mob.move_to(LEFT * 3.15 + UP * y)
        return mob

    def place_right(self, mob, y=0.2):
        mob.move_to(RIGHT * 3.15 + UP * y)
        return mob

    def construct(self):
        durations = load_durations()
        chalk_green = "#9ED36A"
        chalk_blue = "#66D9EF"
        chalk_red = "#FF6B5E"

        title = self.make_text("因式分解法解一元二次方程式", size=38, color=YELLOW)
        credit = self.make_text("stevenke1981 製作", size=24, color=GREY_B)
        title_group = VGroup(title, credit).arrange(DOWN, buff=0.18)
        title_group.to_edge(UP, buff=0.35)
        cap = self.hidden_caption()
        self.timed_play(durations[0], FadeIn(title_group), FadeIn(cap), run_time=1.0)

        rule = self.line_group(
            ["零乘積性質", "A x B = 0", "=> A = 0 或 B = 0"],
            size=35,
            colors=[YELLOW, WHITE, chalk_green],
            buff=0.28,
        )
        rule.move_to(UP * 0.55)
        cap = self.update_step(cap, durations[1], FadeIn(rule, RIGHT), run_time=1.0)

        number_demo = self.line_group(
            ["5 x 0 = 0", "0 x 7 = 0", "0 x 0 = 0", "至少一個因數是 0"],
            size=30,
            colors=[WHITE, WHITE, WHITE, chalk_blue],
            buff=0.22,
        )
        number_demo.next_to(rule, DOWN, buff=0.55)
        cap = self.update_step(cap, durations[2], FadeIn(number_demo), run_time=0.9)

        example_title = self.make_text("例題一", size=30, color=YELLOW)
        example_eq = self.make_text("(x - 1)(x + 2) = 0", size=36, color=WHITE)
        example = VGroup(example_title, example_eq).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        self.place_left(example, y=0.45)
        split = self.line_group(
            ["x - 1 = 0", "或", "x + 2 = 0"],
            size=32,
            colors=[chalk_green, GREY_B, chalk_green],
            buff=0.2,
        )
        split.next_to(example, DOWN, buff=0.45).align_to(example, LEFT)
        cap = self.update_step(
            cap,
            durations[3],
            FadeOut(number_demo),
            FadeOut(rule),
            FadeIn(example),
            FadeIn(split),
            run_time=1.1,
        )

        solve = self.line_group(
            ["x - 1 = 0  ->  x = 1", "x + 2 = 0  ->  x = -2", "答案：x = 1 或 x = -2"],
            size=31,
            colors=[WHITE, WHITE, YELLOW],
            buff=0.25,
        )
        self.place_right(solve, y=0.1)
        cap = self.update_step(cap, durations[4], FadeIn(solve, RIGHT), run_time=1.0)

        note = self.line_group(
            ["不是同時成立", "而是兩個可能的解"],
            size=30,
            colors=[chalk_red, chalk_red],
            buff=0.22,
        )
        note.next_to(solve, DOWN, buff=0.55).align_to(solve, LEFT)
        cap = self.update_step(cap, durations[5], FadeIn(note), Indicate(solve[-1]), run_time=0.9)

        check = self.line_group(
            ["代入 x = 1：", "(1 - 1)(1 + 2) = 0 x 3 = 0", "代入 x = -2：", "(-2 - 1)(-2 + 2) = -3 x 0 = 0"],
            size=26,
            colors=[chalk_blue, WHITE, chalk_blue, WHITE],
            buff=0.2,
        )
        self.place_right(check, y=0.15)
        cap = self.update_step(cap, durations[6], FadeOut(note), FadeTransform(solve, check), run_time=1.0)

        example2_title = self.make_text("例題二：先分解", size=30, color=YELLOW)
        poly = self.make_text("x² + x - 2 = 0", size=36, color=WHITE)
        factor = self.make_text("(x + 2)(x - 1) = 0", size=36, color=chalk_green)
        example2 = VGroup(example2_title, poly, factor).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        self.place_left(example2, y=0.35)
        cap = self.update_step(
            cap,
            durations[7],
            FadeOut(VGroup(example, split, check)),
            FadeIn(example2),
            run_time=1.1,
        )

        split2 = self.line_group(
            ["x + 2 = 0", "或", "x - 1 = 0"],
            size=32,
            colors=[chalk_green, GREY_B, chalk_green],
            buff=0.2,
        )
        self.place_right(split2, y=0.65)
        cap = self.update_step(cap, durations[8], FadeIn(split2, RIGHT), run_time=0.9)

        solve2 = self.line_group(
            ["x + 2 = 0  ->  x = -2", "x - 1 = 0  ->  x = 1", "答案：x = -2 或 x = 1"],
            size=30,
            colors=[WHITE, WHITE, YELLOW],
            buff=0.24,
        )
        solve2.next_to(split2, DOWN, buff=0.55).align_to(split2, LEFT)
        cap = self.update_step(cap, durations[9], FadeIn(solve2), run_time=0.9)

        example3 = self.line_group(
            ["例題三：有公因式", "x² - 3x = 0", "x(x - 3) = 0"],
            size=34,
            colors=[YELLOW, WHITE, chalk_green],
            buff=0.25,
        )
        self.place_left(example3, y=0.35)
        cap = self.update_step(cap, durations[10], FadeOut(VGroup(example2, split2, solve2)), FadeIn(example3), run_time=1.0)

        solve3 = self.line_group(
            ["x = 0", "或", "x - 3 = 0  ->  x = 3", "答案：x = 0 或 x = 3"],
            size=31,
            colors=[WHITE, GREY_B, WHITE, YELLOW],
            buff=0.22,
        )
        self.place_right(solve3, y=0.15)
        cap = self.update_step(cap, durations[11], FadeIn(solve3), run_time=0.9)

        warning = self.line_group(
            ["小心！", "一定要先變成：", "乘積 = 0", "A x B = 1 不能直接拆"],
            size=32,
            colors=[chalk_red, WHITE, YELLOW, chalk_red],
            buff=0.24,
        )
        self.place_left(warning, y=0.3)
        cap = self.update_step(cap, durations[12], FadeOut(solve3), FadeTransform(example3, warning), run_time=1.0)

        steps = self.line_group(
            ["解題流程", "1. 移項成等於 0", "2. 因式分解", "3. 每個因式分別等於 0", "4. 解出 x 並檢查"],
            size=30,
            colors=[YELLOW, WHITE, WHITE, WHITE, WHITE],
            buff=0.2,
        )
        self.place_right(steps, y=0.05)
        cap = self.update_step(cap, durations[13], FadeTransform(warning, steps), run_time=1.0)

        final = self.line_group(
            ["關鍵記法", "因式分解", "+", "零乘積性質", "=> 找到所有解"],
            size=33,
            colors=[YELLOW, chalk_green, WHITE, chalk_blue, YELLOW],
            buff=0.18,
        )
        final.move_to(UP * 0.1)
        cap = self.update_step(cap, durations[14], FadeTransform(steps, final), run_time=1.0)
        self.play(FadeOut(cap), run_time=0.4)
