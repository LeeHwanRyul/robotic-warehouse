"""Assets for the 5-panel Overall Architecture draft.

1. agent_view_t0.png / agent_view_t1.png: the real renderer (neutral agents, 3x cells), 5x5 window (public-view
   radius 2) centred on one agent before and after it moves FORWARD; other agents take NOOP.  Environment and
   reset seed as in output/background_render_20261103/render_background.py.
2. agent_scene.png: a 7x7 crop around the same agent at t=0 (panel 1).
3. discovery_ema.pdf: real log, mean response-distance EMA of same-team vs cross-team compared pairs per 100k
   steps (output/pgct_docs_20261102/discovery_bins.csv: A+C v2 run, corner goals, individual reward, seed 1, 5M).

    PYTHONPATH=<pyglet<2 dir> python presentation/arch_slide_20261103/make_assets.py
"""
import csv
import json
import sys
from pathlib import Path

import gymnasium as gym
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import rware  # noqa: E402,F401
from rware import rendering as R  # noqa: E402

OUT = Path(__file__).resolve().parent
PLAN = ROOT / "output/ac_validation_20261023_final_tmp/test_env_candidates_plan0/b6_corner_indiv_pen005/experiment.json"
BINS = ROOT / "output/pgct_docs_20261102/discovery_bins.csv"
SCALE, CELL = 3, 91  # 3 x 30 px cells + 1 px grid line

_init, _draw_agents = R.Viewer.__init__, R.Viewer._draw_agents


def _scaled_init(self, world_size):
    _init(self, world_size)
    self.grid_size *= SCALE
    self.icon_size *= SCALE
    self.map_width = 1 + self.cols * (self.grid_size + 1)
    self.map_height = 2 + self.rows * (self.grid_size + 1)
    self.width, self.height = self.map_width + self.side_panel_width, self.map_height
    self.window.set_size(self.width, self.height)


def _neutral_draw_agents(self, env):
    self._team_color = lambda team_id: (120, 120, 120)  # instance override for agents only
    try:
        _draw_agents(self, env)
    finally:
        del self._team_color  # fall back to the class method (possibly patched by public_colours)


R.Viewer.__init__, R.Viewer._draw_agents = _scaled_init, _neutral_draw_agents
_team_color, _light_color = R.Viewer._team_color, R.Viewer._light_color
GREY = (110, 110, 110)


def public_colours(on):
    """Public view: no team or request colours (shelf ownership, requests and goal owners are private)."""
    R.Viewer._team_color = (lambda self, team_id: GREY) if on else _team_color
    R.Viewer._light_color = (lambda self, color, alpha=0.45: GREY) if on else _light_color


def window(frame, rows, x, y, r):
    """(2r+1)^2 cells centred on grid cell (x, y); cells outside the map are grey (not observed as floor)."""
    side = (2 * r + 1) * CELL
    out = np.full((side, side, 3), 200, dtype=np.uint8)
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            cx, cy = x + dx, y + dy
            if 0 <= cx < frame.shape[1] // CELL and 0 <= cy < rows:
                tile = frame[1 + cy * CELL:1 + (cy + 1) * CELL, 1 + cx * CELL:1 + (cx + 1) * CELL]
                out[(dy + r) * CELL:(dy + r + 1) * CELL, (dx + r) * CELL:(dx + r + 1) * CELL] = tile
    return out


def render_views():
    job = json.loads(PLAN.read_text(encoding="utf-8"))["jobs"][0]
    env = gym.make(job["config"]["env_id"], render_mode="rgb_array", **json.loads(job["config"]["env_kwargs_json"]))
    env.reset(seed=1)
    base = env.unwrapped
    rows = base.grid_size[0]
    k = next(i for i, a in enumerate(base.agents) if (int(a.x), int(a.y)) == (4, 5))
    scene = np.asarray(env.render())[:, :base.renderer.map_width]
    public_colours(True)
    frame0 = np.asarray(env.render())[:, :base.renderer.map_width]
    x0, y0 = int(base.agents[k].x), int(base.agents[k].y)
    actions = [0] * len(base.agents)
    actions[k] = 1  # FORWARD
    env.step(tuple(actions))
    frame1 = np.asarray(env.render())[:, :base.renderer.map_width]
    public_colours(False)
    x1, y1 = int(base.agents[k].x), int(base.agents[k].y)
    env.close()
    Image.fromarray(window(frame0, rows, x0, y0, 2)).save(OUT / "agent_view_t0.png")
    Image.fromarray(window(frame1, rows, x1, y1, 2)).save(OUT / "agent_view_t1.png")
    Image.fromarray(window(scene, rows, x0, y0, 3)).save(OUT / "agent_scene.png")
    return dict(agent_index=k, before=[x0, y0], after=[x1, y1])


def plot_ema():
    steps, same, cross = [], [], []
    with BINS.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["same_ema"] and row["cross_ema"]:
                steps.append(float(row["step_million"]))
                same.append(float(row["same_ema"]))
                cross.append(float(row["cross_ema"]))
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7})
    fig, ax = plt.subplots(figsize=(1.75, 1.35))
    ax.plot(steps, cross, color="#C0504D", lw=1.4, label="other team")
    ax.plot(steps, same, color="#1F4E9A", lw=1.4, label="same team")
    ax.axhline(0.5, color="#6B6B6B", lw=0.9, ls="--")
    ax.text(5.0, 0.53, "approve < 0.5", ha="right", va="bottom", fontsize=6, color="#6B6B6B")
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("env steps (M)", labelpad=1)
    ax.set_ylabel("distance EMA", labelpad=1)
    ax.legend(loc="center right", fontsize=6, frameon=False, handlelength=1.2, bbox_to_anchor=(1.0, 0.36))
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=2, pad=1)
    fig.tight_layout(pad=0.2)
    fig.savefig(OUT / "discovery_ema.pdf")
    plt.close(fig)
    return dict(bins=len(steps), first_step=steps[0], last_step=steps[-1])


if __name__ == "__main__":
    info = dict(views=render_views(), ema=plot_ema())
    (OUT / "assets.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    print(info)
