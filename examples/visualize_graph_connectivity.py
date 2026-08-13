"""Visualize agent graph connectivity on top of a multi-team RWARE grid.

Example:
    python examples/visualize_graph_connectivity.py --steps 8
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import gymnasium as gym
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import rware  # noqa: F401 - registers Gymnasium environments


Position = Tuple[int, int]


TEAM_COLORS = [
    (220, 72, 72),
    (60, 122, 230),
    (72, 168, 104),
    (214, 156, 42),
    (148, 92, 204),
    (36, 174, 178),
]
COMPONENT_COLORS = [
    (35, 112, 181),
    (226, 124, 48),
    (54, 148, 91),
    (182, 82, 82),
    (128, 88, 174),
    (122, 122, 38),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render communication/training graph connectivity over an environment grid."
    )
    parser.add_argument("--env-id", default="mtgrid-main-6ag-2teams-v0")
    parser.add_argument(
        "--env-kwargs",
        default="{}",
        help="JSON object passed to gym.make, for example '{\"communication_range\": 4}'.",
    )
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--steps", type=int, default=0)
    parser.add_argument(
        "--edge-source",
        choices=["physical", "training", "oracle", "complete"],
        default="physical",
        help="Which adjacency matrix to render.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("runs/graph_connectivity/graph_connectivity.png"),
    )
    parser.add_argument(
        "--hide-ranges",
        action="store_true",
        help="Hide each agent's physical communication range overlay.",
    )
    return parser.parse_args()


def parse_env_kwargs(value: str) -> Dict[str, object]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"--env-kwargs must be valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise SystemExit("--env-kwargs must decode to a JSON object")
    return parsed


def make_env(env_id: str, env_kwargs: Dict[str, object]) -> gym.Env:
    spec = gym.spec(env_id)
    entry_point = str(spec.entry_point)
    kwargs = dict(env_kwargs)
    if "multi_team" in entry_point and "reveal_team_info" not in kwargs:
        kwargs["reveal_team_info"] = True
    return gym.make(env_id, **kwargs)


def run_steps(env: gym.Env, seed: int, steps: int) -> Dict[str, object]:
    _, info = env.reset(seed=seed)
    env.action_space.seed(seed + 10_000)
    for _ in range(max(0, steps)):
        _, _, done, truncated, info = env.step(env.action_space.sample())
        if done or truncated:
            break
    return dict(info)


def grid_size(env: gym.Env) -> Tuple[int, int]:
    size = tuple(int(v) for v in env.unwrapped.grid_size)
    if len(size) != 2:
        raise ValueError("env.grid_size must contain height and width")
    return size


def agent_positions(env: gym.Env) -> List[Position]:
    unwrapped = env.unwrapped
    if hasattr(unwrapped, "agent_positions"):
        positions = np.asarray(unwrapped.agent_positions, dtype=np.int32)
        return [(int(x), int(y)) for y, x in positions]
    if hasattr(unwrapped, "agents"):
        return [(int(agent.x), int(agent.y)) for agent in unwrapped.agents]
    raise ValueError("environment does not expose agent positions")


def team_ids(env: gym.Env) -> Optional[np.ndarray]:
    unwrapped = env.unwrapped
    if hasattr(unwrapped, "get_oracle_team_assignments"):
        return np.asarray(unwrapped.get_oracle_team_assignments(), dtype=np.int32)
    if hasattr(unwrapped, "agent_team_ids"):
        return np.asarray(unwrapped.agent_team_ids, dtype=np.int32)
    return None


def communication_range(env: gym.Env) -> int:
    unwrapped = env.unwrapped
    return int(getattr(unwrapped, "communication_range", getattr(unwrapped, "sensor_range", 0)))


def manual_physical_adjacency(env: gym.Env, positions: Sequence[Position]) -> np.ndarray:
    n_agents = len(positions)
    adj = np.zeros((n_agents, n_agents), dtype=np.float32)
    comm_range = communication_range(env)
    use_manhattan = hasattr(env.unwrapped, "agent_positions")
    for i in range(n_agents):
        for j in range(i + 1, n_agents):
            dx = abs(positions[i][0] - positions[j][0])
            dy = abs(positions[i][1] - positions[j][1])
            distance = dx + dy if use_manhattan else max(dx, dy)
            if distance <= comm_range:
                adj[i, j] = 1.0
                adj[j, i] = 1.0
    return adj


def adjacency_matrix(
    env: gym.Env,
    positions: Sequence[Position],
    edge_source: str,
) -> np.ndarray:
    n_agents = len(positions)
    unwrapped = env.unwrapped
    if edge_source == "complete":
        adj = np.ones((n_agents, n_agents), dtype=np.float32)
    elif edge_source == "oracle":
        labels = team_ids(env)
        adj = np.zeros((n_agents, n_agents), dtype=np.float32)
        if labels is not None:
            for i in range(n_agents):
                for j in range(i + 1, n_agents):
                    if labels[i] == labels[j]:
                        adj[i, j] = 1.0
                        adj[j, i] = 1.0
    elif edge_source == "training":
        if not hasattr(unwrapped, "training_comm_adj"):
            raise ValueError("edge-source=training requires env.training_comm_adj")
        adj = np.asarray(unwrapped.training_comm_adj, dtype=np.float32).copy()
    else:
        if hasattr(unwrapped, "get_neighbor_adjacency"):
            adj = np.asarray(unwrapped.get_neighbor_adjacency(), dtype=np.float32).copy()
        else:
            adj = manual_physical_adjacency(env, positions)

    if adj.shape != (n_agents, n_agents):
        raise ValueError(f"adjacency shape {adj.shape} does not match {n_agents} agents")
    adj = (adj > 0.0).astype(np.float32)
    adj = np.maximum(adj, adj.T)
    np.fill_diagonal(adj, 0.0)
    return adj


def connected_components(adj: np.ndarray) -> List[List[int]]:
    visited = np.zeros(adj.shape[0], dtype=bool)
    components: List[List[int]] = []
    for start in range(adj.shape[0]):
        if visited[start]:
            continue
        stack = [start]
        visited[start] = True
        component = []
        while stack:
            node = stack.pop()
            component.append(node)
            for nxt in np.flatnonzero(adj[node] > 0.0).tolist():
                if not visited[nxt]:
                    visited[nxt] = True
                    stack.append(int(nxt))
        components.append(sorted(component))
    return components


def component_lookup(components: Sequence[Sequence[int]]) -> Dict[int, int]:
    lookup = {}
    for component_id, component in enumerate(components):
        for agent_id in component:
            lookup[int(agent_id)] = int(component_id)
    return lookup


def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = ["arialbd.ttf", "arial.ttf"] if bold else ["arial.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    xy: Tuple[float, float],
    text: str,
    font: ImageFont.ImageFont,
    fill: Tuple[int, int, int],
) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    draw.text((xy[0] - width / 2, xy[1] - height / 2), text, font=font, fill=fill)


def grid_artifacts(env: gym.Env) -> Dict[str, object]:
    unwrapped = env.unwrapped
    artifacts: Dict[str, object] = {
        "obstacles": [],
        "targets": [],
        "shelves": [],
        "requested_shelves": [],
        "goals": [],
    }
    if hasattr(unwrapped, "obstacles"):
        ys, xs = np.nonzero(np.asarray(unwrapped.obstacles, dtype=bool))
        artifacts["obstacles"] = [(int(x), int(y)) for y, x in zip(ys, xs)]
    if hasattr(unwrapped, "target_positions"):
        artifacts["targets"] = [
            (int(x), int(y), int(team_id))
            for (y, x), team_id in unwrapped.target_positions.items()
        ]
    if hasattr(unwrapped, "shelfs"):
        requested_ids = {int(shelf.id) for shelf in getattr(unwrapped, "request_queue", [])}
        artifacts["shelves"] = [
            (int(shelf.x), int(shelf.y)) for shelf in unwrapped.shelfs
        ]
        artifacts["requested_shelves"] = [
            (int(shelf.x), int(shelf.y))
            for shelf in unwrapped.shelfs
            if int(shelf.id) in requested_ids
        ]
    if hasattr(unwrapped, "goals"):
        artifacts["goals"] = [(int(x), int(y)) for x, y in unwrapped.goals]
    return artifacts


def render_connectivity(
    env: gym.Env,
    adj: np.ndarray,
    components: Sequence[Sequence[int]],
    output_path: Path,
    edge_source: str,
    seed: int,
    steps: int,
    show_ranges: bool,
    physical_check_passed: Optional[bool],
) -> None:
    height, width = grid_size(env)
    positions = agent_positions(env)
    labels = team_ids(env)
    comp_ids = component_lookup(components)
    artifacts = grid_artifacts(env)

    cell = int(max(24, min(44, 720 / max(height, width))))
    grid_left = 48
    grid_top = 104
    side_width = 260
    legend_gap = 24
    image_width = grid_left * 2 + width * cell + side_width + legend_gap
    image_height = grid_top + height * cell + 56

    image = Image.new("RGB", (image_width, image_height), (248, 249, 250))
    draw = ImageDraw.Draw(image)
    title_font = load_font(22, bold=True)
    meta_font = load_font(14)
    small_font = load_font(12)
    label_font = load_font(max(12, int(cell * 0.36)), bold=True)

    edge_count = int(np.sum(adj) // 2)
    status = (
        "physical check: pass"
        if physical_check_passed is True
        else "physical check: mismatch"
        if physical_check_passed is False
        else "physical check: n/a"
    )
    title = "Graph connectivity"
    subtitle = (
        f"{env.spec.id} | source={edge_source} | seed={seed} | steps={steps} | "
        f"edges={edge_count} | components={len(components)} | range={communication_range(env)}"
    )
    draw.text((grid_left, 28), title, font=title_font, fill=(26, 32, 44))
    draw.text((grid_left, 60), subtitle, font=meta_font, fill=(70, 80, 96))
    draw.text((grid_left, 80), status, font=small_font, fill=(70, 80, 96))

    def cell_bounds(x: int, y: int) -> Tuple[int, int, int, int]:
        x0 = grid_left + x * cell
        y0 = grid_top + y * cell
        return x0, y0, x0 + cell, y0 + cell

    def center(pos: Position) -> Tuple[float, float]:
        x, y = pos
        x0, y0, x1, y1 = cell_bounds(x, y)
        return (x0 + x1) / 2, (y0 + y1) / 2

    for y in range(height):
        for x in range(width):
            fill = (255, 255, 255)
            outline = (222, 226, 232)
            draw.rectangle(cell_bounds(x, y), fill=fill, outline=outline)

    for x, y in artifacts["obstacles"]:
        draw.rectangle(cell_bounds(x, y), fill=(61, 67, 78), outline=(61, 67, 78))

    for x, y in artifacts["shelves"]:
        x0, y0, x1, y1 = cell_bounds(x, y)
        pad = max(3, cell // 5)
        draw.rectangle((x0 + pad, y0 + pad, x1 - pad, y1 - pad), fill=(183, 190, 199))

    for x, y in artifacts["requested_shelves"]:
        x0, y0, x1, y1 = cell_bounds(x, y)
        pad = max(4, cell // 4)
        draw.rectangle((x0 + pad, y0 + pad, x1 - pad, y1 - pad), fill=(245, 188, 64))

    for x, y, team_id in artifacts["targets"]:
        x0, y0, x1, y1 = cell_bounds(x, y)
        color = TEAM_COLORS[team_id % len(TEAM_COLORS)]
        pad = max(4, cell // 5)
        draw.ellipse((x0 + pad, y0 + pad, x1 - pad, y1 - pad), fill=color)

    for x, y in artifacts["goals"]:
        x0, y0, x1, y1 = cell_bounds(x, y)
        pad = max(3, cell // 7)
        draw.rectangle((x0 + pad, y0 + pad, x1 - pad, y1 - pad), outline=(40, 160, 90), width=3)

    if show_ranges and communication_range(env) > 0:
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        comm_range = communication_range(env)
        use_manhattan = hasattr(env.unwrapped, "agent_positions")
        for agent_id, (x, y) in enumerate(positions):
            color = COMPONENT_COLORS[comp_ids[agent_id] % len(COMPONENT_COLORS)]
            rgba = (*color, 34)
            outline_rgba = (*color, 96)
            if use_manhattan:
                points = [
                    center((x, max(0, y - comm_range))),
                    center((min(width - 1, x + comm_range), y)),
                    center((x, min(height - 1, y + comm_range))),
                    center((max(0, x - comm_range), y)),
                ]
                overlay_draw.polygon(points, fill=rgba, outline=outline_rgba)
            else:
                x0, y0 = max(0, x - comm_range), max(0, y - comm_range)
                x1, y1 = min(width - 1, x + comm_range), min(height - 1, y + comm_range)
                left, top, _, _ = cell_bounds(x0, y0)
                _, _, right, bottom = cell_bounds(x1, y1)
                overlay_draw.rectangle((left, top, right, bottom), fill=rgba, outline=outline_rgba)
        image.paste(Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB"))
        draw = ImageDraw.Draw(image)

    for i in range(adj.shape[0]):
        for j in range(i + 1, adj.shape[1]):
            if adj[i, j] <= 0.0:
                continue
            color = COMPONENT_COLORS[comp_ids[i] % len(COMPONENT_COLORS)]
            draw.line((*center(positions[i]), *center(positions[j])), fill=color, width=max(3, cell // 8))

    radius = max(9, int(cell * 0.34))
    for agent_id, pos in enumerate(positions):
        cx, cy = center(pos)
        if labels is not None:
            fill = TEAM_COLORS[int(labels[agent_id]) % len(TEAM_COLORS)]
        else:
            fill = COMPONENT_COLORS[comp_ids[agent_id] % len(COMPONENT_COLORS)]
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=fill, outline=(22, 28, 38), width=2)
        draw_centered_text(draw, (cx, cy), str(agent_id), label_font, (255, 255, 255))

    panel_left = grid_left + width * cell + legend_gap
    draw.text((panel_left, grid_top), "Components", font=meta_font, fill=(26, 32, 44))
    y_cursor = grid_top + 28
    for component_id, component in enumerate(components):
        color = COMPONENT_COLORS[component_id % len(COMPONENT_COLORS)]
        draw.rectangle((panel_left, y_cursor + 3, panel_left + 14, y_cursor + 17), fill=color)
        draw.text(
            (panel_left + 22, y_cursor),
            f"C{component_id}: {list(component)}",
            font=small_font,
            fill=(48, 56, 70),
        )
        y_cursor += 24

    y_cursor += 8
    draw.text((panel_left, y_cursor), "Legend", font=meta_font, fill=(26, 32, 44))
    y_cursor += 28
    legend_items = [
        ("agent", (38, 94, 180)),
        ("edge", (35, 112, 181)),
        ("range", (165, 178, 196)),
        ("obstacle", (61, 67, 78)),
        ("target/request", (245, 188, 64)),
        ("goal", (40, 160, 90)),
    ]
    for text, color in legend_items:
        draw.rectangle((panel_left, y_cursor + 4, panel_left + 16, y_cursor + 18), fill=color)
        draw.text((panel_left + 24, y_cursor), text, font=small_font, fill=(48, 56, 70))
        y_cursor += 24

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)


def print_summary(
    env: gym.Env,
    adj: np.ndarray,
    components: Sequence[Sequence[int]],
    output_path: Path,
    physical_check_passed: Optional[bool],
) -> None:
    edge_count = int(np.sum(adj) // 2)
    print(f"env={env.spec.id}")
    print(f"agents={adj.shape[0]} edges={edge_count} components={list(map(list, components))}")
    print(f"adjacency=\n{adj.astype(int)}")
    if physical_check_passed is not None:
        print(f"physical_check={'pass' if physical_check_passed else 'mismatch'}")
    print(f"output={output_path.resolve()}")


def main() -> None:
    args = parse_args()
    env_kwargs = parse_env_kwargs(args.env_kwargs)
    env = make_env(args.env_id, env_kwargs)
    try:
        run_steps(env, args.seed, args.steps)
        positions = agent_positions(env)
        adj = adjacency_matrix(env, positions, args.edge_source)
        components = connected_components(adj)

        physical_check_passed = None
        if args.edge_source == "physical" and hasattr(env.unwrapped, "get_neighbor_adjacency"):
            manual_adj = manual_physical_adjacency(env, positions)
            physical_check_passed = bool(np.array_equal(adj, manual_adj))

        output_path = args.output
        if output_path.suffix.lower() != ".png":
            output_path = output_path.with_suffix(".png")
        render_connectivity(
            env=env,
            adj=adj,
            components=components,
            output_path=output_path,
            edge_source=args.edge_source,
            seed=args.seed,
            steps=args.steps,
            show_ranges=not args.hide_ranges,
            physical_check_passed=physical_check_passed,
        )
        print_summary(env, adj, components, output_path, physical_check_passed)
    finally:
        env.close()


if __name__ == "__main__":
    main()
