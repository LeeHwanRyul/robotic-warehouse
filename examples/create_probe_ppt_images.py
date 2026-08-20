"""Create PPT-ready PNG cards for PGCT canonical probe examples.

The generated cards are 16:9 images intended to be inserted directly into a
presentation.

Example:
    python examples/create_probe_ppt_images.py --output output/probes
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFont


W, H = 1920, 1080
MARGIN = 86

BG = (247, 248, 250)
INK = (25, 31, 42)
MUTED = (83, 92, 108)
LIGHT = (234, 238, 244)
LINE = (204, 211, 222)
BLUE = (51, 103, 214)
RED = (214, 78, 68)
GREEN = (51, 150, 96)
ORANGE = (224, 146, 54)
PURPLE = (132, 91, 190)
YELLOW = (242, 190, 72)
DARK = (52, 59, 72)
WHITE = (255, 255, 255)


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = (
        ["C:/Windows/Fonts/malgunbd.ttf", "C:/Windows/Fonts/malgun.ttf"]
        if bold
        else ["C:/Windows/Fonts/malgun.ttf", "C:/Windows/Fonts/arial.ttf"]
    )
    for name in names:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


F_TITLE = font(54, True)
F_SUBTITLE = font(28)
F_SECTION = font(31, True)
F_BODY = font(26)
F_SMALL = font(22)
F_LABEL = font(21, True)
F_FORMULA = font(25)
F_CARD_TITLE = font(30, True)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> Tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    fnt: ImageFont.ImageFont,
    max_width: int,
) -> List[str]:
    words = text.split()
    lines: List[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if text_size(draw, candidate, fnt)[0] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: Tuple[int, int],
    text: str,
    fnt: ImageFont.ImageFont,
    fill: Tuple[int, int, int],
    max_width: int,
    line_gap: int = 10,
) -> int:
    x, y = xy
    lines = wrap_text(draw, text, fnt, max_width)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += text_size(draw, line, fnt)[1] + line_gap
    return y


def rect(
    draw: ImageDraw.ImageDraw,
    box: Tuple[int, int, int, int],
    fill: Tuple[int, int, int] = WHITE,
    outline: Tuple[int, int, int] = LINE,
    width: int = 2,
    radius: int = 18,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def pill(
    draw: ImageDraw.ImageDraw,
    xy: Tuple[int, int],
    text: str,
    fill: Tuple[int, int, int],
    fg: Tuple[int, int, int] = WHITE,
) -> Tuple[int, int, int, int]:
    x, y = xy
    tw, th = text_size(draw, text, F_LABEL)
    box = (x, y, x + tw + 34, y + th + 18)
    draw.rounded_rectangle(box, radius=18, fill=fill)
    draw.text((x + 17, y + 8), text, font=F_LABEL, fill=fg)
    return box


def title(draw: ImageDraw.ImageDraw, heading: str, subtitle: str, tag: str) -> None:
    draw.text((MARGIN, 58), heading, font=F_TITLE, fill=INK)
    draw.text((MARGIN, 128), subtitle, font=F_SUBTITLE, fill=MUTED)
    pill(draw, (W - MARGIN - 240, 66), tag, BLUE)


def centered_text(
    draw: ImageDraw.ImageDraw,
    center: Tuple[float, float],
    text: str,
    fnt: ImageFont.ImageFont,
    fill: Tuple[int, int, int],
) -> None:
    tw, th = text_size(draw, text, fnt)
    draw.text((center[0] - tw / 2, center[1] - th / 2), text, font=fnt, fill=fill)


def arrow(
    draw: ImageDraw.ImageDraw,
    start: Tuple[int, int],
    end: Tuple[int, int],
    fill: Tuple[int, int, int] = DARK,
    width: int = 5,
) -> None:
    draw.line((*start, *end), fill=fill, width=width)
    sx, sy = start
    ex, ey = end
    dx, dy = ex - sx, ey - sy
    length = max((dx * dx + dy * dy) ** 0.5, 1.0)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    size = 18
    points = [
        (ex, ey),
        (ex - ux * size + px * size * 0.55, ey - uy * size + py * size * 0.55),
        (ex - ux * size - px * size * 0.55, ey - uy * size - py * size * 0.55),
    ]
    draw.polygon(points, fill=fill)


def grid(
    draw: ImageDraw.ImageDraw,
    origin: Tuple[int, int],
    rows: int,
    cols: int,
    cell: int,
    obstacles: Iterable[Tuple[int, int]] = (),
    targets: Iterable[Tuple[int, int, Tuple[int, int, int], str]] = (),
    agent: Tuple[int, int, str] | None = None,
    path: Sequence[Tuple[int, int]] = (),
) -> None:
    ox, oy = origin
    for r in range(rows):
        for c in range(cols):
            box = (ox + c * cell, oy + r * cell, ox + (c + 1) * cell, oy + (r + 1) * cell)
            draw.rectangle(box, fill=WHITE, outline=(216, 222, 232), width=2)
    for r, c in obstacles:
        box = (ox + c * cell, oy + r * cell, ox + (c + 1) * cell, oy + (r + 1) * cell)
        draw.rectangle(box, fill=DARK)
    for r, c, color, label in targets:
        cx = ox + c * cell + cell / 2
        cy = oy + r * cell + cell / 2
        rad = cell * 0.31
        draw.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=color)
        centered_text(draw, (cx, cy), label, F_LABEL, WHITE)
    if len(path) >= 2:
        points = [(ox + c * cell + cell / 2, oy + r * cell + cell / 2) for r, c in path]
        draw.line(points, fill=BLUE, width=8, joint="curve")
    if agent is not None:
        r, c, label = agent
        cx = ox + c * cell + cell / 2
        cy = oy + r * cell + cell / 2
        rad = cell * 0.36
        draw.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=(36, 44, 58), outline=INK, width=3)
        centered_text(draw, (cx, cy), label, F_LABEL, WHITE)


def action_bar(
    draw: ImageDraw.ImageDraw,
    xy: Tuple[int, int],
    label: str,
    values: Sequence[Tuple[str, float, Tuple[int, int, int]]],
) -> None:
    x, y = xy
    draw.text((x, y), label, font=F_LABEL, fill=INK)
    y += 38
    max_w = 460
    for name, value, color in values:
        draw.text((x, y), name, font=F_SMALL, fill=MUTED)
        bx = x + 124
        by = y + 6
        draw.rounded_rectangle((bx, by, bx + max_w, by + 20), radius=10, fill=LIGHT)
        draw.rounded_rectangle((bx, by, bx + int(max_w * value), by + 20), radius=10, fill=color)
        draw.text((bx + max_w + 18, y - 2), f"{value:.2f}", font=F_SMALL, fill=INK)
        y += 42


def base() -> Tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (W, H), BG)
    return image, ImageDraw.Draw(image)


def save(image: Image.Image, output: Path, name: str) -> None:
    output.mkdir(parents=True, exist_ok=True)
    image.save(output / name)


def slide_00(output: Path) -> None:
    image, draw = base()
    title(draw, "PGCT Probe Bank", "발표용 예시 시험문제 이미지 세트", "overview")
    left = (MARGIN, 230, 900, 930)
    right = (990, 230, W - MARGIN, 930)
    rect(draw, left)
    rect(draw, right)
    draw.text((left[0] + 40, left[1] + 34), "문서에서 지켜야 할 조건", font=F_SECTION, fill=INK)
    bullets = [
        "모든 agent에게 같은 canonical recurrent history를 준다.",
        "probe hidden state는 h0^Q = 0에서 시작한다.",
        "true objective label z_i 또는 C_ij^obj를 입력으로 쓰지 않는다.",
        "결과는 action distribution fingerprint이고, distance는 D_ij^Q로 요약한다.",
    ]
    y = left[1] + 105
    for b in bullets:
        y = draw_wrapped(draw, (left[0] + 58, y), f"- {b}", F_BODY, INK, left[2] - left[0] - 110, 8) + 20
    draw.text((right[0] + 40, right[1] + 34), "추가한 발표용 프로브", font=F_SECTION, fill=INK)
    items = [
        "Target preference",
        "Pickup / drop decision",
        "Recurrent memory at junction",
        "Blocked route choice",
        "Finite-probe margin check",
        "DQ vs transfer utility",
        "Non-identifiable failure case",
    ]
    y = right[1] + 105
    for idx, item in enumerate(items, 1):
        pill(draw, (right[0] + 58, y), f"{idx:02d}", [BLUE, GREEN, ORANGE, PURPLE, RED, DARK, YELLOW][idx - 1], INK if idx == 7 else WHITE)
        draw.text((right[0] + 125, y + 6), item, font=F_BODY, fill=INK)
        y += 72
    save(image, output, "00_probe_bank_overview.png")


def slide_01(output: Path) -> None:
    image, draw = base()
    title(draw, "Same Exam Sheet", "canonical recurrent probe의 핵심 아이디어", "concept")
    rect(draw, (MARGIN, 250, W - MARGIN, 860))
    y = 300
    boxes = [
        ("Canonical input history Q", "xi_m = [obs_1, action_1, ..., obs_L]", BLUE),
        ("Reset", "probe hidden state h0^Q = 0", GREEN),
        ("Actor i / Actor j", "same Q, side-effect-free forward pass", ORANGE),
        ("Score", "D_ij^Q = average JS(action distributions)", PURPLE),
    ]
    x = 150
    for idx, (head, body, color) in enumerate(boxes):
        rect(draw, (x, y, x + 360, y + 210), fill=(255, 255, 255), outline=color, width=4)
        draw.text((x + 28, y + 28), head, font=F_CARD_TITLE, fill=INK)
        draw_wrapped(draw, (x + 28, y + 90), body, F_BODY, MUTED, 304)
        if idx < len(boxes) - 1:
            arrow(draw, (x + 380, y + 105), (x + 455, y + 105), fill=DARK)
        x += 430
    note = "공정한 비교를 위해 online hidden state와 rollout history를 섞지 않는다."
    draw_wrapped(draw, (150, 620), note, F_SECTION, INK, 1500)
    draw_wrapped(
        draw,
        (150, 705),
        "PPT 설명 문장: '두 학생에게 같은 시험지를 주듯, 모든 agent에게 동일한 recurrent history를 replay해서 행동 분포만 비교합니다.'",
        F_BODY,
        MUTED,
        1500,
    )
    save(image, output, "01_same_exam_sheet.png")


def slide_02(output: Path) -> None:
    image, draw = base()
    title(draw, "Probe 01 - Target Preference", "task-informed but label-free target 선택 문제", "probe")
    grid(draw, (130, 245), 7, 7, 78, obstacles=[(2, 2), (3, 2), (4, 2)], targets=[(1, 5, BLUE, "A"), (5, 5, RED, "B")], agent=(3, 1, "i"), path=[(3, 1), (3, 3), (2, 4), (1, 5)])
    rect(draw, (830, 245, 1790, 865))
    draw.text((870, 285), "시험문제", font=F_SECTION, fill=INK)
    prompt = "같은 local history에서 agent가 target type A와 B 중 어느 방향으로 행동 확률을 더 배분하는가?"
    y = draw_wrapped(draw, (870, 340), prompt, F_BODY, INK, 850)
    y += 24
    draw.text((870, y), "입력", font=F_LABEL, fill=BLUE)
    y = draw_wrapped(draw, (870, y + 40), "target/obstacle/agent geometry만 사용한다. true z_i나 same-objective label은 사용하지 않는다.", F_BODY, MUTED, 840)
    y += 24
    action_bar(
        draw,
        (870, y),
        "예시 응답 분포",
        [("UP", 0.08, LINE), ("RIGHT", 0.63, BLUE), ("DOWN", 0.11, LINE), ("NOOP", 0.18, ORANGE)],
    )
    draw.text((120, 850), "목적: objective와 관련된 행동 fingerprint를 만든다.", font=F_BODY, fill=INK)
    save(image, output, "02_probe_target_preference.png")


def slide_03(output: Path) -> None:
    image, draw = base()
    title(draw, "Probe 02 - Pickup / Drop Decision", "requested shelf와 goal 주변에서 TOGGLE_LOAD 반응 보기", "probe")
    grid(draw, (130, 240), 7, 7, 78, obstacles=[(1, 1), (1, 2), (5, 4)], targets=[(3, 3, YELLOW, "S"), (5, 5, GREEN, "G")], agent=(3, 3, "i"))
    rect(draw, (830, 240, 1790, 878))
    draw.text((870, 280), "시험문제", font=F_SECTION, fill=INK)
    y = draw_wrapped(draw, (870, 336), "agent가 requested shelf 위에 있거나 goal 근처에 있을 때, load/drop action probability가 task state에 맞게 올라가는가?", F_BODY, INK, 850)
    y += 28
    draw.text((870, y), "측정", font=F_LABEL, fill=BLUE)
    y = draw_wrapped(draw, (870, y + 40), "p_i(TOGGLE_LOAD | Q)와 p_j(TOGGLE_LOAD | Q)를 비교하고 JS divergence에 포함한다.", F_BODY, MUTED, 840)
    y += 24
    action_bar(
        draw,
        (870, y),
        "예시 응답 분포",
        [("TOGGLE", 0.71, GREEN), ("RIGHT", 0.10, LINE), ("LEFT", 0.06, LINE), ("NOOP", 0.13, ORANGE)],
    )
    draw.text((120, 850), "좋은 이유: 단순 이동보다 reward-objective signal에 민감하다.", font=F_BODY, fill=INK)
    save(image, output, "03_probe_pickup_drop.png")


def slide_04(output: Path) -> None:
    image, draw = base()
    title(draw, "Probe 03 - Recurrent Memory", "초기 관측 단서가 나중의 junction 행동에 남는지 확인", "probe")
    rect(draw, (100, 245, 720, 850))
    rect(draw, (780, 245, 1400, 850))
    rect(draw, (1460, 245, 1818, 850))
    draw.text((130, 285), "Frame 1", font=F_SECTION, fill=INK)
    grid(draw, (180, 360), 5, 5, 70, targets=[(1, 3, BLUE, "A")], agent=(3, 1, "i"))
    draw.text((810, 285), "Frame L", font=F_SECTION, fill=INK)
    grid(draw, (860, 360), 5, 5, 70, obstacles=[(2, 2)], targets=[(1, 4, BLUE, "A"), (3, 4, RED, "B")], agent=(2, 1, "i"))
    arrow(draw, (720, 540), (780, 540), fill=DARK)
    draw.text((1495, 285), "Question", font=F_SECTION, fill=INK)
    y = draw_wrapped(draw, (1495, 345), "초기 frame에서 본 단서가 hidden state에 남아 junction에서 action distribution을 바꾸는가?", F_BODY, INK, 285)
    y += 36
    draw_wrapped(draw, (1495, y), "D_ij^Q는 여러 recurrent step의 JS divergence를 평균한다.", F_SMALL, MUTED, 285)
    draw.text((120, 910), "좋은 이유: recurrent policy 비교에서 online history 차이를 제거하고 memory-dependent behavior만 본다.", font=F_BODY, fill=INK)
    save(image, output, "04_probe_recurrent_memory.png")


def slide_05(output: Path) -> None:
    image, draw = base()
    title(draw, "Probe 04 - Blocked Route Choice", "장애물 때문에 같은 target도 다른 action sequence를 요구하는 문제", "probe")
    grid(
        draw,
        (135, 230),
        8,
        8,
        72,
        obstacles=[(2, 3), (3, 3), (4, 3), (5, 3), (5, 4), (5, 5)],
        targets=[(1, 6, BLUE, "T")],
        agent=(6, 1, "i"),
        path=[(6, 1), (6, 2), (6, 3), (6, 4), (4, 5), (2, 6), (1, 6)],
    )
    rect(draw, (840, 230, 1790, 875))
    draw.text((880, 270), "시험문제", font=F_SECTION, fill=INK)
    y = draw_wrapped(draw, (880, 330), "단순히 target이 보이는지가 아니라, local geometry 아래에서 어느 route action을 선택하는지 비교한다.", F_BODY, INK, 835)
    y += 24
    draw.text((880, y), "label-free 조건", font=F_LABEL, fill=BLUE)
    y = draw_wrapped(draw, (880, y + 40), "obstacle map과 visible task objects는 사용 가능하지만, hidden objective label은 사용하지 않는다.", F_BODY, MUTED, 835)
    y += 30
    action_bar(
        draw,
        (880, y),
        "예시 응답 분포",
        [("RIGHT", 0.48, BLUE), ("UP", 0.34, GREEN), ("DOWN", 0.05, LINE), ("NOOP", 0.13, ORANGE)],
    )
    save(image, output, "05_probe_blocked_route.png")


def slide_06(output: Path) -> None:
    image, draw = base()
    title(draw, "Probe 05 - Finite Probe Margin", "M개의 probe로 pair distance가 안정되는지 보는 문제", "diagnostic")
    rect(draw, (110, 235, 1810, 880))
    draw.text((155, 280), "시험문제", font=F_SECTION, fill=INK)
    draw_wrapped(draw, (155, 335), "M개의 canonical history를 샘플링했을 때 same-objective pair와 different-objective pair의 distance interval이 분리되는가?", F_BODY, INK, 1540)
    axis_y = 590
    axis_x0 = 230
    axis_x1 = 1660
    draw.line((axis_x0, axis_y, axis_x1, axis_y), fill=DARK, width=4)
    for x, label in [(axis_x0, "0.0"), ((axis_x0 + axis_x1) // 2, "0.5"), (axis_x1, "1.0")]:
        draw.line((x, axis_y - 12, x, axis_y + 12), fill=DARK, width=3)
        centered_text(draw, (x, axis_y + 44), label, F_SMALL, MUTED)
    vals = [
        (0.12, GREEN, "same", -46),
        (0.18, GREEN, "same", -76),
        (0.21, GREEN, "same", -46),
        (0.55, RED, "diff", 46),
        (0.61, RED, "diff", 76),
        (0.72, RED, "diff", 46),
    ]
    for idx, (v, color, label, offset) in enumerate(vals):
        x = axis_x0 + int((axis_x1 - axis_x0) * v)
        y = axis_y - 86 if label == "same" else axis_y + 86
        draw.line((x, axis_y, x, y), fill=color, width=3)
        draw.ellipse((x - 18, y - 18, x + 18, y + 18), fill=color)
        centered_text(draw, (x, y + offset), f"{v:.2f}", F_SMALL, INK)
    threshold_x = axis_x0 + int((axis_x1 - axis_x0) * 0.38)
    draw.line((threshold_x, axis_y - 160, threshold_x, axis_y + 160), fill=ORANGE, width=5)
    centered_text(draw, (threshold_x, axis_y - 190), "threshold", F_LABEL, ORANGE)
    draw_wrapped(draw, (155, 810), "PPT 설명 문장: 'M이 커질수록 empirical D_Q가 흔들릴 확률이 줄어들고, margin이 충분하면 edge classification이 안정됩니다.'", F_BODY, MUTED, 1540)
    save(image, output, "06_probe_finite_margin.png")


def slide_07(output: Path) -> None:
    image, draw = base()
    title(draw, "Probe 06 - D_Q vs Transfer Utility", "행동 유사도가 실제 critic transfer 이득을 예측하는지 검증", "kill-test")
    rect(draw, (100, 240, 805, 870))
    rect(draw, (875, 240, 1818, 870))
    draw.text((145, 285), "Counterfactual utility test", font=F_SECTION, fill=INK)
    y = draw_wrapped(draw, (145, 350), "동일 checkpoint를 두 branch로 복제한다.", F_BODY, INK, 600)
    y += 28
    branch_y = y
    rect(draw, (165, branch_y, 445, branch_y + 145), fill=(244, 249, 255), outline=BLUE, width=3)
    rect(draw, (500, branch_y, 780, branch_y + 145), fill=(247, 255, 249), outline=GREEN, width=3)
    draw.text((195, branch_y + 30), "Branch A", font=F_LABEL, fill=BLUE)
    draw_wrapped(draw, (195, branch_y + 70), "j -> i critic transfer", F_SMALL, INK, 210)
    draw.text((530, branch_y + 30), "Branch B", font=F_LABEL, fill=GREEN)
    draw_wrapped(draw, (530, branch_y + 70), "no peer transfer", F_SMALL, INK, 210)
    arrow(draw, (445, branch_y + 72), (500, branch_y + 72), fill=DARK)
    draw_wrapped(draw, (145, branch_y + 200), "U_i<-j = J_i(Branch A) - J_i(Branch B)", F_FORMULA, INK, 600)
    draw_wrapped(draw, (145, branch_y + 260), "핵심 plot: x = D_ij^Q, y = U_i<-j. 기대 관계는 D_Q가 낮을수록 U가 높아지는 음의 상관이다.", F_BODY, MUTED, 600)
    draw.text((920, 285), "Example scatter", font=F_SECTION, fill=INK)
    plot = (965, 370, 1715, 790)
    draw.rectangle(plot, fill=WHITE, outline=LINE, width=2)
    draw.line((plot[0] + 60, plot[3] - 55, plot[2] - 45, plot[3] - 55), fill=DARK, width=3)
    draw.line((plot[0] + 60, plot[3] - 55, plot[0] + 60, plot[1] + 35), fill=DARK, width=3)
    centered_text(draw, ((plot[0] + plot[2]) / 2, plot[3] - 12), "D_ij^Q", F_SMALL, MUTED)
    draw.text((plot[0] + 8, plot[1] + 28), "U_i<-j", font=F_SMALL, fill=MUTED)
    points = [(0.12, 0.65), (0.18, 0.42), (0.25, 0.36), (0.40, 0.08), (0.52, -0.05), (0.72, -0.24), (0.82, -0.35)]
    for xval, yval in points:
        x = plot[0] + 60 + int((plot[2] - plot[0] - 120) * xval)
        y = plot[3] - 55 - int((plot[3] - plot[1] - 110) * ((yval + 0.45) / 1.2))
        draw.ellipse((x - 14, y - 14, x + 14, y + 14), fill=BLUE if yval > 0 else RED)
    arrow(draw, (plot[0] + 160, plot[1] + 115), (plot[2] - 155, plot[3] - 155), fill=ORANGE, width=4)
    save(image, output, "07_probe_transfer_utility.png")


def slide_08(output: Path) -> None:
    image, draw = base()
    title(draw, "Probe 07 - Non-identifiable Failure Case", "D_Q가 낮아도 transfer가 항상 안전하진 않다", "failure")
    rect(draw, (110, 235, 890, 880))
    rect(draw, (990, 235, 1810, 880))
    draw.text((155, 280), "Case A", font=F_SECTION, fill=GREEN)
    y = draw_wrapped(draw, (155, 340), "Behaviorally indistinguishable and transfer-compatible", F_BODY, INK, 650)
    draw_wrapped(draw, (155, y + 30), "D_ij^Q ~= 0, U_i<-j > 0", F_FORMULA, GREEN, 650)
    draw.text((155, 560), "해석", font=F_LABEL, fill=INK)
    draw_wrapped(draw, (155, 605), "objective label recovery는 실패해도 transfer 관점에서는 큰 문제가 아닐 수 있다.", F_BODY, MUTED, 650)
    draw.text((1035, 280), "Case B", font=F_SECTION, fill=RED)
    y = draw_wrapped(draw, (1035, 340), "Behaviorally indistinguishable but transfer-incompatible", F_BODY, INK, 690)
    draw_wrapped(draw, (1035, y + 30), "D_ij^Q ~= 0, U_i<-j < 0", F_FORMULA, RED, 690)
    draw.text((1035, 560), "위험", font=F_LABEL, fill=INK)
    draw_wrapped(draw, (1035, 605), "현재 gate는 uncertainty detector가 아니므로 D_Q ~= 0이면 잘못된 edge도 accept할 수 있다.", F_BODY, MUTED, 690)
    draw_wrapped(draw, (155, 915), "PPT 결론: PGCT는 'safe transfer guarantee'가 아니라 'conservative transfer gate'로 설명하는 것이 방어 가능하다.", F_BODY, INK, 1540)
    save(image, output, "08_probe_failure_case.png")


def slide_09(output: Path) -> None:
    image, draw = base()
    title(draw, "Recommended Probe Set", "실험에서 바로 쓸 수 있는 probe bank 구성", "checklist")
    rect(draw, (115, 230, 1810, 890))
    headers = ["Probe", "질문", "왜 좋은가"]
    xs = [165, 520, 1120]
    for x, h in zip(xs, headers):
        draw.text((x, 285), h, font=F_SECTION, fill=INK)
    rows = [
        ("Target preference", "어느 target 방향에 확률을 주는가?", "objective-sensitive fingerprint"),
        ("Pickup/drop", "TOGGLE_LOAD 확률이 task state에 반응하는가?", "reward와 직접 연결"),
        ("Recurrent memory", "초기 단서가 junction 선택에 남는가?", "recurrent policy 검증"),
        ("Blocked route", "장애물 아래 route 선택이 안정적인가?", "geometry-aware behavior"),
        ("Random/neutral", "task signal이 약할 때도 분리되는가?", "baseline"),
        ("Failure case", "D_Q ~= 0, U < 0인 regime이 있는가?", "negative transfer 방어"),
    ]
    y = 365
    for idx, row in enumerate(rows):
        fill = (255, 255, 255) if idx % 2 == 0 else (241, 244, 249)
        draw.rounded_rectangle((145, y - 18, 1770, y + 62), radius=12, fill=fill)
        for x, text in zip(xs, row):
            draw_wrapped(draw, (x, y), text, F_SMALL, INK if x == xs[0] else MUTED, 520 if x != xs[0] else 300, 4)
        y += 88
    draw_wrapped(draw, (165, 915), "주의: oracle label-informed probe는 proposed method가 아니라 diagnostic upper bound로만 사용한다.", F_BODY, RED, 1500)
    save(image, output, "09_probe_set_checklist.png")


SLIDES = [
    slide_00,
    slide_01,
    slide_02,
    slide_03,
    slide_04,
    slide_05,
    slide_06,
    slide_07,
    slide_08,
    slide_09,
]


def create_contact_sheet(output: Path, image_paths: Sequence[Path]) -> Path:
    thumbs: List[Image.Image] = []
    for path in image_paths:
        img = Image.open(path).convert("RGB")
        img.thumbnail((480, 270))
        thumbs.append(img.copy())
    sheet_w = 2 * 520 + 3 * 40
    rows = (len(thumbs) + 1) // 2
    sheet_h = rows * 340 + 80
    sheet = Image.new("RGB", (sheet_w, sheet_h), BG)
    draw = ImageDraw.Draw(sheet)
    for idx, thumb in enumerate(thumbs):
        col = idx % 2
        row = idx // 2
        x = 40 + col * 560
        y = 40 + row * 340
        rect(draw, (x - 10, y - 10, x + 500, y + 310), fill=WHITE, outline=LINE, radius=12)
        sheet.paste(thumb, (x, y))
        draw.text((x, y + 282), image_paths[idx].name, font=F_SMALL, fill=INK)
    path = output / "probe_contact_sheet.png"
    sheet.save(path)
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate PGCT probe example images.")
    parser.add_argument("--output", type=Path, default=Path("output/probes"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for slide in SLIDES:
        slide(args.output)
    image_paths = sorted(path for path in args.output.glob("*.png") if path.name != "probe_contact_sheet.png")
    contact_sheet = create_contact_sheet(args.output, image_paths)
    print(f"generated={len(image_paths)}")
    for path in image_paths:
        print(path.resolve())
    print(contact_sheet.resolve())


if __name__ == "__main__":
    main()
