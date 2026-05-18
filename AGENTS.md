# Sol Naciente — AGENTS.md

## Run

- Entrypoint: `python src/solnaciente/gui/app.py` (run from repo root; `app.py` adds `src/` to `sys.path`)
- Simulation-only (no GUI): `python -c "from solnaciente.sims.monte_carlo import MonteCarloSimulator; ..."` (run from `src/`)

## Dependencies

No `requirements.txt` or `pyproject.toml`. Needed at runtime:
`PySide6`, `numpy`, `scipy`, `matplotlib`, `pandas`, `openpyxl`

## Architecture

- **Package boundary**: `src/solnaciente/` — import as `from solnaciente.xxx import yyy`
- **`gui/app.py`**: sys.path insertion + Qt dark theme + starts `MainWindow`
- **`gui/main_window.py`**: Orchestrates UI. Simulation runs in `QThread` via `SimulationWorker` to avoid freezing.
- **`gui/sidebar.py`**: User-facing parameter controls. Emits `start_requested(dict)` signal.
- **`sims/monte_carlo.py`**: `MonteCarloSimulator.__init__` accepts `days`, `fixed_fee`, `company_share`, plus distribution params (`poisson_lam`, `erlang_mean`, `erlang_var`, `geom_mean`, `rate_mean`, `rate_std`). `run()` aggregates over `n_runs`.
- **`models/investment.py`**: `Investment` dataclass with `daily_rates: List[float]` (one rate per day, NOT a single `daily_rate`). `growth_series()` applies a different rate each day.
- **`sims/distributions.py`**: Pure functions returning `np.ndarray` — `daily_new_investments_poisson`, `magnitude_erlang`, `duration_geometric`, `daily_rate_normal`.

## Business model quirk

The company only collects fees (`$100` fixed + `10%` of profit) and **never bears the investment principal**. This means `success_prob` (fraction of runs with positive company NPV) is always ~100% and risk is always "Bajo". This is **correct behavior** — to see variability, the model would need costs, defaults, or a client-perspective NPV.

## Conventions

- Spanish UI labels, report text, comments, and most identifiers
- `from __future__ import annotations` used broadly
- `float` / `int` / `List` typing throughout (pre-3.9 style with `typing`)
- `np.random.default_rng(seed)` pattern for reproducible RNG, not the legacy `np.random`
- No tests exist; no lint/typecheck config; no CI

## Sidebar params caveat

The sidebar collects distribution parameters but the signaling keys were historically unreliable. Currently working keys: `poisson_lambda`, `erlang_mean`, `erlang_var`, `geom_mean`, `rate_mean`, `rate_std`. If adding new UI controls, verify they reach `MonteCarloSimulator.__init__` via `workers.py`.

## Git

Only 2 commits. No branches, no CI, no release workflow.
