# RWARE Curriculum Runs

Use the curriculum wrappers instead of editing
`examples/train_recurrent_ippo_consensus.py` for each stage. The main trainer
should stay focused on shared PPO, diagnostics, checkpointing, and W&B logic.

## Curriculum 1: Delivery

```powershell
python examples/curriculum1/train.py
```

This trains one agent to find the requested shelf, pick it up, and deliver it
to the goal. The default checkpoint is saved under:

```text
runs/recurrent_ippo_consensus/curriculum1_1ag_delivery_sr2/final.pt
```

## Curriculum 2: Return

```powershell
python examples/curriculum2/train.py
```

This continues from the Curriculum 1 actor and trains the agent to return the
delivered shelf to its home position. By default it loads:

```text
runs/recurrent_ippo_consensus/curriculum1_1ag_delivery_sr2/final.pt
```

To reuse a different Stage 1 checkpoint, append an override:

```powershell
python examples/curriculum2/train.py `
  --init-checkpoint runs/recurrent_ippo_consensus/stage1_1ag_delivery_sr2_pickupfix/final.pt
```

Any argument appended to the wrapper command overrides that wrapper's default
because the wrapper passes defaults first and user arguments last.
