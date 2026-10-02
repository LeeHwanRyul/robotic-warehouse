"""Guard against displaying team-label edges instead of the learned PGCT gate."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from examples.eval_checkpoint_generalization import checkpoint_pgct_gate


def checkpoint():
    distances = np.full((4, 4), 0.8)
    # Deliberately connect opposite-parity actors, unlike the oracle team graph.
    distances[0, 1] = distances[1, 0] = 0.05
    np.fill_diagonal(distances, np.nan)
    return {
        "agents": [None] * 4, "iteration": 100,
        "config": dict(communication_enabled=True, peer_transfer_mode="pgct",
                       graph_mode="policy", pgct_peer_loss_coef=0.01,
                       edge_threshold=0.5, min_probe_count=8, uncertainty_scale=1,
                       value_uncertainty_decay=0.9, pgct_gate_style="threshold",
                       pgct_min_policy_information=0.1, pgct_warmup_updates=10,
                       pgct_distance_threshold=0.12, pgct_distance_temperature=0.25,
                       pgct_gate_power=1),
        "graph": dict(distance_ema=distances, distance_count=np.full((4, 4), 20),
                      policy_information=np.ones(4)),
    }


def test_expansion_uses_learned_edges_not_team_parity():
    gate = checkpoint_pgct_gate(checkpoint(), 8)
    assert gate[0, 1] == gate[4, 5] == 1  # Learned cross-team edge survives.
    assert gate[0, 2] == gate[4, 6] == 0  # True team labels do not add edges.
    assert gate[0, 4] == gate[3, 7] == 1  # Distinct copies of identical actors.
    assert not np.diag(gate).any()


def test_disabled_communication_and_warmup_do_not_create_clone_links():
    ckpt = checkpoint()
    ckpt["config"]["communication_enabled"] = False
    assert not checkpoint_pgct_gate(ckpt, 6).any()
    ckpt["config"]["communication_enabled"] = True
    ckpt["iteration"] = 0
    assert not checkpoint_pgct_gate(ckpt, 6).any()


def test_insufficient_evidence_or_information_does_not_add_learned_links():
    ckpt = checkpoint()
    ckpt["graph"]["distance_count"][0, 1] = 0
    assert checkpoint_pgct_gate(ckpt, 6)[0, 1] == 0
    ckpt["graph"]["policy_information"][0] = 0
    gate = checkpoint_pgct_gate(ckpt, 6)
    assert not gate[0].any()
    assert not gate[4].any()
