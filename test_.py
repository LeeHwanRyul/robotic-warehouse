from rware.multi_team_warehouse import MultiTeamWarehouse
from rware.warehouse import Action, ObservationType

env = MultiTeamWarehouse(
    shelf_columns=5,
    column_height=6,
    shelf_rows=2,
    n_agents=5,
    n_teams=2,
    msg_bits=0,

    sensor_range=5,
    observation_type=ObservationType.FLATTENED,
    
    request_queue_size=4,
    max_inactivity_steps=100,
    max_steps=500,
    render_mode="human",
    reveal_team_info=True,

    shelf_team_mode="soft_zones",
    shelf_soft_zone_ratio=0.7,
    shelf_soft_zone_axis="x",

    goal_team_mode="soft_zones",
    goals_per_team=2,
    soft_goal_separation=0.8,

    require_matching_team_goal=True,
)

obs, info = env.reset(seed=0)

done = False

while True:
    env.render()

    actions = env.action_space.sample()
    obs, rewards, done, truncated, info = env.step(actions)

env.close()