# Qiskit QAOA feasibility and evaluation methodology for Q-Rescue (verified 9 October 2026)

All version numbers, class names and signatures below were read from live PyPI pages / JSON, official docs or GitHub source on 9 October 2026. Anything I could not confirm from a live page is listed under "Gaps" rather than stated as fact. Qubit counts, memory figures and probability arithmetic are my own calculations and sit under "Inferences".

## 1. Current versions, support status and mutual compatibility (October 2026)

### Takeaway
The supported core is Qiskit SDK 2.5.2 (Aug 2026, Python >= 3.10) plus qiskit-aer 0.17.2. qiskit-optimization (0.7.0, Aug 2025) and qiskit-algorithms (0.4.0, Aug 2025) are both "no longer officially supported by IBM"; the qiskit-optimization GitHub repo was archived read-only on 12 July 2026, and IBM points users to qiskit-addon-opt-mapper 0.1.0, which does modelling/mapping only and contains no QAOA.

### Cited Findings
- qiskit latest version is 2.5.2; `requires_python >=3.10`; core dependencies `numpy<3,>=2.0`, `scipy>=1.14`, `rustworkx>=0.15.0`, `dill>=0.3`, `stevedore>=3.0.0`, `typing-extensions` — [PyPI JSON qiskit](https://pypi.org/pypi/qiskit/json)
- qiskit 2.5.2 files were uploaded 2026-08-13; classifiers list Python 3.10–3.14; wheels are `cp310-abi3` (one wheel per platform for 3.10+), including `win_amd64` — [PyPI JSON qiskit 2.5.2](https://pypi.org/pypi/qiskit/2.5.2/json)
- The IBM release-notes index lists 2.5 as the newest Qiskit SDK series (2.0–2.5, then 1.x); no 2.6 or 3.0 is listed — [IBM Quantum docs, Qiskit release notes](https://quantum.cloud.ibm.com/docs/en/api/qiskit/release-notes)
- Qiskit 2.5 release notes: NumPy minimum raised to 2.0; items deprecated in 2.5 "will be removed in Qiskit v3.0" with no date given; no deprecation touching QAOAAnsatz, primitives or SparsePauliOp is mentioned on that page — [Qiskit 2.5 release notes](https://quantum.cloud.ibm.com/docs/en/api/qiskit/release-notes/2.5)
- Qiskit 2.1 release notes: "Python 3.9 is deprecated starting with Qiskit v2.1 and will no longer be supported in Qiskit v2.3." — [Qiskit 2.1 release notes](https://quantum.cloud.ibm.com/docs/en/api/qiskit/release-notes/2.1)
- qiskit-aer latest version is 0.17.2, released 17 September 2025; install with `pip install qiskit-aer` — [PyPI qiskit-aer](https://pypi.org/project/qiskit-aer/)
- qiskit-aer 0.17.2 `requires_dist`: `qiskit>=1.1.0`, `numpy>=1.16.3`, `scipy>=1.0`, `psutil>=5`, `python-dateutil>=2.8.0` (no upper cap on qiskit); metadata `requires_python >=3.7`; wheels exist for cp39–cp314 including `win_amd64` for every one of them; the cp314 wheels were added later (latest file 2026-02-04) — [PyPI JSON qiskit-aer 0.17.2](https://pypi.org/pypi/qiskit-aer/0.17.2/json)
- CONFLICT (minor): Aer's PyPI classifiers list only Python 3.7–3.12 although wheels exist for 3.13 and 3.14 — [PyPI qiskit-aer](https://pypi.org/project/qiskit-aer/). The hosted Aer API docs are labelled "Qiskit Aer 0.17.1" (page last updated 2025/06/04) while PyPI's latest is 0.17.2 — [Aer docs, SamplerV2](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.primitives.SamplerV2.html)
- qiskit-optimization latest version is 0.7.0, uploaded 2025-08-20 (previous release 0.6.1 on 2024-02-28); `requires_python >=3.9`; depends on `qiskit <3,>=1.1`, `scipy>=1.9.0`, `numpy>=1.17`, `docplex !=2.24.231,>=2.21.207`, `setuptools>=40.1.0`, `networkx>=2.6.3`; classifiers Python 3.9–3.13; extras `cplex` (only Python <3.13, or <3.12 on macOS), `cvx`, `matplotlib`, `gurobi` — [PyPI JSON qiskit-optimization](https://pypi.org/pypi/qiskit-optimization/json)
- qiskit-optimization README: "Qiskit Optimization is no longer officially supported by IBM"; "it is provided as-is and without official support"; "For a fully supported solution and extended mapping features, migrate to the" qiskit-addon-opt-mapper library — [qiskit-optimization README (raw)](https://raw.githubusercontent.com/qiskit-community/qiskit-optimization/main/README.md)
- The qiskit-community/qiskit-optimization repository "was archived by the owner on Jul 12, 2026. It is now read-only." (549 commits) — [GitHub qiskit-community/qiskit-optimization](https://github.com/qiskit-community/qiskit-optimization)
- qiskit-optimization 0.7.0 release notes: removes the dependency on qiskit-algorithms by moving essential components in; adds support for V2 primitives (BaseSamplerV2 / BaseEstimatorV2), described as the most notable change; V1 primitives still work but are deprecated; adds support for Python 3.12 and 3.13 and for Qiskit 2.X; "To run Qiskit Optimization you need a minimum Qiskit version of 1.1.0."; Python 3.8 dropped — [qiskit-optimization release notes](https://qiskit-community.github.io/qiskit-optimization/release_notes.html)
- qiskit-algorithms latest version is 0.4.0, uploaded 2025-08-29; `requires_python >=3.9`; `qiskit>=1.0`, `scipy>=1.4`, `numpy>=1.17`; classifiers Python 3.9–3.13 — [PyPI JSON qiskit-algorithms](https://pypi.org/pypi/qiskit-algorithms/json)
- qiskit-algorithms README: "Qiskit Algorithms is no longer officially supported by IBM" and use is "under your own risk"; no archive notice was visible on its repo page — [GitHub qiskit-community/qiskit-algorithms](https://github.com/qiskit-community/qiskit-algorithms)
- qiskit-algorithms 0.4.0 release notes: follows the deprecation of `BlueprintCircuit` in Qiskit 2.1; adds Python 3.13; passing a `BlueprintCircuit` without its qubit count set to VQE/SamplingVQE is deprecated — [qiskit-algorithms release notes](https://qiskit-community.github.io/qiskit-algorithms/release_notes.html)
- qiskit-ibm-runtime latest version is 0.50.0, uploaded 2026-09-24; `requires_python >=3.10`; requires `qiskit<3,>=2.3.0` — [PyPI JSON qiskit-ibm-runtime](https://pypi.org/pypi/qiskit-ibm-runtime/json); [PyPI JSON 0.50.0](https://pypi.org/pypi/qiskit-ibm-runtime/0.50.0/json)
- qiskit-addon-opt-mapper: only release is 0.1.0, uploaded 2025-11-03; `requires_python >=3.10`; depends on `qiskit<3`, cvxpy, docplex, networkx, numpy, rustworkx, scipy; summary "An addon for optimization problem modeling" — [PyPI JSON qiskit-addon-opt-mapper](https://pypi.org/pypi/qiskit-addon-opt-mapper/json)
- qiskit-addon-opt-mapper docs (v0.1.0, page updated 2025/11/27): provides `OptimizationProblem`, converters `OptimizationProblemToQubo`, `OptimizationProblemToHubo`, `BinaryToSpin`, `SpinToBinary`, translators `to_ising`, `from_docplex_mp`, `to_docplex_mp`, and classical reference solvers `CplexSolver`, `GurobiSolver`, `ScipyMilpSolver`; no QAOA or quantum algorithm is mentioned; it "may occasionally make breaking changes" — [qiskit-addon-opt-mapper docs](https://qiskit.github.io/qiskit-addon-opt-mapper/)
- Migration guide: `QuadraticProgram` -> `OptimizationProblem`, `CplexOptimizer` -> `CplexSolver`, `GurobiOptimizer` -> `GurobiSolver`, `ScipyMilpOptimizer` -> `ScipyMilpSolver`, `OptimizationResult` -> `SolverResult`; the `algorithms`, `optimizers` and `minimum_eigensolvers` modules of qiskit-optimization have no migration path in the new package — [opt-mapper migration guide](https://qiskit.github.io/qiskit-addon-opt-mapper/how_tos/00_migrate_from_qiskit_optimization.html)

### Inferences
- A Python version satisfying every package above is 3.12 (qiskit >=3.10; qiskit-optimization classifiers stop at 3.13; cplex extra needs <3.13; PuLP 4.0.0 needs >=3.12; Aer has wheels). 3.13 also works if the cplex extra is not needed. This is derived from the metadata above, not from a tested install.
- pip will resolve qiskit 2.5.2 + qiskit-aer 0.17.2 + qiskit-optimization 0.7.0 together because the declared ranges overlap (`qiskit<3,>=1.1`; `qiskit>=1.1.0`). Declared compatibility is not the same as tested compatibility: qiskit-optimization 0.7.0 was released a year before Qiskit 2.5 and its repo is now archived, so no fix will arrive if 2.5.x breaks something. The team should pin exact versions in a requirements file and run a smoke test on day one.
- qiskit-algorithms is not needed at all: qiskit-optimization 0.7.0 ships its own QAOA/SamplingVQE/NumPyMinimumEigensolver, and the low-level route needs neither package.
- qiskit-ibm-runtime is unnecessary for a simulator-only project; omitting it removes a dependency with a tight qiskit floor (>=2.3.0).
- The "officially supported" stack for this project is therefore qiskit + qiskit-aer (+ optionally qiskit-addon-opt-mapper for modelling), with QAOA assembled by hand.

### Gaps
- I did not find a statement, on any official page, that qiskit-optimization 0.7.0 has been tested against Qiskit 2.4/2.5. The archived repo's issue tracker was not inspected.
- Upload date of the first qiskit 2.5.0 release and the exact Qiskit 3.0 timeline were not found.
- The qiskit-algorithms repo page showed no archive banner, but I could not confirm its last commit date or whether it has an active maintainer.
- I did not confirm that Aer 0.17.2 (Sept 2025) has been tested with Qiskit 2.5; no Aer release newer than 0.17.2 was shown on PyPI.

## 2. Two implementation routes: verified names, import paths and signatures

### Takeaway
Both routes exist today. Route 2 (SparsePauliOp + qaoa_ansatz/QAOAAnsatz + V2 primitives + SciPy) depends only on officially supported packages and matches the current IBM tutorial, so it is the more robust and transparent choice; Route 1 (qiskit_optimization QuadraticProgram + MinimumEigenOptimizer + its own QAOA) is shorter but rests on an archived, unsupported package. A sensible hybrid is to use QuadraticProgram / QuadraticProgramToQubo (or opt-mapper) only for modelling and exact checks, and run QAOA by hand.

### Cited Findings
Route 1 (high-level, qiskit-optimization 0.7.0):
- Modules present in the 0.7.0 API docs: `algorithms`, `applications`, `converters`, `problems`, `translators`, `minimum_eigensolvers`, `optimizers`, `utils` — [qiskit-optimization API index](https://qiskit-community.github.io/qiskit-optimization/apidocs/qiskit_optimization.html)
- `qiskit_optimization.converters` contains `QuadraticProgramConverter`, `InequalityToEquality`, `IntegerToBinary`, `LinearEqualityToPenalty`, `LinearInequalityToPenalty`, `MaximizeToMinimize`, `MinimizeToMaximize`, `QuadraticProgramToQubo` — [qiskit-optimization API index](https://qiskit-community.github.io/qiskit-optimization/apidocs/qiskit_optimization.html)
- `qiskit_optimization.minimum_eigensolvers` contains `NumPyMinimumEigensolver`, `SamplingVQE`, `QAOA`, `VQE` and result classes; `qiskit_optimization.optimizers` contains `COBYLA`, `NELDER_MEAD`, `SPSA`, `SciPyOptimizer`; `qiskit_optimization.translators` has functions `from_docplex_mp`, `to_docplex_mp`, `from_gurobipy`, `to_gurobipy`, `from_ising`, `to_ising`; `qiskit_optimization.utils` has `algorithm_globals` — [qiskit-optimization API index](https://qiskit-community.github.io/qiskit-optimization/apidocs/qiskit_optimization.html)
- `qiskit_optimization.algorithms` contains `MinimumEigenOptimizer`, `CplexOptimizer`, `GurobiOptimizer`, `ScipyMilpOptimizer`, `WarmStartQAOAOptimizer`, `RecursiveMinimumEigenOptimizer`, `GroverOptimizer`, `SolutionSample`, `OptimizationResultStatus` and others — [qiskit-optimization API index](https://qiskit-community.github.io/qiskit-optimization/apidocs/qiskit_optimization.html)
- Import paths changed in 0.7.0: QAOA/VQE/NumPyMinimumEigensolver move from `qiskit_algorithms.minimum_eigensolvers` to `qiskit_optimization.minimum_eigensolvers`; `algorithm_globals` from `qiskit_algorithms.utils` to `qiskit_optimization.utils`; optimizers from `qiskit_algorithms.optimizers` to `qiskit_optimization.optimizers` (not all qiskit-algorithms optimizers were migrated) — [qiskit-optimization release notes](https://qiskit-community.github.io/qiskit-optimization/release_notes.html)
- QAOA signature (0.7.0 docs): `QAOA(sampler, optimizer, *, reps=1, initial_state=None, mixer=None, initial_point=None, aggregation=None, callback=None, pass_manager=None)`; sampler typed `BaseSamplerV1 | BaseSamplerV2`; if `initial_point` is None a random point within parameter bounds is used (bounds -2pi to 2pi if the ansatz gives none) — [QAOA API, qiskit-optimization 0.7.0](https://qiskit-community.github.io/qiskit-optimization/stubs/qiskit_optimization.minimum_eigensolvers.QAOA.html)
- `MinimumEigenOptimizer(min_eigen_solver, penalty=None, converters=None)`; with `converters=None` an internal `QuadraticProgramToQubo` is used; `solve(problem)` returns `MinimumEigenOptimizationResult` — [MinimumEigenOptimizer API](https://qiskit-community.github.io/qiskit-optimization/stubs/qiskit_optimization.algorithms.MinimumEigenOptimizer.html)
- Current README example (V2 primitives): `from qiskit_optimization.minimum_eigensolvers import QAOA`, `from qiskit_optimization.optimizers import SPSA`, `from qiskit_aer.primitives import SamplerV2`, `sampler = SamplerV2(seed=seed, default_shots=10000)`, `pass_manager = generate_preset_pass_manager(optimization_level=1, backend=AerSimulator())`, `qaoa = QAOA(sampler=sampler, optimizer=spsa, reps=5, pass_manager=pass_manager)`, `algorithm = MinimumEigenOptimizer(qaoa)` — [GitHub qiskit-community/qiskit-optimization](https://github.com/qiskit-community/qiskit-optimization)
- The 0.7.0 prelude says the V2-primitive migration "requires attention to pass manager requirements for hardware and simulator backends." — [qiskit-optimization release notes](https://qiskit-community.github.io/qiskit-optimization/release_notes.html)
- `QuadraticProgramToQubo(penalty=None)`; its `__init__` chains, in order: `LinearInequalityToPenalty`, `InequalityToEquality(mode="integer")`, `IntegerToBinary()`, `LinearEqualityToPenalty`, `MaximizeToMinimize()`; continuous variables and quadratic constraints are rejected; non-integer float coefficients in constraints are rejected with a message beginning "Can not convert inequality constraints to equality constraint because" — [quadratic_program_to_qubo.py source](https://raw.githubusercontent.com/qiskit-community/qiskit-optimization/main/qiskit_optimization/converters/quadratic_program_to_qubo.py)
- Penalty default, docs: "If None is passed, a penalty factor will be automatically calculated on every conversion." — [QuadraticProgramToQubo API](https://qiskit-community.github.io/qiskit-optimization/stubs/qiskit_optimization.converters.QuadraticProgramToQubo.html)
- Penalty default, source (`_auto_define_penalty`): returns `1.0 + (lin_b.upperbound - lin_b.lowerbound) + (quad_b.upperbound - quad_b.lowerbound)` from the objective's linear and quadratic bounds; if any constraint coefficient or rhs is a non-integer float it returns `default_penalty = 1e5` and logs a warning that "The value could be too small. If so, set the penalty coefficient manually." — [linear_equality_to_penalty.py source](https://raw.githubusercontent.com/qiskit-community/qiskit-optimization/main/qiskit_optimization/converters/linear_equality_to_penalty.py)
- `LinearInequalityToPenalty(penalty=None)` converts only four inequality forms without slack (x, y, x_i binary; P the penalty): `x <= y` -> `P(x - xy)`; `x >= y` -> `P(y - xy)`; `sum x_i <= 1` (n >= 2) -> `P * sum_{i<j} x_i x_j`; `sum x_i >= n-1` (n >= 2) -> `P * sum_{i<j} (1-x_i)(1-x_j)`. Constraints not matching a pattern are left unchanged (and then fall through to InequalityToEquality, which adds slack) — [LinearInequalityToPenalty API, 0.7.0](https://qiskit-community.github.io/qiskit-optimization/stubs/qiskit_optimization.converters.LinearInequalityToPenalty.html)
- 0.7.0 deprecates `export_as_lp_string()`, `read_from_lp_file()`, `write_to_lp_file()` on QuadraticProgram; use `prettyprint()` to print a model. A 0.6.0 fix corrected slack-variable ordering in `InequalityToEquality` — [qiskit-optimization release notes](https://qiskit-community.github.io/qiskit-optimization/release_notes.html)

Route 2 (low-level, official IBM tutorial pattern):
- The IBM "Quantum approximate optimization algorithm" tutorial requires "Qiskit SDK v2.0 or later" and Qiskit Runtime v0.22 or later; imports `from qiskit.quantum_info import SparsePauliOp`, `from qiskit.circuit.library import QAOAAnsatz`, `from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager`, `from scipy.optimize import minimize`, and `EstimatorV2`/`SamplerV2` from `qiskit_ibm_runtime` — [IBM tutorial: QAOA](https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-optimization-algorithm)
- Tutorial steps: cost Hamiltonian via `SparsePauliOp.from_sparse_list(max_cut_paulis, n)` with `("ZZ", [i, j], weight)` tuples; ansatz `QAOAAnsatz(cost_operator=cost_hamiltonian, reps=2)` then `circuit.measure_all()`; `pm = generate_preset_pass_manager(optimization_level=3, backend=backend)`; cost function applies `hamiltonian.apply_layout(ansatz.layout)`, submits the PUB `(ansatz, isa_hamiltonian, params)` to `estimator.run` and reads `results.data.evs`; optimiser `minimize(cost_func_estimator, init_params, args=(...), method="COBYLA", tol=1e-2)` — [IBM tutorial: QAOA](https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-optimization-algorithm)
- The tutorial notes that the general QUBO Hamiltonian includes linear (single-Z) terms, needed for weighted graphs or other QUBO-expressible problems; it verifies the small example against brute-force enumeration — [IBM tutorial: QAOA](https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-optimization-algorithm)
- Function form: `qaoa_ansatz(cost_operator, reps=1, initial_state=None, mixer_operator=None, insert_barriers=False, name='QAOA', flatten=True)` returns a `QuantumCircuit` (docs built from `stable/2.5`) — [qaoa_ansatz API](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.qaoa_ansatz)
- Class form: `QAOAAnsatz(cost_operator=None, reps=1, initial_state=None, mixer_operator=None, name='QAOA', flatten=None)`, subclass of `EvolvedOperatorAnsatz`; the page strongly recommends `flatten=True` for anything other than visualisation because nesting adds parameter-binding overhead — [QAOAAnsatz API](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.QAOAAnsatz)
- CONFLICT on deprecation status of `QAOAAnsatz`: the Qiskit 2.1 release notes state "All QuantumCircuit subclasses are now deprecated in favor of their alternatives introduced in Qiskit v1.3", that `BlueprintCircuit` is deprecated, that `EvolvedOperatorAnsatz` is replaced by `evolved_operator_ansatz()`, and that these "will only be removed in Qiskit v3.0" — [Qiskit 2.1 release notes](https://quantum.cloud.ibm.com/docs/en/api/qiskit/release-notes/2.1). However the 2.5 API page for `QAOAAnsatz` shows no deprecation notice — [QAOAAnsatz API](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.QAOAAnsatz) — the `stable/2.5` source shows no deprecation decorator on the class — [qaoa_ansatz.py, stable/2.5](https://raw.githubusercontent.com/Qiskit/qiskit/stable/2.5/qiskit/circuit/library/n_local/qaoa_ansatz.py) — and the current IBM tutorial still imports the class — [IBM tutorial: QAOA](https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-optimization-algorithm)
- Reference primitives in the SDK: `qiskit.primitives.StatevectorSampler(*, default_shots=1024, seed=None)`, "incompatible with mid-circuit measurements" — [StatevectorSampler API](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.primitives.StatevectorSampler); `qiskit.primitives.StatevectorEstimator(*, default_precision=0.0, seed=None)`, exact for unitary-only circuits, error bars (`stds`) are 0 — [StatevectorEstimator API](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.primitives.StatevectorEstimator)
- Aer primitives: `qiskit_aer.primitives.SamplerV2(*, default_shots: int = 1024, seed: int | None = None, options: dict | None = None)` with `backend_options` and `run_options` and a `from_backend(backend, **options)` constructor — [Aer SamplerV2](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.primitives.SamplerV2.html); `qiskit_aer.primitives.EstimatorV2(*, options: dict | None = None)` with `default_precision` (default 0.0), `backend_options`, `run_options` — [Aer EstimatorV2](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.primitives.EstimatorV2.html)

Removed / legacy names to avoid:
- qiskit-optimization 0.6.0 removed `QuantumInstance`, Opflow and the runtime client classes, and replaced the `qiskit.algorithms` dependency with qiskit-algorithms; 0.7.0 then dropped qiskit-algorithms as a dependency — [qiskit-optimization release notes](https://qiskit-community.github.io/qiskit-optimization/release_notes.html)

### Inferences
- Any tutorial that imports `qiskit.algorithms`, `qiskit.opflow`, `QuantumInstance`, `qiskit.utils.algorithm_globals`, `Aer.get_backend('qasm_simulator')` with `execute`, or `from qiskit.primitives import Sampler` (V1) is out of date for this stack; tutorials importing `qiskit_algorithms.minimum_eigensolvers.QAOA` are one generation behind the 0.7.0 import path.
- Use the function `qaoa_ansatz(...)` in new code. It is the documented v1.3+ replacement style, defaults to `flatten=True`, and avoids the unresolved deprecation question around the `QAOAAnsatz` class and Qiskit 3.0.
- Route 2 is more robust for students because (a) every dependency is IBM-supported, (b) the cost function, the Hamiltonian and the decoding are visible and testable by hand on a 2-variable example, and (c) nothing depends on an archived repo. Its cost is roughly 60–100 lines of own code and full responsibility for bit ordering and the QUBO -> Ising mapping.
- Route 1 is fastest to a first result and gives `prettyprint()`, automatic penalty and built-in interpretation back to the original variables, which is valuable as a cross-check even if the final experiment uses Route 2.
- For Q-Rescue specifically, "each call gets at most one ambulance" and "each ambulance takes at most one call" are both of the form `sum x_i <= 1`, which `LinearInequalityToPenalty` converts with pairwise penalties and no slack qubits. A constraint with a single eligible variable (n = 1) is trivially satisfied and should simply be omitted.
- The automatic penalty is an upper-bound style value (1 + objective range). With non-integer travel-time coefficients in the objective that is fine, but non-integer coefficients in constraints trigger the 1e5 fallback, which would swamp the objective and flatten the QAOA landscape. Q-Rescue's constraints have 0/1 coefficients, so the fallback should not trigger; the team should still print and report the penalty actually used and do a small penalty sweep.

### Gaps
- I did not fetch the API pages for `to_ising` (return value and sign/offset convention), `SparsePauliOp.from_sparse_list` (exact signature), `MinimumEigenOptimizationResult` (`samples`, `raw_samples`, `status`) or `CplexOptimizer`/`GurobiOptimizer`; their existence is confirmed from the module index and tutorial only, not their signatures.
- The opt-mapper `to_ising` usage and whether `OptimizationProblemToQubo` uses the same penalty rule were not verified.
- No official example was found that wires `qiskit-addon-opt-mapper` output into `qaoa_ansatz` for a constrained assignment problem.

## 3. Qubit counts and statevector-simulation limits

### Takeaway
A pairwise-penalty formulation needs exactly |E| qubits (12 for a full 3x4), explicit unserved variables add one per call (16), and slack or idle variables on every constraint add A + C (19); all of these fit easily in laptop memory since a complex128 statevector costs 16 * 2^n bytes. No official source gives QAOA wall-clock times at 8–20 qubits, so the team must measure these itself.

### Cited Findings
- Aer docs: a statevector uses 2^n complex values at 16 bytes each; `max_memory_mb` caps state memory (0 = use system memory); `precision` can be single or double (default double) — [Aer AerSimulator docs](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.AerSimulator.html)
- Aer `statevector_parallel_threshold` defaults to 14 qubits: OpenMP parallelisation of gate application only starts above that size; `statevector_sample_measure_opt` defaults to 10 — [Aer AerSimulator docs](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.AerSimulator.html)
- `sum x_i <= 1` is penalised as `P * sum_{i<j} x_i x_j` with no extra variables; other inequality forms are left for slack conversion — [LinearInequalityToPenalty API](https://qiskit-community.github.io/qiskit-optimization/stubs/qiskit_optimization.converters.LinearInequalityToPenalty.html)
- QuadraticProgramToQubo applies `InequalityToEquality(mode="integer")` then `IntegerToBinary()` to any inequality not caught by the penalty patterns — [quadratic_program_to_qubo.py source](https://raw.githubusercontent.com/qiskit-community/qiskit-optimization/main/qiskit_optimization/converters/quadratic_program_to_qubo.py)

### Inferences
Qubit counts (my arithmetic; A ambulances, C calls, full eligibility so |E| = A*C; fewer if some pairs are ineligible):

| Formulation | Extra qubits | 2x3 | 3x4 | 4x5 |
|---|---|---|---|---|
| (a) x_ac only; both "<= 1" families as pairwise penalties, no slack | 0 | 6 | 12 | 20 |
| (b) one-hot per call with explicit unserved variable u_c (sum_a x_ac + u_c = 1); ambulance "<= 1" still pairwise | + C | 9 | 16 | 25 |
| (c) slack/idle variable on every constraint (calls and ambulances), e.g. forcing InequalityToEquality | + A + C | 11 | 19 | 29 |
| (c') slack only on the ambulance family | + A | 8 | 15 | 24 |

- A binary slack on a "sum <= 1" constraint is mathematically the same thing as an explicit "unserved"/"idle" variable, so (b)/(c) are the slack formulations under a friendlier name. Each "<= 1" constraint over binaries needs only one slack bit because the slack range is {0, 1}.
- In formulation (a) nothing rewards serving a call unless the objective does: with A < C at least C − A calls are necessarily unserved, and the objective must carry an explicit negative reward (or unserved penalty) per assignment, otherwise the all-zeros bitstring is feasible and optimal for a pure cost-minimisation objective. This is a modelling decision the team must make and document.
- Statevector memory at complex128 (16 * 2^n bytes): 8 qubits = 4 KiB; 12 = 64 KiB; 16 = 1 MiB; 20 = 16 MiB; 25 = 512 MiB; 29 = 8 GiB; 30 = 16 GiB. So memory is irrelevant up to ~25 qubits on any laptop, 29 is marginal on 16 GB RAM, and time (number of circuit evaluations x gates x 2^n) becomes the binding constraint first.
- Brute-force search space: 2^12 = 4,096; 2^16 = 65,536; 2^20 = 1,048,576 bitstrings. All are trivially enumerable classically with vectorised NumPy, which is why brute force is a legitimate ground truth for every instance size in scope.
- The 3x4 instance in formulation (a) or (b) (12–16 qubits) is the sweet spot: small enough to iterate quickly and to enumerate exactly, large enough that uniform random sampling does not trivially hit the optimum with few shots. 4x5 with slack (29 qubits) should be declared out of scope.

### Gaps
- I found no authoritative, citable benchmark of wall-clock time per QAOA optimisation at 8/12/16/20 qubits on a laptop with Aer 0.17 / Qiskit 2.5. Any runtime number in the report must come from the team's own timing (record CPU, RAM, depth p, optimizer iterations, shots).
- The typical gate count of the transpiled cost layer for this specific QUBO (dense pairwise penalties produce many RZZ terms) was not measured.

## 4. Classical optimizer, depth, initial parameters and CVaR

### Takeaway
IBM's tutorial uses COBYLA via scipy.optimize.minimize, and the literature says optimizer choice barely matters in exact statevector simulation but matters under shot noise (COBYLA and Nelder-Mead degrade; SPSA/Adam-type methods hold up). Random initialisation is the main documented failure mode, so use a structured start (linear ramp / TQA, or interpolate from p to p+1) plus a few multi-starts; CVaR aggregation is available as the `aggregation` argument of QAOA/SamplingVQE in qiskit-optimization 0.7.0.

### Cited Findings
- IBM tutorial uses `method="COBYLA"` with `tol=1e-2`, initial parameters `initial_gamma = np.pi`, `initial_beta = np.pi / 2`, reps = 2 for the small example and reps = 1 for the 100-qubit one; it says QAOA has no principled default angles and that any bounded choice works as a warm start for small problems — [IBM tutorial: QAOA](https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-optimization-algorithm)
- IBM tutorial's convergence guidance: a smoothly decreasing, plateauing curve signals convergence; a noisy, non-monotonic curve suggests too few shots, poor initial parameters, or noise-dominated depth — [IBM tutorial: QAOA](https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-optimization-algorithm)
- qiskit-optimization's README example uses `SPSA(maxiter=250)` with a shot-based Aer `SamplerV2` (10,000 shots) and `reps=5` — [GitHub qiskit-community/qiskit-optimization](https://github.com/qiskit-community/qiskit-optimization)
- Optimizers shipped in qiskit-optimization 0.7.0: `COBYLA`, `NELDER_MEAD`, `SPSA`, `SciPyOptimizer` (a generic wrapper); `optimizer` may also be any callable implementing the `Minimizer` protocol — [qiskit-optimization API index](https://qiskit-community.github.io/qiskit-optimization/apidocs/qiskit_optimization.html); [QAOA API](https://qiskit-community.github.io/qiskit-optimization/stubs/qiskit_optimization.minimum_eigensolvers.QAOA.html)
- Pellow-Jarman et al., Sci Rep 14, 16011 (2024): "there is no significant difference in the performance of classical optimizers in a state vector simulation"; "the Adam and AMSGrad optimizers perform best in the presence of shot noise"; under real device noise SPSA, Adam and AMSGrad are the top performers; on 5-qubit minimum-vertex-cover instances quality improves up to about six layers and then declines on noisy hardware — [arXiv:2307.10149](https://arxiv.org/abs/2307.10149)
- A search summary of the same paper's body reports that COBYLA and Nelder-Mead are noticeably affected by shot noise while SPSA slightly outperforms the others in that setting (secondary summary of the full text; the abstract itself does not name COBYLA/Nelder-Mead) — [arXiv:2307.10149 PDF](https://arxiv.org/pdf/2307.10149)
- Scriva et al., Phys. Rev. A 109, 032408 (2024): with measurement shot noise, energy-based optimizers give resource scaling "comparable to direct brute-force search", and a gradient-based optimizer improves this "at most quadratically" (studied for VQE-style variational optimisation) — [arXiv:2308.00044](https://arxiv.org/abs/2308.00044)
- Zhou et al., Phys. Rev. X 10, 021067 (2020): proposes heuristic strategies to find quasi-optimal p-level parameters in O(poly(p)) time, whereas "the standard strategy of random initialization requires 2^{O(p)} optimization runs to achieve similar performance" — [arXiv:1812.01041](https://arxiv.org/abs/1812.01041)
- Sack & Serbyn, Quantum 5, 491 (2021): "random initialization of the QAOA is prone to converging to local minima with sub-optimal performance"; Trotterized quantum annealing (TQA) initialisation gives "the same performance as the best result out of an exponentially scaling number of random initializations" — [arXiv:2101.05742](https://arxiv.org/abs/2101.05742)
- Montanez-Barrera & Michielsen, npj Quantum Information 11, 131 (2025): "fixed linear ramp schedules, linear ramp QAOA (LR-QAOA), can efficiently approximate optimal solutions across diverse COPs" without classically optimising the parameters — [arXiv:2405.09169](https://arxiv.org/abs/2405.09169)
- CVaR: Barkoutsos et al., Quantum 4, 256 (2020): "we propose the Conditional Value-at-Risk as an aggregation function", which "leads to faster convergence to better solutions for all combinatorial optimization problems tested in our study" — [arXiv:1907.04769](https://arxiv.org/abs/1907.04769)
- Current implementation of CVaR: the `aggregation` parameter of `qiskit_optimization.minimum_eigensolvers.QAOA` (inherited from `SamplingVQE`) is "a float or callable"; a float is the CVaR parameter alpha in [0, 1] — [QAOA API, qiskit-optimization 0.7.0](https://qiskit-community.github.io/qiskit-optimization/stubs/qiskit_optimization.minimum_eigensolvers.QAOA.html)
- Default initial point in qiskit-optimization's QAOA is random within bounds when `initial_point=None` — [QAOA API](https://qiskit-community.github.io/qiskit-optimization/stubs/qiskit_optimization.minimum_eigensolvers.QAOA.html)

### Inferences
- Recommended default for Q-Rescue: optimise against the exact statevector expectation (no shot noise) with COBYLA, as in the IBM tutorial; in that regime the literature finds optimizers roughly equivalent, so COBYLA's simplicity wins. If the team optimises against sampled estimates instead, switch to SPSA or raise shots, and say so.
- L-BFGS-B / BFGS with finite-difference gradients is viable on an exact statevector (the objective is deterministic and smooth) and can be run through `scipy.optimize.minimize`; I found no official Qiskit doc recommending it for QAOA, so present it as an optional comparison, not a default.
- Depth: p = 1, 2, 3 is a defensible sweep (2p parameters each). Report all three; do not report only the best. On a noiseless simulator deeper p should not hurt in principle, so any degradation with p signals optimizer stagnation rather than physics.
- Initialisation plan that is cheap and defensible: (i) linear-ramp/TQA-style start (gammas increasing, betas decreasing across layers), (ii) for p+1 start from the interpolated p-level optimum, (iii) K random restarts (e.g. 10–20) as a control so the benefit of structured initialisation is shown rather than assumed. Never pass `initial_point=None` silently in Route 1, since that means an unseeded-looking random start.
- CVaR in Route 2 is a few lines: sort sampled objective values and average the best alpha fraction (e.g. alpha = 0.1–0.25). Note that CVaR changes the objective being optimised, so the plain expectation, the CVaR value and the sampled-optimum probability must be reported separately.
- For dense penalty QUBOs the energy scale is dominated by the penalty P, so parameter landscapes become stiff in gamma; rescaling the Hamiltonian (dividing by its largest coefficient) before optimisation is a common practical fix — this is my inference, not a cited recommendation.

### Gaps
- I did not retrieve the Fernández-Pendás et al. twelve-optimizer QAOA study or arXiv:2408.00557 directly; they appeared only in search summaries and should not be cited without checking.
- No official IBM/Qiskit page was found that recommends a specific optimizer or p for constrained (penalty) QUBOs, or that names INTERP/FOURIER; those names are from the body of Zhou et al., not its abstract.
- No built-in Qiskit helper for linear-ramp or TQA initial points was found in the pages read.

## 5. Simulation settings: exact vs shots, shot counts, seeds, noise, Aer methods

### Takeaway
Optimise on exact statevector expectations, then draw a fixed, seeded number of shots from the final circuit to evaluate solutions; a noise model is not needed for a first experiment. Seeds must be set in four places (sampler/estimator, transpiler, optimizer start point, any NumPy randomness).

### Cited Findings
- `StatevectorEstimator` results are exact when the circuit contains only unitary operations; non-unitary operations can make them stochastic and `seed` then makes them reproducible; `stds` are 0 — [StatevectorEstimator API](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.primitives.StatevectorEstimator)
- `StatevectorSampler(default_shots=1024, seed=None)`: seed may be an int or `np.random.Generator`; if None "a randomly seeded default RNG" is used — [StatevectorSampler API](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.primitives.StatevectorSampler)
- Aer `SamplerV2(default_shots=1024, seed=None, options=None)`: "The seed for random number generation. If None, a random seeded default RNG will be used."; `options` carries `backend_options` (passed to `AerSimulator`) and `run_options` (passed to `AerSimulator.run()`) — [Aer SamplerV2](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.primitives.SamplerV2.html)
- Aer `EstimatorV2` options: `default_precision` (default 0.0), `backend_options`, `run_options`; when a precision is set, estimates are sampled from a normal distribution centred on the expectation value — [Aer EstimatorV2](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.primitives.EstimatorV2.html)
- Aer simulation methods: `automatic` (default), `statevector` (dense; noisy runs sample a noisy circuit per shot), `density_matrix`, `stabilizer` (Clifford only), `matrix_product_state`, `extended_stabilizer`, `unitary`, `superop`, `tensor_network` (GPU only) — [Aer AerSimulator docs](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.AerSimulator.html)
- Shot counts used in official material: IBM tutorial uses 1,000 shots per Estimator evaluation and 10,000 for final sampling — [IBM tutorial: QAOA](https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-optimization-algorithm); the qiskit-optimization README uses `default_shots=10000` — [GitHub qiskit-community/qiskit-optimization](https://github.com/qiskit-community/qiskit-optimization); default for both Sampler implementations is 1024 — [Aer SamplerV2](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.primitives.SamplerV2.html)
- `algorithm_globals` now lives in `qiskit_optimization.utils` (migrated from `qiskit_algorithms.utils`) and the README example seeds through it and through `SamplerV2(seed=seed, ...)` — [qiskit-optimization release notes](https://qiskit-community.github.io/qiskit-optimization/release_notes.html); [GitHub qiskit-community/qiskit-optimization](https://github.com/qiskit-community/qiskit-optimization)
- IBM tutorial applies dynamical decoupling and twirling only because it targets real hardware; these are error-suppression options of the Runtime primitives — [IBM tutorial: QAOA](https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-optimization-algorithm)

### Inferences
- Two-stage protocol: (1) optimisation loop on exact expectation (`StatevectorEstimator`, or Aer `EstimatorV2` with precision 0) so the optimizer sees a deterministic objective; (2) final evaluation by sampling N shots from the optimised circuit with a seeded sampler. With n <= 16 the team can additionally compute the exact output distribution from the statevector and report exact success/feasibility probabilities, with shots shown only as the "what a device would give" view.
- Shot count is a statistical-error choice: the standard error of an estimated probability p from N shots is sqrt(p(1-p)/N), so N = 1024 gives at most about +/-1.6 percentage points (1 s.e.) and N = 8192 about +/-0.55. 1024–8192 is defensible; state N and keep it identical for QAOA and for the random baseline.
- Shot counts must be read against the search-space size. For 12 qubits (4,096 states) with one optimal bitstring, uniform random sampling finds the optimum at least once with probability 1 − (1 − 1/4096)^N: about 22% at N = 1024, 63% at N = 4096 and 86% at N = 8192. "QAOA's best sample was optimal" is therefore nearly meaningless at these shot counts; the per-shot probability of the optimum is the honest metric.
- Seeds to fix and log: sampler/estimator `seed`; `seed_transpiler` on the pass manager; the optimizer's initial point (generate from a seeded `np.random.default_rng`); `algorithm_globals.random_seed` if Route 1 is used; plus the instance-generation seed. Use different seeds across repeated runs and the same seed list for every method.
- Noise model: omit in the first experiment. The claim being tested is algorithmic behaviour on a constrained QUBO, and a device noise model adds a fake-backend dependency, slower simulation and an extra story to explain. If added later, label it a sensitivity study.
- Aer method: explicit `method="statevector"` (do not rely on `automatic`) so runs are comparable; `density_matrix` only if a noise model is added, and note its memory is 16 * 4^n bytes (my arithmetic: 12 qubits = 256 MiB, 16 qubits = 64 GiB), which rules out noisy density-matrix simulation at 16 qubits on a laptop.
- For a simulator with all-to-all connectivity, heavy transpilation is unnecessary; optimisation level 1 as in the qiskit-optimization README is sufficient, with a fixed transpiler seed.

### Gaps
- The Aer page read did not document `seed_simulator` itself (it is passed through `run_options`); the exact key name and whether Aer `EstimatorV2` with precision 0 is strictly exact were not confirmed from the docs.
- Whether `generate_preset_pass_manager` still accepts `seed_transpiler` under that exact name in 2.5 was not checked on its API page.
- No official guidance stating a recommended shot count for small QAOA simulations was found; the numbers above are examples from official tutorials, not recommendations.

## 6. Constraint handling: penalties vs constraint-preserving mixers; treating infeasible samples

### Takeaway
The penalty method is the only approach with turnkey tooling; custom mixers are supported as arguments (`mixer_operator` + `initial_state` in `qaoa_ansatz`, `mixer` + `initial_state` in qiskit-optimization's QAOA) but Qiskit ships no ready-made XY/ring mixer or W-state initialiser for assignment constraints, so that is stretch-goal work. Infeasible samples should be counted and reported, never silently repaired.

### Cited Findings
- `qaoa_ansatz` docs: `mixer_operator` is "An optional custom mixer, which defaults to global Pauli-X" rotations, and with a custom mixer "the initial_state might also require modification"; for `initial_state`: "If a custom mixer is chosen, this circuit should be set to prepare its ground state, to appropriately fulfill the annealing conditions." — [qaoa_ansatz.py, stable/2.5](https://raw.githubusercontent.com/Qiskit/qiskit/stable/2.5/qiskit/circuit/library/n_local/qaoa_ansatz.py); [qaoa_ansatz API](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.qaoa_ansatz)
- `QAOAAnsatz` class: `mixer_operator` may be a `BaseOperator` or a parameterised `QuantumCircuit`; default initial state is Hadamards on all qubits — [QAOAAnsatz API](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.QAOAAnsatz)
- qiskit-optimization QAOA: `mixer` is a `QuantumCircuit` or `BaseOperator` that "can constrain the search to a feasible subspace or support warm-starting" — [QAOA API, qiskit-optimization 0.7.0](https://qiskit-community.github.io/qiskit-optimization/stubs/qiskit_optimization.minimum_eigensolvers.QAOA.html)
- Wang, Rubin, Dominy, Rieffel, Phys. Rev. A 101, 012320 (2020): "This work explores strategies for enforcing hard constraints by using XY-Hamiltonians as mixing operators"; the approach shows "a significant improvement over the general X-mixer"; "the generalized W-state yields better performance than easier-to-generate classical initial states when XY mixers are used" — [arXiv:1904.09314](https://arxiv.org/abs/1904.09314)
- Penalty tooling: `LinearEqualityToPenalty`, `LinearInequalityToPenalty`, and automatic penalty selection as described in section 2 — [linear_equality_to_penalty.py source](https://raw.githubusercontent.com/qiskit-community/qiskit-optimization/main/qiskit_optimization/converters/linear_equality_to_penalty.py)
- qiskit-optimization 0.2.0 upgrade note: `MinimumEigenOptimizer.solve()` returns the best solution in terms of the original problem — [qiskit-optimization release notes](https://qiskit-community.github.io/qiskit-optimization/release_notes.html)
- IBM tutorial uses two different decoding rules: most likely bitstring for the small example, and the lowest-cost sampled bitstring for the 100-qubit example — [IBM tutorial: QAOA](https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-optimization-algorithm)
- A 2026 hardware benchmark (as summarised in search results) used a matched uniform-random control and found most feasible low-fidelity outcomes fell within the random range (secondary summary; original not opened) — [search result: Benchmarking Standard and Qubit-Efficient Quantum Optimization on Real Hardware](https://huggingface.co/papers/2607.11637.md)

### Inferences
- An XY/ring mixer preserves a one-hot (Hamming-weight-1) block. Q-Rescue has two overlapping constraint families (per call and per ambulance) on the same variables; a mixer that preserves one family does not automatically preserve the other, so a hybrid (XY mixer on one family, penalty on the other) or a more elaborate mixer would be needed. With "<= 1" rather than "= 1" constraints the one-hot block structure only exists if unserved/idle variables are added (formulation (b)/(c)). This makes the mixer route a genuine research task, not a configuration option; recommend penalty as the baseline and one XY-mixer variant only as a clearly labelled stretch experiment.
- Reporting rules for samples: (1) classify every sampled bitstring as feasible/infeasible against the original constraints (not via the penalised energy); (2) report feasibility rate = feasible shots / total shots; (3) report three decoders side by side — most-probable bitstring, best feasible sample, and expectation value — because they answer different questions and the IBM tutorial itself uses two of them; (4) if no feasible sample appears, record a failure for that run and show the classical exact solution explicitly labelled as a fallback; (5) never apply a repair heuristic without reporting pre-repair numbers, since repair can be responsible for all of the apparent quality.
- "Best feasible sample" is a max over N draws and is strongly biased upward with N; always pair it with the same statistic for N uniform random bitstrings.
- Penalty scaling should be treated as an experimental factor: too small yields infeasible optima of the QUBO; too large compresses the objective signal relative to the penalty and hurts optimisation. Verify by brute force that the QUBO's minimiser is feasible and equals the original optimum for the chosen P before running any QAOA.

### Gaps
- No Qiskit-provided XY-mixer, ring-mixer or W/Dicke-state preparation helper for QAOA was found in the pages read; I did not search the whole circuit library, so absence is not proven.
- The abstract of the XY-mixer paper does not itself use the phrases "Hamming weight" or "feasible subspace"; the mechanism statement in my inference comes from general knowledge of the paper and should be checked in the full text before quoting.
- No official Qiskit statement on how to treat infeasible samples was found; the rules above are methodology recommendations.

## 7. Evaluating repeated stochastic runs and fair quantum-vs-classical comparison

### Takeaway
Published guidance converges on: brute-force ground truth, a uniform-random-sampling baseline at equal sample count, strong classical heuristics (simulated annealing), disclosure of how parameters were tuned, many instances/seeds with robust statistics, and conclusions scoped to what was tested. No single canonical "QAOA benchmarking standard" exists.

### Cited Findings
- Abbas et al., "Challenges and Opportunities in Quantum Optimization", Nat Rev Phys (2024), 46 authors: stresses benchmarking by "proposing clear metrics to conduct appropriate comparisons with classical optimization techniques" — [arXiv:2312.02279](https://arxiv.org/abs/2312.02279)
- Koch et al., "Quantum Optimization Benchmarking Library - The Intractable Decathlon", Nature Computational Science 6, 653-671 (2026): presents ten problem classes for "systematic, fair, and comparable benchmarks for quantum optimization methods"; baseline results "illustrate a standardized form to present benchmarking solutions, which has been designed to ensure comparability"; classes become hard for classical methods at sizes "ranging from less than 100" variables upward — [arXiv:2504.03832](https://arxiv.org/abs/2504.03832)
- Lubinski et al., "Optimization Applications as Quantum Performance Benchmarks", ACM Trans. Quantum Computing 5(3), 2024: framework assessing "the trade-off between run-time execution performance and the solution quality" for iterative hybrid applications, shown as performance profiles over time — [arXiv:2302.02278](https://arxiv.org/abs/2302.02278)
- Montanez-Barrera, Michielsen, Bernal Neira (2025): LR-QAOA benchmarking protocol that identifies "when performance becomes statistically indistinguishable from random sampling" — [arXiv:2502.06471](https://arxiv.org/abs/2502.06471)
- Search summary of that paper's body: a result is meaningful only while its approximation ratio lies above the confidence interval of a random sampler, and that interval widens as the number of samples decreases (secondary summary of full text) — [arXiv:2502.06471 PDF](https://arxiv.org/pdf/2502.06471)
- Metriq platform (2026), per search summary: defines an effective approximation ratio in which 0 corresponds to random sampling and 1 to perfectly sampling optimal bitstrings, and checks that results significantly exceed the random baseline (secondary summary; paper not opened) — [arXiv:2603.08680](https://arxiv.org/pdf/2603.08680)
- Dolzhkov, Fuchs, Theis (April 2026): "a per-shot statistical framework, which tracks the quality of QAOA outputs"; instances built from well-known generators, avoiding "synthetic constructions tailored to either quantum or classical algorithms"; QAOA treated as a black box under default settings; results "highlight its current limitations" versus Goemans-Williamson — [arXiv:2604.08367](https://arxiv.org/abs/2604.08367)
- Scriva et al. (2024) measure "the scaling of the quantum resources, defined as the required number of circuit repetitions" to reach a fixed success probability — i.e. a time-to-solution-style metric counted in shots — [arXiv:2308.00044](https://arxiv.org/abs/2308.00044)
- Zhou et al. and Sack & Serbyn both treat the number of random initialisations as a cost that must be counted (2^{O(p)} runs for random initialisation) — [arXiv:1812.01041](https://arxiv.org/abs/1812.01041); [arXiv:2101.05742](https://arxiv.org/abs/2101.05742)
- IBM's own tutorial validates its small instance against brute-force enumeration — [IBM tutorial: QAOA](https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-optimization-algorithm)
- dwave-samplers ships a `RandomSampler` (uniform random samples) and `SimulatedAnnealingSampler`, usable as the random and heuristic baselines on the same QUBO — [PyPI JSON dwave-samplers](https://pypi.org/pypi/dwave-samplers/json)

### Inferences
Recommended evaluation protocol for Q-Rescue (synthesised from the sources above; not a quoted standard):
- Inputs: one fixed set of instances (e.g. 10–20 seeded 3x4 instances plus a few 2x3), generated before any tuning; every method receives the identical objective, constraints and penalty-free definition of feasibility.
- Ground truth: brute-force enumeration of all 2^n bitstrings on the original constrained problem; record the optimum value, number of optimal solutions and number of feasible solutions.
- Repetitions: at least 20–30 independent QAOA runs per (instance, p, configuration) with distinct seeds; report median and IQR (not mean +/- std, since distributions are skewed and bounded), and show every run as a point in a strip/box plot.
- Metrics per run: per-shot probability of the optimum (success probability p_s); feasibility rate; approximation ratio computed on feasible samples only, r = (f_worst_feasible − f) / (f_worst_feasible − f_opt) for minimisation, stated explicitly because several definitions exist; optimality gap of the best feasible sample; expectation value of the original objective conditional on feasibility; number of circuit evaluations and wall-clock time.
- Time-to-solution in shots: TTS_99 = ln(1 − 0.99) / ln(1 − p_s) shots per attempt-chain, multiplied by cost per shot, and it must also charge the optimisation-loop evaluations and all restarts, not just final sampling.
- Baselines at equal budget: (i) uniform random bitstrings with the same N; (ii) uniform random feasible assignments; (iii) greedy nearest-ambulance; (iv) `linear_sum_assignment` on the linear part; (v) simulated annealing on the same QUBO with a disclosed sweep budget; (vi) exact solver. Report an effective ratio normalised so random = 0 and optimal = 1.
- Disclosure: state the tuning budget for every method (QAOA: optimizer, maxiter, restarts, p sweep, penalty sweep; SA: sweeps, reads, schedule), which instances were used for tuning, and all seeds and package versions.
- Scope the claim: "on these N simulated instances of size n, with this formulation", never "QAOA does X".

### Gaps
- The TAQOS protocol paper (ICCS 2023, DOI 10.1007/978-3-031-36030-5_13) could not be read: the PDF came back as an undecodable byte stream, so its title, authors and content are unverified and it should not be cited without checking.
- Metriq (arXiv:2603.08680) and the 2026 hardware benchmark were seen only through search summaries.
- The classic time-to-solution reference (Rønnow et al., "Defining and detecting quantum speedup", 2014) was not fetched; it predates the requested 2019–2026 window.
- I found no source prescribing a specific number of repetitions/seeds; 20–30 is a statistical-practice recommendation, not a citation.
- The full text of Abbas et al. (its benchmarking section) was not read; only the abstract is quoted.

## 8. Classical baselines available in Python today

### Takeaway
Brute-force enumeration is the correct exact solver here (at most about a million states) and handles the quadratic objective directly; `scipy.optimize.linear_sum_assignment` solves only the linear part; simulated annealing should come from dwave-samplers because dwave-neal is deprecated.

### Cited Findings
- SciPy docs are at v1.18.0; `scipy.optimize.linear_sum_assignment(cost_matrix, maximize=False)` — "Solve the linear sum assignment problem"; it "can also solve a generalization of the classic assignment problem where the cost matrix is rectangular"; implementation is "a modified Jonker-Volgenant algorithm with no initialization" (Crouse 2016) — [SciPy linear_sum_assignment](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html)
- OR-Tools latest PyPI release is 9.15.6755 (14 January 2026), Python >= 3.9, classifiers 3.9–3.14 — [PyPI ortools](https://pypi.org/project/ortools/)
- CP-SAT "works over the integers" and "you must define your optimization problem using integers only"; non-integer terms must be scaled by "a sufficiently large integer" (page last updated 2024-08-28) — [OR-Tools CP-SAT solver guide](https://developers.google.com/optimization/cp/cp_solver)
- PuLP latest is 4.0.0 (25 September 2026), Python >= 3.12; it is "a linear and mixed integer programming modeler"; "CBC is not shipped inside the PuLP package" any more — install `pulp[cbc]` or provide a CBC executable — [PyPI PuLP](https://pypi.org/project/PuLP/)
- dwave-samplers latest is 1.8.0, Python >= 3.10; includes `SimulatedAnnealingSampler`, `RandomSampler`, `SteepestDescentSolver`, `TabuSampler`, `TreeDecompositionSolver`, `PlanarGraphSolver`, and path-integral / rotor simulated-quantum-annealing samplers — [PyPI JSON dwave-samplers](https://pypi.org/pypi/dwave-samplers/json)
- dwave-neal (latest 0.6.0): "dwave-neal is deprecated in favor of dwave-samplers" — [PyPI JSON dwave-neal](https://pypi.org/pypi/dwave-neal/json)
- qiskit-optimization ships `CplexOptimizer`, `GurobiOptimizer`, `ScipyMilpOptimizer` and `NumPyMinimumEigensolver`; the `cplex` extra installs only on Python < 3.13 (< 3.12 on macOS) — [qiskit-optimization API index](https://qiskit-community.github.io/qiskit-optimization/apidocs/qiskit_optimization.html); [PyPI JSON qiskit-optimization](https://pypi.org/pypi/qiskit-optimization/json)
- qiskit-addon-opt-mapper ships `CplexSolver`, `GurobiSolver`, `ScipyMilpSolver` and a how-to "Validate your modeling with classical solvers" — [qiskit-addon-opt-mapper docs](https://qiskit.github.io/qiskit-addon-opt-mapper/)

### Inferences
- Exact solver with a quadratic binary objective, in order of practicality for this project: (1) brute-force enumeration in NumPy (direct, zero dependencies, also yields the full feasible-set statistics needed for approximation ratios); (2) `MinimumEigenOptimizer(NumPyMinimumEigensolver())`, which diagonalises the 2^n Ising Hamiltonian and so is exact but equally exponential; (3) a MIQP solver (Gurobi/CPLEX via the qiskit-optimization or opt-mapper wrappers), which adds a licence/installation risk for no benefit at this size; (4) CP-SAT or a MILP solver (CBC/HiGHS via PuLP or `ScipyMilp*`) after linearising each product x_i x_j with an auxiliary binary variable and three linear constraints — a standard reformulation but extra work and integer scaling for CP-SAT.
- `linear_sum_assignment` is exact only when the quadratic future-coverage weight is zero; it is useful as (a) a sanity check at lambda = 0 where QAOA/brute force must match it, and (b) a "myopic dispatch" baseline that quantifies what the quadratic term buys. It natively handles the rectangular 3x4 case (one call left unserved).
- PuLP 4.0.0's Python >= 3.12 requirement and unbundled CBC are a fresh breaking change; if PuLP is used at all, pin it. For this project PuLP is unnecessary.
- `NumPyMinimumEigensolver` on 16+ qubits builds a large matrix/diagonal; brute force over bitstrings is the lighter exact check.

### Gaps
- I did not confirm from current Gurobi or CPLEX documentation that they accept a non-convex quadratic binary objective directly, nor the current size limits of their free/pip licences; this was not fetched.
- The CP-SAT page read does not state whether the objective must be linear nor describe multiplication constraints; the linearisation advice is standard practice, not sourced from current OR-Tools docs.
- Upload dates for dwave-samplers 1.8.0 and dwave-neal 0.6.0 were not retrievable (PyPI HTML pages failed to load; JSON was truncated).
- `ScipyMilpOptimizer`'s handling of quadratic objectives was not checked (MILP implies linear only).

## 9. Limits and honesty: what a small simulated QAOA experiment can show

### Takeaway
A 12–16 qubit simulated QAOA study demonstrates a correct formulation and an honest characterisation of a heuristic; it provides no evidence of quantum advantage. Peer-reviewed sources place any plausible QAOA speed-up at hundreds of qubits, and classical simulation cost doubles with every added qubit.

### Cited Findings
- Guerreschi & Matsuura, Sci Rep 9, 6903 (2019), title "QAOA for Max-Cut requires hundreds of qubits for quantum speed-up": a speed-up over classical solvers is not expected until "several hundreds of qubits are available" — [arXiv:1812.07589](https://arxiv.org/abs/1812.07589)
- Koch et al. (2026): benchmark problem classes become challenging for established classical methods at system sizes "ranging from less than 100" variables upward — far above this project's 8–20 — [arXiv:2504.03832](https://arxiv.org/abs/2504.03832)
- Scriva et al. (2024): with realistic shot noise, variational optimisation with energy-based optimizers scales comparably "to direct brute-force search" — [arXiv:2308.00044](https://arxiv.org/abs/2308.00044)
- Dolzhkov, Fuchs, Theis (2026): per-shot comparison of QAOA with Goemans-Williamson results "highlight its current limitations" — [arXiv:2604.08367](https://arxiv.org/abs/2604.08367)
- Sack & Serbyn (2021): random initialisation "is prone to converging to local minima with sub-optimal performance" — [arXiv:2101.05742](https://arxiv.org/abs/2101.05742)
- Aer docs: a statevector stores 2^n complex values at 16 bytes each (memory doubles per qubit) — [Aer AerSimulator docs](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.AerSimulator.html)
- The IBM QAOA tutorial makes no quantum-advantage claim and does not compare its 100-qubit result to a classical baseline; it checks the small case by brute force — [IBM tutorial: QAOA](https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-optimization-algorithm)
- Abbas et al. (2024) frame the field's open question as where quantum advantage is possible at all and call for clear metrics for comparison with classical techniques — [arXiv:2312.02279](https://arxiv.org/abs/2312.02279)

### Inferences
- Statements the team can defend: the dispatch problem was formulated correctly as a QUBO and verified against exhaustive search; QAOA at depth p on a noiseless simulator samples the optimum with probability X (median over seeds) versus Y for uniform random sampling; feasibility rate was Z; the classical exact solver is instantaneous at this size and is what a real dispatcher would use.
- Statements the team must not make: any speed-up, any "quantum advantage", any claim about real hardware (no noise was modelled), any claim about scaling to city-sized instances (the simulator cost is exponential and the trend from three sizes is not a scaling law).
- The honest framing for a hackathon is "a validated quantum-ready formulation with a transparent benchmark harness", in which a negative or neutral QAOA result is a legitimate finding.
- Because 2^12 = 4,096 states are enumerable in well under a second classically while each QAOA run needs hundreds of circuit simulations, the simulated QAOA will be slower than brute force at every size in scope; say so in the results.

### Gaps
- I did not locate a single official IBM documentation sentence stating outright that small simulated QAOA shows no advantage; the IBM evidence is the absence of such a claim in the tutorial.
- Stilck França & García-Patrón (Nature Physics 2021, limits of optimisation on noisy devices) was not fetched and is not cited.

## 10. Streamlit: current version and caching long-running QAOA runs

### Takeaway
Streamlit 1.65.0 (2 October 2026, Python >= 3.10) reruns the whole script on every interaction, so QAOA must never run in the main script body; load precomputed results from disk and wrap loaders in `st.cache_data`.

### Cited Findings
- streamlit latest is 1.65.0, uploaded 2026-10-02; `requires_python >=3.10`; classifiers Python 3.10–3.14 — [PyPI JSON streamlit 1.65.0](https://pypi.org/pypi/streamlit/1.65.0/json)
- "Streamlit runs your script from top to bottom at every user interaction or code change."; "Long-running functions run again and again, which slows down your app." — [Streamlit caching docs](https://docs.streamlit.io/develop/concepts/architecture/caching)
- `st.cache_data` "is the recommended way to cache computations that return data"; it "creates a new copy of the data at each function call" — [Streamlit caching docs](https://docs.streamlit.io/develop/concepts/architecture/caching)
- `st.cache_resource` is the "recommended way to cache global resources like ML models or database connections"; it "does not create a copy of the cached return value" and "the return value must be thread-safe" — [Streamlit caching docs](https://docs.streamlit.io/develop/concepts/architecture/caching)
- `ttl` "sets a time to live on a cached function"; `max_entries` "sets the maximum number of entries in the cache"; parameters prefixed with an underscore are excluded from hashing, and `hash_funcs` handles unhashable inputs; a spinner is shown by default while a cached function runs (`show_spinner`) — [Streamlit caching docs](https://docs.streamlit.io/develop/concepts/architecture/caching)
- "`st.cache_data` implicitly uses the `pickle` module, which is known to be insecure." — [Streamlit caching docs](https://docs.streamlit.io/develop/concepts/architecture/caching)
- "In Streamlit 1.62.0, `st.cache` was removed." — [Streamlit caching docs](https://docs.streamlit.io/develop/concepts/architecture/caching)

### Inferences
- Architecture: an offline experiment script writes results (per-run parameters, counts, metrics, seeds, package versions) to JSON/Parquet; the dashboard only reads these files through an `@st.cache_data` loader. The demo then cannot fail or stall on a live optimisation, and what is shown is exactly what was benchmarked.
- If a "run live" button is offered, restrict it to the smallest instance at p = 1, key the cache on a hashable instance description (tuples or a frozen dataclass, not NumPy arrays or QuantumCircuit objects), and prefix unhashable arguments (circuits, samplers) with an underscore. Heavy simulator objects belong in `st.cache_resource`.
- In-memory caches are lost when the server restarts, so on-disk precomputed results are the reliable path for demo day.
- Old Streamlit snippets using `@st.cache` or `st.experimental_memo` will fail on 1.65.0.

### Gaps
- The `persist="disk"` option of `st.cache_data` is not mentioned on the concept page read; its current status was not verified on the API page.
- Streamlit fragment / background-execution features for long tasks were not checked.

## 11. Scope realism for four beginners: low-risk parts and typical sticking points

### Takeaway
Modelling, brute force, classical baselines, the dashboard and a penalty-based p = 1–3 statevector QAOA are low-risk; the documented traps are version mismatch from outdated tutorials, bit ordering, penalty scaling, random-initialisation stagnation and running simulations inside Streamlit reruns. Constraint-preserving mixers and noise models are stretch goals.

### Cited Findings
- Bit ordering: "By default, Qiskit follows the little-endian bit ordering convention."; in a displayed bitstring "bit n-1 is the leftmost bit, and bit 0 is the rightmost bit"; the guide also notes `BitArray` defaults to big-endian so primitive output handling varies — [IBM guide: bit ordering](https://quantum.cloud.ibm.com/docs/en/guides/bit-ordering)
- The IBM QAOA tutorial explicitly calls `.reverse()` on the decoded bit list and labels its plot axis "Bitstrings (reversed)" — [IBM tutorial: QAOA](https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-optimization-algorithm)
- Ordering bugs have occurred inside the library itself: 0.2.0 fixed bit ordering and probabilities in `MinimumEigenOptimizer` with the qasm simulator; 0.6.0 fixed slack-variable ordering in `InequalityToEquality`; 0.7.0 fixed `MagicRounding.round()` returning decision variables in the wrong order — [qiskit-optimization release notes](https://qiskit-community.github.io/qiskit-optimization/release_notes.html)
- API churn: import paths for QAOA, optimizers and `algorithm_globals` changed in qiskit-optimization 0.7.0; V1 primitives are deprecated there; `QuantumInstance`/Opflow were removed in 0.6.0 — [qiskit-optimization release notes](https://qiskit-community.github.io/qiskit-optimization/release_notes.html)
- V2 primitives require attention to pass managers / transpilation; QAOA in qiskit-optimization takes a `pass_manager` argument — [qiskit-optimization release notes](https://qiskit-community.github.io/qiskit-optimization/release_notes.html); [QAOA API](https://qiskit-community.github.io/qiskit-optimization/stubs/qiskit_optimization.minimum_eigensolvers.QAOA.html)
- In the low-level route the observable must be mapped with `hamiltonian.apply_layout(ansatz.layout)` after transpilation — [IBM tutorial: QAOA](https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-optimization-algorithm)
- Penalty scaling: the automatic penalty falls back to 1e5 with a warning that "The value could be too small. If so, set the penalty coefficient manually." when constraint coefficients are non-integer — [linear_equality_to_penalty.py source](https://raw.githubusercontent.com/qiskit-community/qiskit-optimization/main/qiskit_optimization/converters/linear_equality_to_penalty.py)
- Optimizer stagnation: random initialisation "is prone to converging to local minima with sub-optimal performance" — [arXiv:2101.05742](https://arxiv.org/abs/2101.05742); IBM's diagnostic is that a noisy, non-monotonic cost curve suggests too few shots or poor initial parameters — [IBM tutorial: QAOA](https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-optimization-algorithm)
- Nested (non-flattened) ansatz circuits add parameter-binding overhead; `flatten=True` is strongly recommended outside visualisation — [QAOAAnsatz API](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.QAOAAnsatz)
- Streamlit reruns the full script on every interaction — [Streamlit caching docs](https://docs.streamlit.io/develop/concepts/architecture/caching)
- qiskit-optimization is archived and unsupported, so bugs found during the hackathon will not be fixed upstream — [GitHub qiskit-community/qiskit-optimization](https://github.com/qiskit-community/qiskit-optimization)

### Inferences
Low-risk (standard, well documented):
- Instance generator and data model; brute-force exact solver; `linear_sum_assignment` and greedy baselines; simulated annealing via dwave-samplers; QUBO construction with pairwise penalties; p = 1–3 QAOA on exact statevector with COBYLA; a Streamlit dashboard reading precomputed files.

Medium risk (budget time, add tests):
- QUBO -> Ising conversion done by hand (signs, the x = (1 − z)/2 substitution, constant offset). Mitigation: unit test that the Ising energy plus offset equals the QUBO value for every bitstring of a 4–6 variable instance, and cross-check against `QuadraticProgram.to_ising()`.
- Bit ordering in decoding. Mitigation: a one-qubit-set test (prepare a known basis state, assert the decoded variable assignment), and a single shared decode function used by every method.
- Penalty choice. Mitigation: brute-force check that the QUBO minimiser is feasible and optimal for the original problem; sweep 2–3 penalty values.
- Version drift from copied tutorials. Mitigation: a pinned requirements file created on day one from the versions in section 1, plus a rule that code is only copied from docs showing those versions.

High risk / stretch only:
- XY or ring mixers with custom initial states for two overlapping constraint families; noise-model studies; 20+ qubit instances with slack; warm-start or recursive QAOA; any live QAOA in the dashboard.

Suggested division of labour for four students: (1) modelling + brute force + classical baselines; (2) QUBO/Ising + QAOA runner + unit tests; (3) experiment harness, seeds, statistics and plots; (4) Streamlit dashboard + results file schema + write-up. The benchmark harness should exist before QAOA tuning starts so tuning cannot leak into evaluation.

### Gaps
- No official "common beginner mistakes with QAOA" troubleshooting page was found; the risk ranking above is my synthesis from the cited docs, release-note bug fixes and literature.
- The Qiskit Slack / Stack Exchange and the (archived) issue tracker were not surveyed for frequency of these problems.
- The bit-ordering guide page read does not cover `SparsePauliOp` label ordering or `from_sparse_list` indexing; these should be checked on the `SparsePauliOp` API page before the team relies on a label-string construction (index-based `from_sparse_list`, as in the IBM tutorial, avoids label-order ambiguity).
