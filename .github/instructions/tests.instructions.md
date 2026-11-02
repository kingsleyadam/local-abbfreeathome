---
applyTo: "tests/**"
---

## Tests

Tests import `src.abbfreeathome.*`; `pyproject.toml` puts the repository root on
pytest's import path. Async tests use `@pytest.mark.asyncio` and async fixtures use
`pytest_asyncio.fixture`. Channel tests construct realistic input/output mappings
with `AsyncMock(spec=FreeAtHomeApi)` and a mock `Device`; transport tests use
`aioresponses` and patched WebSockets. Shared fixtures are in `tests/conftest.py`,
including an aiohttp/aioresponses compatibility patch. `pytest-env` sets
`FREEATHOME_MAX_REQUEST_TRIES=1` to avoid retry delays in tests.
