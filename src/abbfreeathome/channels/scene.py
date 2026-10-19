"""Observe free@home scene requests reported by the SysAP."""

from typing import TYPE_CHECKING, Any

from ..bin.pairing import Pairing
from .base import Base

if TYPE_CHECKING:
    from ..device import Device


class Scene(Base):
    """Represent a scene's notification channel, without controlling the scene."""

    _callback_attributes: list[str] = ["scene_control"]

    def __init__(
        self,
        device: "Device",
        channel_id: str,
        channel_name: str,
        inputs: dict[str, dict[str, Any]],
        outputs: dict[str, dict[str, Any]],
        parameters: dict[str, dict[str, Any]],
        floor_name: str | None = None,
        room_name: str | None = None,
    ) -> None:
        """Load scene metadata without emitting an initial request."""
        self._scene_control: str | None = None
        super().__init__(
            device,
            channel_id,
            channel_name,
            inputs,
            outputs,
            parameters,
            floor_name,
            room_name,
        )

    @property
    def scene_control(self) -> str | None:
        """Return the raw scene-control value, not the identity of the scene."""
        return self._scene_control

    def update_scene(
        self, datapoint_key: str, datapoint_value: str, is_priming: bool = False
    ) -> None:
        """Emit explicit scene requests even during WebSocket snapshot priming."""
        # Scene notifications are commands, not replayed snapshot values.
        self.update_channel(datapoint_key, datapoint_value)

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str | None:
        """Accept recall telegrams and ignore invalid or learning values."""
        if datapoint.get("pairingID") != Pairing.AL_SCENE_CONTROL.value:
            return None

        value = datapoint.get("value")
        if not isinstance(value, str):
            return None
        try:
            control = int(value)
        except ValueError:
            return None

        # AL_SCENE_CONTROL is one byte; bit 7 distinguishes learning from recall.
        if not 0 <= control < 128:
            return None

        # Scene identity comes from the device/channel, not this payload. Base
        # dispatches every live update, including repeated identical requests;
        # loading or refreshing cached values does not dispatch callbacks.
        self._scene_control = value
        return "scene_control"
