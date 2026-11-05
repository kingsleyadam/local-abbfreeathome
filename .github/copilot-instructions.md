# Repository instructions

## Build, test, and lint

This is the `local-abbfreeathome` Python package, imported as `abbfreeathome`.
Python 3.12+ is required; CI tests Python 3.12, 3.13, and 3.14, and the VS Code
Dev Container uses Python 3.12.
Use `uv` to manage the virtual environment; it is the Dev Container default.
Run commands from the repository root with the virtual environment active.

```sh
uv venv
source .venv/bin/activate
uv pip install -r src/abbfreeathome/dev-requirements.txt
uv pip install -e .
pre-commit install

python -m build
python -m pytest tests
python -m pytest tests/test_switch_actuator.py
python -m pytest tests/test_switch_actuator.py::test_turn_on
python -m pytest --cov=. --cov-branch --cov-report=xml:coverage/coverage.xml --junitxml=junit/test-results.xml
ruff check .
ruff format --check .
```

Packaging uses Hatchling and includes `src/abbfreeathome` in the wheel.
The Dev Container's `postCreateCommand` already runs `uv venv`, installs the
development requirements, and runs `pre-commit install`.
Pre-commit runs Ruff with `--fix` and the Ruff formatter. Ruff configuration lives
in `pyproject.toml`, including docstring checks, import sorting, and bans on
`async_timeout` and `pytz` in favor of `asyncio.timeout` and `zoneinfo`.
CI's coverage-summary gate requires 100% line and branch coverage; every change
must keep it there by adding tests for new or changed code. Only when a path is
genuinely untestable (for example, version-dependent imports) may it be excluded
with a `# pragma: no cover` comment, ideally with a short reason after it.

## Architecture

This is an independent asynchronous library for the ABB/Busch-Jaeger Free@Home
SysAP **Local API**, designed for use by Home Assistant without depending on it.
The Local API must be enabled on the SysAP; protocol reference:
<https://developer.eu.mybuildings.abb.com/fah_local>.

- `api.py`: `FreeAtHomeSettings` reads `/settings.json`; `FreeAtHomeApi` owns REST
  transport, authentication, TLS, retries, virtual-device creation, and WebSocket
  connections. REST paths are prefixed with `/fhapi/v1`; responses are unwrapped
  by SysAP UUID. Transport failures map to exceptions in `exceptions.py`.
  An injected `aiohttp.ClientSession` belongs to the caller; internally created
  sessions are closed by the API's async context manager.
- `freeathome.py`: `FreeAtHome.load()` fetches cached configuration and builds
  `Floorplan` -> `Device` -> channel objects. `Device.load_channels()` selects
  classes from the physical or virtual mappings in `const.py`. `get_channels()`
  caches a filtered view keyed by `<device_serial>/<channel_id>`; device/channel
  changes must keep this cache consistent. Channels with neither floor nor room
  are excluded unless `include_orphan_channels=True`; class filters use exact
  types, not subclass matching. Serials starting with `6000` are treated as virtual.
- `channels/base.py`: channels hold a parent `Device` and access transport through
  `self.device.api`. Constructors initialize state from configuration datapoints
  without making requests. Channel methods issue commands; `refresh_state()`
  provides explicit REST refreshes. Normal ongoing updates arrive through
  `FreeAtHome.ws_listen()` -> `FreeAtHome.update()` -> channel update handlers.
- `parameters.py`: `ParametersMixin` provides shared device/channel parameter
  lookup and change callbacks. Floor and room names are resolved by `Floorplan`,
  with channel locations falling back to device locations.

## Path-specific instructions

Detailed conventions live in `.github/instructions/*.instructions.md`, scoped by
their `applyTo` globs. Read the matching file before changing code in its scope
if it is not already loaded.

- `channels.instructions.md` (`src/abbfreeathome/**/*.py`, `tests/**/*.py`):
  channel, datapoint, event, and parameter conventions.
- `tests.instructions.md` (`tests/**`): test structure, fixtures, and mocking patterns.

## Pull request scope

Keep PRs small and easy to review: each PR should address one focused bug,
feature, or refactor, with only the tests and documentation needed for that change.
Do not bundle unrelated fixes, cleanup, dependency upgrades, renames, or formatting
changes. Format touched code without reformatting unrelated files.

For larger work, propose a split into independently reviewable, working PRs before
implementing the full change. Separate preparatory refactors from behavior changes
when each can stand on its own; keep tightly coupled changes together rather than
leaving broken intermediate states. If the scope grows beyond the original task,
pause and agree on the split instead of silently expanding the PR.

Before opening a PR, inspect the complete diff and remove incidental changes.
Keep the description concise: state the purpose, behavioral changes, and validation,
and identify any follow-up work deliberately left for separate PRs.

## Issue and pull request labels

Every new issue and PR must have at least one relevant label. Inspect existing
repository labels and apply them when creating the issue or PR; do not leave
labeling as a follow-up task or invent new labels without agreement.

For documentation-only PRs, `documentation` is the only required label. For
chore PRs, which change neither code nor documentation (for example CI, tooling,
the Dev Container, or repository configuration), `chore` is the only required
label. Neither needs a version-impact label.

For all other PRs, also apply exactly one version-impact label:

- `Semver-Major`: breaking changes; also add `breaking-change`.
- `Semver-Minor`: backward-compatible features; also add `enhancement`.
- `Semver-Patch`: bug fixes or backward-compatible refactors; add `bug` for fixes.

Use additional labels such as `documentation` or `question` when applicable.
If the version impact is unclear, ask before creating the PR rather than guessing.
PR labels categorize generated release notes via `.github/release.yml` and inform
the required version bump. Keep labels consistent with the actual change, updating
them if the PR scope changes.

## Releases

The package version is in `pyproject.toml`. Tag pushes publish to PyPI and create
a GitHub release; TestPyPI publishing is manually dispatched. Optional release
highlights belong in `.github/release-notes/<exact-tag>.md` and must be merged
before pushing the tag, as documented in `.github/release-notes/README.md`.
