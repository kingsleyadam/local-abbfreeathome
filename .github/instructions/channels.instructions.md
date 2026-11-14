---
applyTo: "src/abbfreeathome/**/*.py,tests/**/*.py"
---

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
  overridden refresh handlers during construction. Declare output refresh pairings
  in `_state_refresh_pairings` and subscribable properties in `_callback_attributes`.
  `refresh_state()` skips refresh pairings the channel does not have, so a class
  may list pairings that only some of its devices provide. Input pairings listed
  in `_input_refresh_pairings` are loaded at construction and fetched by
  `refresh_state()`, which caches the values it reads and notifies
  each refreshed attribute once. Declare refreshed attributes that report commands
  rather than state, such as sensor button presses, `requested_*` values, or a
  cover's `target_position`, in `_command_callback_attributes`; `refresh_state()`
  does not notify them, so a refresh does not look like a new command; they must
  also be listed in `_callback_attributes`. Optionally map callback attributes to
  the refresh pairings that feed them in `_attribute_refresh_pairings`, so that
  `refresh_state(attributes=...)` reads only those; unmapped attributes or an
  empty list refresh every pairing. Each entry must list exactly the refresh
  pairings whose `_refresh_state_from_datapoint()` result includes the
  attribute; `test_attribute_refresh_pairings_match_handlers` checks this for
  every mapped channel class. `update_channel()` handles output updates
  and handles input updates only when `_handle_input_updates` is `True`. Enable
  it for virtual channels and channels that expose `requested_*` values, because
  physical inputs can share pairing IDs with outputs.
  `_refresh_state_from_datapoint()` updates state and returns affected attribute
  names, or `[]` when unhandled. To reject an invalid value, it must raise
  before changing any state rather than return `[]`, so `update_channel()` and
  `refresh_state()` keep the previous cached value. Callbacks are synchronous,
  zero-argument functions; `_notify_callbacks()` deduplicates a subscriber across
  attributes.
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
