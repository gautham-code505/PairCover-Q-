"""
Discrete-time rolling dispatch simulation.

Decisions are taken at fixed epochs (default every 2 minutes, like a dispatcher clearing
the queue), so simultaneous calls form real batches. An ambulance stays busy from dispatch
until it is back at its home station: travel to scene, on-scene time, optional transport
to the nearest hospital plus handover, and the return trip. Units are not re-tasked en route.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from qrescue.simulation.policies import DispatchState
from qrescue.simulation.region import Call, Region


@dataclass
class SimResult:
    policy: str
    calls: list
    dispatch_t: np.ndarray
    unit: np.ndarray
    response: np.ndarray        # arrival -> on scene, minutes (includes queueing)
    uncovered: float            # time-averaged share of demand with no idle unit within threshold
    horizon: float
    deferrals: int              # epochs where a call waited although a unit was idle


def simulate(region: Region, calls: list[Call], policy, rate_per_hour: float, *,
             epoch: float = 2.0, cover_minutes: float = 12.0, horizon_hours: float | None = None) -> SimResult:
    n, n_amb = len(calls), region.n_ambulances
    base = region.base_xy
    zone_rate = rate_per_hour * region.demand_share
    base_covers = region.travel(base[:, None, :], region.zones[None, :, :]) <= cover_minutes
    free_at = np.zeros(n_amb)
    busy = [[] for _ in range(n_amb)]
    dispatch_t = np.full(n, np.nan)
    unit = np.full(n, -1)
    response = np.full(n, np.nan)
    pending: list[Call] = []
    nxt, t, deferrals = 0, epoch, 0

    while nxt < n or pending:
        while nxt < n and calls[nxt].t <= t:
            pending.append(calls[nxt])
            nxt += 1
        idle = np.flatnonzero(free_at <= t)
        if pending and len(idle):
            xy = np.array([c.xy for c in pending])
            travel = region.travel(base[idle][:, None, :], xy[None, :, :])
            state = DispatchState(t, pending, idle, travel, base_covers[idle], zone_rate, cover_minutes)
            done = set()
            for u, j in policy(state):
                a, c = int(idle[u]), pending[j]
                to_scene = float(travel[u, j])
                leave = t + to_scene + c.on_scene
                if c.transport:
                    hosp = region.hospitals[np.argmin(region.travel(region.hospitals, c.xy))]
                    end = leave + float(region.travel(c.xy, hosp)) + c.handover + float(region.travel(hosp, base[a]))
                else:
                    end = leave + float(region.travel(c.xy, base[a]))
                free_at[a] = end
                busy[a].append((t, end))
                dispatch_t[c.id], unit[c.id], response[c.id] = t, a, (t - c.t) + to_scene
                done.add(j)
            pending = [c for j, c in enumerate(pending) if j not in done]
            if pending and len(done) < len(idle):
                deferrals += 1
        # jump to the next epoch at which something can change
        if pending and (free_at <= t).any():
            t += epoch
            continue
        events = []
        if nxt < n:
            events.append(calls[nxt].t)
        if pending:
            events.append(free_at[free_at > t].min())
        if not events:
            break
        t = max(t + epoch, math.ceil(min(events) / epoch) * epoch)

    horizon = (horizon_hours * 60.0) if horizon_hours else (calls[-1].t if calls else 0.0)
    uncovered = _time_avg_uncovered(busy, base_covers, region.demand_share, horizon)
    return SimResult(getattr(policy, "name", str(policy)), calls, dispatch_t, unit, response, uncovered, horizon, deferrals)


def _time_avg_uncovered(busy, base_covers, share, horizon, step=1.0) -> float:
    grid = np.arange(0.0, horizon, step) + step / 2
    idle = np.ones((len(busy), len(grid)), dtype=bool)
    for a, intervals in enumerate(busy):
        for s, e in intervals:
            idle[a, (grid >= s) & (grid < e)] = False
    covered = (base_covers.T.astype(int) @ idle.astype(int)) > 0      # (Z, K)
    return float((share[:, None] * ~covered).sum(0).mean())


def summarize(result: SimResult, target: float = 12.0) -> dict:
    r = result.response
    pr = np.array([c.priority for c in result.calls])
    wait = result.dispatch_t - np.array([c.t for c in result.calls])
    out = {
        "calls": int(len(r)),
        "mean_response": float(np.mean(r)),
        "p90_response": float(np.percentile(r, 90)),
        "late_share": float(np.mean(r > target)),
        "mean_queue_wait": float(np.mean(wait)),
        "uncovered_demand": result.uncovered,
        "deferrals": result.deferrals,
    }
    for p in (1, 2, 3):
        m = pr == p
        out[f"p{p}_mean_response"] = float(np.mean(r[m])) if m.any() else float("nan")
        out[f"p{p}_late_share"] = float(np.mean(r[m] > target)) if m.any() else float("nan")
    return out
