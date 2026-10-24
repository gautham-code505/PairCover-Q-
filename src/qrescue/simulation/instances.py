"""
Benchmark instances for QAOA, built from the same epoch model the simulation uses.

Two families, kept separate in every report:

- operational: epoch problems harvested from the rolling simulation as they actually
  occurred (with the 12-minute eligibility rule these are small, mostly 1-4 qubits);
- surge: several simultaneous non-P1 calls in a busy hour (a multi-incident surge),
  drawn from the same region, demand surface and model. These are the only realistic
  source of 8-12 qubit problems in this region.
"""

from __future__ import annotations

import numpy as np

from qrescue.simulation.engine import simulate
from qrescue.simulation.paircover import EpochModel, build_model, epoch_qubo
from qrescue.simulation.policies import PairCover
from qrescue.simulation.region import Region, generate_calls


def model_to_dict(model: EpochModel, **meta) -> dict:
    return {"travel": model.travel.tolist(), "weight": model.weight.tolist(), "unserved": model.unserved.tolist(),
            "c": model.c.tolist(), "g": [[int(a), int(b), float(v)] for (a, b), v in model.g.items()], "lam": float(model.lam),
            "eligible": None if model.eligible is None else model.eligible.tolist(), **meta}


def model_from_dict(d: dict) -> EpochModel:
    return EpochModel(np.array(d["travel"]), np.array(d["weight"]), np.array(d["unserved"]), np.array(d["c"]),
                      {(int(a), int(b)): v for a, b, v in d["g"]}, d["lam"],
                      None if d["eligible"] is None else np.array(d["eligible"], dtype=bool))


def n_variables(model: EpochModel) -> int:
    return len(epoch_qubo(model)[0])


def harvest_operational(region: Region, rate: float, lam: float, seeds, sizes, per_size: int, rng) -> list[dict]:
    """Epoch problems that actually occurred in the simulation, grouped by QUBO size."""
    found: dict = {n: [] for n in sizes}

    def rec(model, assignment):
        n = n_variables(model)
        if n in found and model.n_calls >= 1:
            found[n].append(model)

    for seed in seeds:
        simulate(region, generate_calls(region, rate, 24 * 7, seed), PairCover(lam, recorder=rec), rate,
                 horizon_hours=24 * 7)
    out = []
    for n, models in found.items():
        for k in rng.permutation(len(models))[:per_size]:
            out.append(model_to_dict(models[k], family="operational", qubits=n))
    return out


def surge_instances(region: Region, rate: float, lam: float, sizes, per_size: int, rng, cover_minutes: float = 12.0,
                    tau: float = 20.0, max_tries: int = 200000) -> list[dict]:
    """Random multi-incident states: 2-5 non-P1 calls at once, 4-7 idle units."""
    base_covers = region.travel(region.base_xy[:, None, :], region.zones[None, :, :]) <= cover_minutes
    zone_rate = rate * region.demand_share
    found: dict = {n: [] for n in sizes}
    for _ in range(max_tries):
        if all(len(v) >= per_size for v in found.values()):
            break
        idle = np.sort(rng.choice(region.n_ambulances, size=int(rng.integers(4, region.n_ambulances + 1)), replace=False))
        k = int(rng.integers(2, 6))
        zones = rng.choice(len(region.zones), size=k, p=region.demand_share)
        xy = np.clip(region.zones[zones] + rng.uniform(-2, 2, (k, 2)), 0, region.size_km)
        travel = region.travel(region.base_xy[idle][:, None, :], xy[None, :, :])
        weight = rng.choice([2, 1], size=k, p=[0.35 / 0.75, 0.40 / 0.75])
        wait = rng.uniform(0, 4, k)
        model = build_model(travel, weight, wait, base_covers[idle], zone_rate, lam, tau, max_travel=cover_minutes)
        n = n_variables(model)
        if n in found and len(found[n]) < per_size and (model.c.any() or model.g):
            found[n].append(model_to_dict(model, family="surge", qubits=n))
    return [d for n in sizes for d in found[n]]
