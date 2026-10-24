"""
Synthetic service region and call stream for the rolling dispatch simulation.

Everything here is synthetic and clearly labelled as such: zone layout, demand
surface, station and hospital locations, travel speeds, priorities and service
times are modelling assumptions, not data from any real ambulance service.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

PRIORITY_WEIGHTS = {1: 3, 2: 2, 3: 1}   # P1 = most urgent
PRIORITY_MIX = (0.25, 0.35, 0.40)       # share of P1, P2, P3 calls


@dataclass(frozen=True)
class Region:
    """A square region divided into demand zones, with stations and hospitals (km)."""
    zones: np.ndarray            # (Z, 2) zone centroids
    demand_share: np.ndarray     # (Z,) share of calls originating in each zone, sums to 1
    stations: np.ndarray         # (S, 2) station locations
    hospitals: np.ndarray        # (H, 2) hospital locations
    home_station: tuple          # station index of each ambulance
    size_km: float = 24.0
    min_per_km: float = 1.2      # 50 km/h average with lights and siren
    detour: float = 1.3          # road distance / straight-line distance

    @property
    def n_ambulances(self) -> int:
        return len(self.home_station)

    @property
    def base_xy(self) -> np.ndarray:
        """(A, 2) home-station coordinates of every ambulance."""
        return self.stations[list(self.home_station)]

    def travel(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Travel minutes between point arrays a (..., 2) and b (..., 2), broadcasting."""
        return np.linalg.norm(np.asarray(a) - np.asarray(b), axis=-1) * self.detour * self.min_per_km


def default_region() -> Region:
    """6 x 6 grid of 4 km zones: a dense city centre, a smaller town, a sparse periphery."""
    centres = (np.arange(6) + 0.5) * 4.0
    zones = np.array([(x, y) for y in centres for x in centres])
    city = np.exp(-((zones - [12.0, 12.0]) ** 2).sum(1) / (2 * 4.5 ** 2))
    town = 0.6 * np.exp(-((zones - [5.0, 19.0]) ** 2).sum(1) / (2 * 3.0 ** 2))
    weight = 0.08 + 2.0 * city + town
    stations = np.array([
        [10.0, 10.0], [14.5, 13.5],   # two city stations whose areas overlap
        [5.0, 19.0],                  # town
        [19.0, 5.0], [19.0, 19.0], [4.0, 5.0],
    ])
    hospitals = np.array([[12.0, 12.5], [6.0, 18.0]])
    home_station = (0, 0, 1, 2, 3, 4, 5)   # 7 ambulances; station 0 holds two
    return Region(zones, weight / weight.sum(), stations, hospitals, home_station)


@dataclass
class Call:
    id: int
    t: float                     # arrival time, minutes
    zone: int
    xy: np.ndarray
    priority: int                # 1, 2 or 3
    on_scene: float              # minutes at scene
    transport: bool              # whether the patient is taken to hospital
    handover: float = 15.0       # minutes at hospital

    @property
    def weight(self) -> int:
        return PRIORITY_WEIGHTS[self.priority]


def generate_calls(region: Region, rate_per_hour: float, hours: float, seed: int) -> list[Call]:
    """Poisson call stream. The same seed gives the same stream, so every policy sees identical calls."""
    rng = np.random.default_rng(seed)
    n = rng.poisson(rate_per_hour * hours)
    times = np.sort(rng.uniform(0.0, hours * 60.0, n))
    zones = rng.choice(len(region.zones), size=n, p=region.demand_share)
    jitter = rng.uniform(-2.0, 2.0, (n, 2))
    xy = np.clip(region.zones[zones] + jitter, 0.0, region.size_km)
    priority = rng.choice([1, 2, 3], size=n, p=PRIORITY_MIX)
    # lognormal on-scene time with mean ~20 min, sd ~8 min
    sigma = np.sqrt(np.log(1 + (8 / 20) ** 2))
    on_scene = rng.lognormal(np.log(20) - sigma ** 2 / 2, sigma, n)
    transport = rng.uniform(size=n) < 0.85
    return [Call(i, float(times[i]), int(zones[i]), xy[i], int(priority[i]), float(on_scene[i]), bool(transport[i]))
            for i in range(n)]


@dataclass
class RegionStats:
    """Descriptive statistics used to report how the synthetic region is set up."""
    cover_count: np.ndarray = field(default_factory=lambda: np.zeros(0))
    demand_by_cover_count: dict = field(default_factory=dict)


def describe_region(region: Region, cover_minutes: float) -> RegionStats:
    """How many ambulances cover each zone within the threshold when all are idle."""
    reach = region.travel(region.base_xy[:, None, :], region.zones[None, :, :]) <= cover_minutes
    count = reach.sum(0)
    share = {int(k): float(region.demand_share[count == k].sum()) for k in np.unique(count)}
    return RegionStats(count, share)
