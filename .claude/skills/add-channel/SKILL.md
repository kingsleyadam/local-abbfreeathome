---
name: add-channel
description: Add or extend support for a Free@Home channel (function ID) in local-abbfreeathome, covering physical and virtual channels, mapping extra function IDs to existing classes, subclassing, enums, tests, and documentation. Use when asked to support a new device, channel, function ID, or datapoint, or to implement a channel feature request.
---

# Adding channel support

Read `.github/instructions/channels.instructions.md` and
`.github/instructions/tests.instructions.md` first; this skill applies them.

## 1. Gather evidence

Work from real channel data, never invented pairings or values. You need:

- The `functionID` (hex string), and whether the device is physical or virtual
  (virtual serials start with `6000`; interface `VIRTUAL_DEVICE`).
- The channel's `inputs`, `outputs`, and `parameters` with `pairingID`s and
  sample values, typically from the issue, Home Assistant diagnostics, or
  `FreeAtHomeApi.get_configuration()`.
- What each value means. Check ABB's SDK
  ([pairingIds.ts](https://github.com/Busch-Jaeger/node-free-at-home/blob/master/src/pairingIds.ts),
  [functionIds.ts](https://github.com/Busch-Jaeger/node-free-at-home/blob/master/src/functionIds.ts),
  [parameterIds.ts](https://github.com/Busch-Jaeger/node-free-at-home/blob/master/src/parameterIds.ts))
  and the [Local API docs](https://developer.eu.mybuildings.abb.com/fah_local).

If the data is missing or the meaning of a value is ambiguous, stop and ask the
user rather than guessing; cite the source of any value mapping in the class
docstring (see `HeatingCoolingSensorState` in `channels/heating_cooling_sensor.py`).

## 2. Choose the approach

Pick the smallest change that models the behavior correctly:

| Situation | Approach | Example |
| --- | --- | --- |
| Behaves exactly like an existing class | Map the function ID to that class in `const.py` | `FID_BLINDS_ACTUATOR_TYPE*` |
| Existing class with different pairings or extra features | Subclass and override pairings or handlers | `MWireSwitchActuator`, `StaircaseLightSensor` (#249) |
| New kind of channel | New module in `channels/` | `HeatingCoolingSensor` (#278) |
| Virtual device channel | New module in `channels/virtual/` | `VirtualDimmingActuator` (#268) |

Consumers filter channels by exact type, so a new subclass or class is a
visible change for them (for example the Home Assistant integration). Confirm
the approach with the user when the choice is not obvious.

## 3. Enums

Use `Function`, `Pairing`, and `Parameter` from `bin/`. If an ID is missing,
add it with the name and value from ABB's SDK file cited in that module's
docstring.

If ABB documents no name, first confirm the ID appears in the user's
configuration. Then make up a name, using the same `PYCUSTOM` suffix as
`FID_SWITCH_ACTUATOR_PYCUSTOM0` (#237) so it is clearly not an official ABB name
(for example `AL_<DESCRIPTION>_PYCUSTOM0`). Add it at the end of the enum,
below the "custom to this python package" comment, creating that comment if the
enum lacks one. Note in the PR where the ID was observed.

## 4. Implement the class

Use the closest existing class as a template: `heating_cooling_sensor.py` for a
read-only sensor, `switch_actuator.py` for commands, and
`virtual/virtual_switch_actuator.py` for a virtual channel. Then:

- Use the standard `__init__` signature, set every state field before
  `super().__init__()`, and model multi-valued states as an `enum.Enum` with
  `unknown = None`, exposing `.name` from the property.
- Declare `_callback_attributes`, `_state_refresh_pairings`,
  `_input_refresh_pairings`, and `_handle_input_updates` as described in the
  channel instructions.
- In `_refresh_state_from_datapoint()`, match on `pairingID`, update state, and
  return the affected attribute names, or `[]` for unhandled pairings. Treat
  missing values as unknown (log at debug) and invalid values as unknown (log a
  warning naming the channel).
- Commands look up datapoint IDs with `get_input_by_pairing()` (physical) or
  `get_output_by_pairing()` (virtual feedback), call
  `self.device.api.set_datapoint(...)`, then update local state as the existing
  classes do.
- If you override `update_channel()` or `update_scene()`, pass `is_priming`
  through.
- Write docstrings for the module, classes, and public methods (Ruff enforces them).

## 5. Register the function ID

Add the import and mapping entry in `const.py`, in
`FUNCTION_CHANNEL_MAPPING` (physical) or `FUNCTION_VIRTUAL_CHANNEL_MAPPING`
(virtual). Place the entry next to related function IDs, otherwise
alphabetically.

## 6. Tests

Add `tests/test_<module>.py` (or extend the existing file for a subclass or
mapping change). Build the fixture from the evidence in step 1 through
`Device(...).load_channels(mock_floorplan)` so discovery is tested; for
virtual channels use a `6000...` serial and `interface=Interface.VIRTUAL_DEVICE`.
Cover:

- Discovery: the function ID creates the exact class (`type(channel) is ...`).
- Initial state for each meaningful value, plus missing datapoints.
- `refresh_state()`: `get_datapoint` is awaited with the expected datapoint IDs.
- Updates via `update_channel()`: state changes and callbacks fire once;
  unrelated pairings are ignored without callbacks.
- Invalid and missing values become unknown with the expected log.
- Each command: `set_datapoint` is awaited with the expected datapoint and
  value, and local state updates.
- Any overridden priming or scene behavior.

Coverage must stay at 100%:

```sh
python -m pytest --cov=. --cov-branch --cov-report=term-missing
ruff check . && ruff format --check .
```

## 7. Documentation

- `README.md` "Channel Implementation" table: add or update the row (physical
  rows alphabetically, virtual rows under **Virtual Devices**) with its commands
  and properties, including the meaning of non-obvious state values.
- Virtual channels: update the matching rows and the implemented-class count in
  `docs/virtual-devices.md`.

## 8. Open the PR

Use the `open-pr` skill with a `feat/<topic>-<issue>` branch, labeled
`Semver-Minor` and `enhancement` (or `Semver-Patch` and `bug` if this fixes a
wrong mapping). Link the issue, and note any follow-up needed in the Home
Assistant integration (`kingsleyadam/local-abbfreeathome-hass`) under Follow-up.
