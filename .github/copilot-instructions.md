# Repository instructions

## Build, test, and lint

This is the `local-abbfreeathome` Python package, imported as `abbfreeathome`.
Python 3.12+ is required; CI and the VS Code Dev Container use Python 3.12.
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

## Channel and event conventions

- Function IDs arrive as hexadecimal strings and are decoded with `Function`.
  Register new channel support in `FUNCTION_CHANNEL_MAPPING` or
  `FUNCTION_VIRTUAL_CHANNEL_MAPPING` in `const.py`; use the enums in `bin/` for
  function, interface, pairing, and parameter IDs. Multiple function IDs may
  share a class when their behavior is identical. The README's older reference
  to `FreeAtHome._get_function_to_channel_mapping` is superseded by these mappings.
- Datapoint dictionaries use `idp...`/`odp...` keys, integer `pairingID` values,
  and usually string wire values such as `"0"`/`"1"`. Resolve datapoint IDs with
  `get_input_by_pairing()` / `get_output_by_pairing()` rather than hardcoding
  indexes. Physical actuator commands generally write inputs; virtual actuator
  feedback writes outputs.
- Initialize subclass state fields before `super().__init__()`: `Base` invokes
  overridden refresh handlers during construction. Declare REST refresh pairings
  in `_state_refresh_pairings` and subscribable properties in `_callback_attributes`.
  `_refresh_state_from_datapoint()` updates state and returns affected attribute
  names, or `[]` when unhandled. Callbacks are synchronous, zero-argument
  functions; `_notify_callbacks()` deduplicates a subscriber across attributes.
- Preserve repeated event delivery outside priming, even for identical values.
  The post-WebSocket-(re)connect priming window updates cached datapoints but
  suppresses callbacks for unchanged values, while still notifying real changes.
  Propagate `is_priming` through overridden update handlers.
- `FreeAtHome.update()` applies parameters before datapoints so interpreters
  such as sensor LED-mode handling see current configuration. Parameter IDs use
  `par0002` form; shared lookup accepts string, integer, or `Parameter` enum IDs.
  Parameter callbacks fire only on value changes.
- `scenesTriggered` contains nested device/channel outputs, merged with ordinary
  datapoints and dispatched through `update_scene()`. Virtual switch/dimmer
  `requested_*` properties represent commands independently of reported state.
  Ordinary output feedback must not emit request callbacks; virtual-switch scene
  commands must emit request callbacks even when unchanged or during priming.

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

For documentation-only PRs, `documentation` is the only required label; no
version-impact label is required.

For all other PRs, also apply exactly one version-impact label:

- `Semver-Major`: breaking changes; also add `breaking-change`.
- `Semver-Minor`: backward-compatible features; also add `enhancement`.
- `Semver-Patch`: bug fixes or backward-compatible refactors; add `bug` for fixes.

Use additional labels such as `documentation` or `question` when applicable.
If the version impact is unclear, ask before creating the PR rather than guessing.
PR labels categorize generated release notes via `.github/release.yml` and inform
the required version bump. Keep labels consistent with the actual change, updating
them if the PR scope changes.

## Tests and releases

Tests import `src.abbfreeathome.*`; `pyproject.toml` puts the repository root on
pytest's import path. Async tests use `@pytest.mark.asyncio` and async fixtures use
`pytest_asyncio.fixture`. Channel tests construct realistic input/output mappings
with `AsyncMock(spec=FreeAtHomeApi)` and a mock `Device`; transport tests use
`aioresponses` and patched WebSockets. Shared fixtures are in `tests/conftest.py`,
including an aiohttp/aioresponses compatibility patch. `pytest-env` sets
`FREEATHOME_MAX_REQUEST_TRIES=1` to avoid retry delays in tests.

The package version is in `pyproject.toml`. Tag pushes publish to PyPI and create
a GitHub release; TestPyPI publishing is manually dispatched. Optional release
highlights belong in `.github/release-notes/<exact-tag>.md` and must be merged
before pushing the tag, as documented in `.github/release-notes/README.md`.
