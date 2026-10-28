"""
Run benchmark QAOA circuits on IBM quantum hardware (Round 2, mentor follow-up).

Takes instances frozen in reports/qaoa_benchmark/instances.json with the noiseless ramp-chain
angles from results.json (tight penalty), so nothing is re-optimised on the device. For each
circuit it records, next to the hardware counts, the same circuit's noiseless probability, the
random baselines and the exact classical answer with its wall-clock time, so the app and deck
can show classical vs simulator vs hardware on one problem.

Two modes:
- real device: needs an IBM Quantum Platform account saved once on this machine, e.g.
      python -c "from qiskit_ibm_runtime import QiskitRuntimeService as S; S.save_account(token='...', set_as_default=True)"
  (or QISKIT_IBM_TOKEN / QISKIT_IBM_INSTANCE in the environment). The token never goes in the repo.
- --fake NAME: a local fake backend (e.g. FakeTorino) with a noise model built from a real
  device's calibration snapshot. No account, no queue.

Jobs can queue for hours. The script writes a manifest as soon as the job is submitted, so
--no-wait plus a later --retrieve JOB_ID finishes the scoring.

Usage:
    python scripts/run_ibm_hardware.py --fake FakeTorino
    python scripts/run_ibm_hardware.py                       # least busy real device, waits
    python scripts/run_ibm_hardware.py --backend ibm_torino --no-wait
    python scripts/run_ibm_hardware.py --retrieve <job id>
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(_ROOT, "src"))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))

import numpy as np
from qiskit.circuit.library import QAOAAnsatz
from qiskit.transpiler import generate_preset_pass_manager

from qrescue.quantum.qaoa_fast import qubo_energies
from qrescue.simulation.instances import model_from_dict
from qrescue.simulation.paircover import epoch_qubo
from run_qaoa_benchmark import feasible_mask
from run_qaoa_noise import cost_operator

BENCH = os.path.join(_ROOT, "reports", "qaoa_benchmark")
OUT = os.path.join(_ROOT, "reports", "ibm_hardware")
# 4q p=2 is the clearest gain over uniform-feasible guessing (0.59 vs 0.20); 6q shows the
# cost of a bigger circuit on the same device.
DEFAULT_CIRCUITS = ["oper-4q-1:1", "oper-4q-1:2", "oper-6q-5:2"]


def load_benchmark():
    inst = {d["id"]: d for d in json.load(open(os.path.join(BENCH, "instances.json"), encoding="utf-8"))}
    rows = json.load(open(os.path.join(BENCH, "results.json"), encoding="utf-8"))["rows"]
    ramp = {(r["id"], r["p"]): r for r in rows if r["init"] == "ramp" and r["penalty_factor"] == 1.0}
    return inst, ramp


def problem(inst_dict):
    """QUBO, exact classical answer (timed) and the masks used to score samples."""
    model = model_from_dict(inst_dict)
    variables, h, J, const, _ = epoch_qubo(model)
    n = len(variables)
    t0 = time.perf_counter()
    energies = qubo_energies(h, J, n)
    best = int(np.argmin(energies))
    classical_seconds = time.perf_counter() - t0
    return {"variables": variables, "h": h, "J": J, "n": n, "energies": energies,
            "opt": np.isclose(energies, energies.min()), "feas": feasible_mask(variables, n),
            "classical_best": best, "classical_seconds": classical_seconds}


def decode(index, variables):
    """Bitstring index -> dispatch pairs, e.g. ['A3->C1']. Bit k is qubit k (little-endian)."""
    return [f"A{u + 1}->C{j + 1}" for k, (u, j) in enumerate(variables) if (index >> k) & 1]


def two_qubit_count(circ):
    return sum(1 for inst in circ.data if inst.operation.num_qubits == 2)


def build(spec, inst, ramp, pm):
    iid, p = spec.split(":")
    p = int(p)
    prob = problem(inst[iid])
    r = ramp[(iid, p)]
    circ = QAOAAnsatz(cost_operator(prob["h"], prob["J"], prob["n"]), reps=p).assign_parameters(r["params"])
    circ.measure_all()
    isa = pm.run(circ)
    meta = {"id": iid, "p": p, "qubits": prob["n"], "params": r["params"],
            "isa_depth": isa.depth(), "isa_2q": two_qubit_count(isa),
            "physical_qubits": [isa.layout.initial_index_layout()[q] for q in range(prob["n"])] if isa.layout else None,
            "ideal_p_opt": r["p_opt"], "ideal_p_feasible": r["p_feasible"],
            "random_p_opt": r["random_p_opt"], "random_feasible_p_opt": r["random_feasible_p_opt"],
            "random_p_feasible": r["random_p_feasible"],
            "classical_best": decode(prob["classical_best"], prob["variables"]),
            "classical_energy": float(prob["energies"][prob["classical_best"]]),
            "classical_seconds": prob["classical_seconds"]}
    return isa, meta


def score(meta, counts, inst):
    prob = problem(inst[meta["id"]])
    shots = sum(counts.values())
    idx = {k: int(k.replace(" ", ""), 2) for k in counts}
    hits = sum(c for k, c in counts.items() if prob["opt"][idx[k]])
    ok = sum(c for k, c in counts.items() if prob["feas"][idx[k]])
    top = sorted(counts.items(), key=lambda kv: -kv[1])
    # The answer a dispatcher would act on: the lowest-energy feasible sample.
    seen_feasible = [idx[k] for k, _ in top if prob["feas"][idx[k]]]
    pick = min(seen_feasible, key=lambda i: prob["energies"][i]) if seen_feasible else None
    return meta | {
        "shots": shots, "p_opt": hits / shots, "p_feasible": ok / shots,
        "gain_vs_uniform_feasible": (hits / shots) / meta["random_feasible_p_opt"] if meta["random_feasible_p_opt"] else None,
        "most_frequent": top[0][0], "most_frequent_is_optimal": bool(prob["opt"][idx[top[0][0]]]),
        "hardware_pick": decode(pick, prob["variables"]) if pick is not None else None,
        "hardware_pick_is_optimal": bool(pick is not None and prob["opt"][pick]),
        "top_counts": dict(top[:16])}


def job_timing(job):
    """Queue and execution seconds from Runtime metrics; empty for local fake runs."""
    out = {}
    try:
        m = job.metrics()
        ts = m.get("timestamps", {})
        parse = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
        if ts.get("created") and ts.get("running"):
            out["queue_seconds"] = (parse(ts["running"]) - parse(ts["created"])).total_seconds()
        if ts.get("running") and ts.get("finished"):
            out["run_seconds"] = (parse(ts["finished"]) - parse(ts["running"])).total_seconds()
        # Billed QPU time (whole seconds) and the time the circuits themselves ran on the chip.
        out["qpu_charge_seconds"] = m.get("usage", {}).get("qpu_charge_time_seconds")
        if m.get("circuits_execution_time_ns") is not None:
            out["circuit_execution_seconds"] = m["circuits_execution_time_ns"] / 1e9
        out["timestamps"] = ts
    except Exception as e:  # metrics are best-effort
        out["metrics_error"] = str(e)
    return out


def finish(manifest, result, timing, inst):
    rows = [score(meta, pub.data.meas.get_counts(), inst) for meta, pub in zip(manifest["circuits"], result)]
    out = manifest | {"status": "done", "timing": timing, "circuits": rows,
                      "completed_utc": datetime.now(timezone.utc).isoformat()}
    path = os.path.join(OUT, f"{manifest['label']}.json")
    json.dump(out, open(path, "w", encoding="utf-8"), indent=1)
    for r in rows:
        print(f"{r['id']} p={r['p']} ({r['qubits']}q, {r['isa_2q']} 2q gates, depth {r['isa_depth']}): "
              f"p_opt {r['p_opt']:.3f} hw vs {r['ideal_p_opt']:.3f} ideal vs {r['random_feasible_p_opt']:.3f} uniform-feasible; "
              f"pick {r['hardware_pick']} optimal={r['hardware_pick_is_optimal']}; classical {r['classical_best']} "
              f"in {r['classical_seconds'] * 1e3:.2f} ms")
    print(f"wrote {os.path.relpath(path, _ROOT)}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--circuits", nargs="+", default=DEFAULT_CIRCUITS, help="instance:depth pairs")
    ap.add_argument("--shots", type=int, default=4096)
    ap.add_argument("--backend", help="real device name; default is the least busy one")
    ap.add_argument("--fake", help="local fake backend class, e.g. FakeTorino")
    ap.add_argument("--no-wait", action="store_true", help="submit, write the manifest and exit")
    ap.add_argument("--retrieve", metavar="JOB_ID", help="fetch and score a job submitted earlier")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    inst, ramp = load_benchmark()

    from qiskit_ibm_runtime import SamplerV2

    if args.retrieve:
        from qiskit_ibm_runtime import QiskitRuntimeService
        manifest = json.load(open(os.path.join(OUT, f"job_{args.retrieve}.json"), encoding="utf-8"))
        job = QiskitRuntimeService().job(args.retrieve)
        print(f"job {args.retrieve} on {manifest['backend']}: {job.status()}")
        result = job.result()
        return finish(manifest, result, job_timing(job), inst)

    if args.fake:
        import qiskit_ibm_runtime.fake_provider as fp
        backend = getattr(fp, args.fake)()
    else:
        from qiskit_ibm_runtime import QiskitRuntimeService
        service = QiskitRuntimeService()
        backend = service.backend(args.backend) if args.backend else \
            service.least_busy(operational=True, simulator=False, min_num_qubits=8)
    pm = generate_preset_pass_manager(backend=backend, optimization_level=3, seed_transpiler=7)
    isa, metas = zip(*(build(s, inst, ramp, pm) for s in args.circuits))

    t0 = time.perf_counter()
    job = SamplerV2(mode=backend).run(list(isa), shots=args.shots)
    label = f"{backend.name if args.fake else 'real_' + backend.name}_{job.job_id()[:8]}"
    manifest = {"label": label, "kind": "fake" if args.fake else "real", "backend": backend.name,
                "backend_qubits": backend.num_qubits, "job_id": job.job_id(), "shots": args.shots,
                "submitted_utc": datetime.now(timezone.utc).isoformat(), "status": "submitted",
                "note": ("Local fake backend: noise from a calibration snapshot of the named device, run on Aer."
                         if args.fake else "Real IBM Quantum device. Angles were tuned noiselessly, not on the device."),
                "circuits": list(metas)}
    if not args.fake:
        json.dump(manifest, open(os.path.join(OUT, f"job_{job.job_id()}.json"), "w", encoding="utf-8"), indent=1)
    print(f"submitted {len(isa)} circuits to {backend.name}, job {job.job_id()}", flush=True)
    if args.no_wait and not args.fake:
        print(f"later: python scripts/run_ibm_hardware.py --retrieve {job.job_id()}")
        return manifest
    result = job.result()
    timing = job_timing(job) if not args.fake else {}
    timing["wall_seconds_incl_queue"] = time.perf_counter() - t0
    return finish(manifest, result, timing, inst)


if __name__ == "__main__":
    main()
