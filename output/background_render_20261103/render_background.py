"""Background-slide frames of the main environment (corner goals, individual reward, 6 agents in 2 teams).

Uses the project's own renderer (rware/rendering.py) on the exact env kwargs of b6_corner_indiv_pen005, seed 1
(copied from output/ac_validation_20261023_final_tmp/test_env_candidates_plan0/b6_corner_indiv_pen005/experiment.json).
Agents take uniformly random actions; this is an illustration of the task, not a trained policy.

    PYTHONPATH=<pyglet<2 dir>;<repo root> python output/background_render_20261103/render_background.py
"""
import json
import sys
from pathlib import Path

import gymnasium as gym
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import rware  # noqa: E402,F401  (registers the env ids)
from rware import rendering as R  # noqa: E402

OUT = Path(__file__).resolve().parent
PLAN = ROOT / "output/ac_validation_20261023_final_tmp/test_env_candidates_plan0/b6_corner_indiv_pen005/experiment.json"
STEPS = 400
EVERY = 20
SCALE = int(sys.argv[1]) if len(sys.argv) > 1 else 1  # cell size multiplier for slide-quality images

_init = R.Viewer.__init__


def _scaled_init(self, world_size):
    """Larger cells for this script only; rware/rendering.py itself is unchanged."""
    _init(self, world_size)
    if SCALE > 1:
        self.grid_size *= SCALE
        self.icon_size *= SCALE
        self.map_width = 1 + self.cols * (self.grid_size + 1)
        self.map_height = 2 + self.rows * (self.grid_size + 1)
        self.width, self.height = self.map_width + self.side_panel_width, self.map_height
        self.window.set_size(self.width, self.height)


R.Viewer.__init__ = _scaled_init

# "neutral": agents drawn in one grey (team membership unknown to the agents); shelves and goals keep team colours.
NEUTRAL = len(sys.argv) > 2 and sys.argv[2] == "neutral"
_draw_agents = R.Viewer._draw_agents


def _neutral_draw_agents(self, env):
    original = self._team_color
    self._team_color = lambda team_id: (120, 120, 120)
    try:
        _draw_agents(self, env)
    finally:
        self._team_color = original


if NEUTRAL:
    R.Viewer._draw_agents = _neutral_draw_agents


def main():
    job = json.loads(PLAN.read_text(encoding="utf-8"))["jobs"][0]
    env_id, kwargs = job["config"]["env_id"], json.loads(job["config"]["env_kwargs_json"])
    env = gym.make(env_id, render_mode="rgb_array", **kwargs)
    env.reset(seed=1)
    base = env.unwrapped
    rng = np.random.default_rng(1)
    rows = []
    for t in range(STEPS + 1):
        if t % EVERY == 0:
            frame = np.asarray(env.render())
            loaded = sum(a.carrying_shelf is not None for a in base.agents)
            suffix = (f"_x{SCALE}" if SCALE > 1 else "") + ("_neutral" if NEUTRAL else "")
            name = f"frame_t{t:03d}_loaded{loaded}{suffix}.png"
            Image.fromarray(frame).save(OUT / name)
            map_name = f"map_t{t:03d}{suffix}.png"
            Image.fromarray(frame[:, :base.renderer.map_width]).save(OUT / map_name)  # map only, no side panel
            rows.append(dict(step=t, loaded=loaded, file=name, map_file=map_name, shape=list(frame.shape)))
        _, _, done, truncated, _ = env.step(tuple(int(a) for a in rng.integers(0, 5, size=len(base.agents))))
        if done or truncated:
            break
    env.close()
    (OUT / f"frames{'_x%d' % SCALE if SCALE > 1 else ''}{'_neutral' if NEUTRAL else ''}.json").write_text(json.dumps(dict(
        env_id=env_id, seed=1, policy="uniform random", scale=SCALE, neutral_agents=NEUTRAL, frames=rows),
                                                indent=1), encoding="utf-8")
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
