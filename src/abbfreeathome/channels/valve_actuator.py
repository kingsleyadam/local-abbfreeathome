"""Free@Home Valve Actuator Classes."""

from typing import TYPE_CHECKING, Any

from ..bin.pairing import Pairing
from .base import Base

if TYPE_CHECKING:
    from ..device import Device


class ValveActuatorMixin:
    """Mixin class for valve actuator position control."""

    async def _set_valve_position(
        self, value: int, attr_name: str, input_pairing: Pairing
    ):
        """
        Set a valve position with bounds checking.

        Args:
            value: The valve position to set (0-100)
            attr_name: The internal attribute name (e.g., "_position")
            input_pairing: The input pairing ID for setting the valve position

        """
        value = max(0, value)
        value = min(value, 100)

        await self._set_valve_datapoint(input_pairing, str(value))
        setattr(self, attr_name, value)

    def _refresh_valve_position_from_datapoint(
        self, datapoint: dict[str, Any], attr_name: str
    ) -> str:
        """
        Refresh valve position from a datapoint.

        Args:
            datapoint: The datapoint dictionary
            attr_name: The internal attribute name

        Returns:
            The attribute name that was refreshed

        """
        value = datapoint.get("value")
        setattr(self, attr_name, int(float(value)))
        return attr_name.lstrip("_")

    async def _set_valve_datapoint(self, input_pairing: Pairing, value: str):
        """Set a valve position datapoint on the API."""
        input_id, _input_value = self.get_input_by_pairing(pairing=input_pairing)
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=input_id,
            value=value,
        )


class HeatingActuator(ValveActuatorMixin, Base):
    """Free@Home HeatingActuator Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_INFO_VALUE_HEATING,
    ]
    _callback_attributes: list[str] = [
        "position",
    ]

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
        """Initialize the Free@Home HeatingActuator class."""
        self._position: int | None = None

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
    def position(self) -> int | None:
        """Get the position of the actuator."""
        return self._position

    async def set_position(self, value: int):
        """
        Set the position of the valve.

        The position has to be between 0 and 100
        Fully closed = 0
        Fully open = 100
        """
        await self._set_valve_position(
            value=value,
            attr_name="_position",
            input_pairing=Pairing.AL_ACTUATING_VALUE_HEATING,
        )

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the channel from a given output.

        This will return the name of the attribute, which was refreshed or None.
        """
        pairing_id = datapoint.get("pairingID")

        if pairing_id == Pairing.AL_INFO_VALUE_HEATING.value:
            return self._refresh_valve_position_from_datapoint(
                datapoint=datapoint,
                attr_name="_position",
            )
        return None


class CoolingActuator(ValveActuatorMixin, Base):
    """Free@Home CoolingActuator Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_INFO_VALUE_COOLING,
    ]
    _callback_attributes: list[str] = [
        "position",
    ]

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
        """Initialize the Free@Home CoolingActuator class."""
        self._position: int | None = None

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
    def position(self) -> int | None:
        """Get the position of the actuator."""
        return self._position

    async def set_position(self, value: int):
        """
        Set the position of the valve.

        The position has to be between 0 and 100
        Fully closed = 0
        Fully open = 100
        """
        await self._set_valve_position(
            value=value,
            attr_name="_position",
            input_pairing=Pairing.AL_ACTUATING_VALUE_COOLING,
        )

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the channel from a given output.

        This will return the name of the attribute, which was refreshed or None.
        """
        pairing_id = datapoint.get("pairingID")

        if pairing_id == Pairing.AL_INFO_VALUE_COOLING.value:
            return self._refresh_valve_position_from_datapoint(
                datapoint=datapoint,
                attr_name="_position",
            )
        return None


class HeatingCoolingActuator(ValveActuatorMixin, Base):
    """Free@Home HeatingCoolingActuator Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_INFO_VALUE_HEATING,
        Pairing.AL_INFO_VALUE_COOLING,
    ]
    _callback_attributes: list[str] = [
        "heating_position",
        "cooling_position",
    ]

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
        """Initialize the Free@Home HeatingCoolingActuator class."""
        self._heating_position: int | None = None
        self._cooling_position: int | None = None

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
    def heating_position(self) -> int | None:
        """Get the heating valve position (0-100%)."""
        return self._heating_position

    @property
    def cooling_position(self) -> int | None:
        """Get the cooling valve position (0-100%)."""
        return self._cooling_position

    async def set_heating_position(self, value: int):
        """
        Set the heating valve position.

        The position has to be between 0 and 100
        Fully closed = 0
        Fully open = 100
        """
        await self._set_valve_position(
            value=value,
            attr_name="_heating_position",
            input_pairing=Pairing.AL_ACTUATING_VALUE_HEATING,
        )

    async def set_cooling_position(self, value: int):
        """
        Set the cooling valve position.

        The position has to be between 0 and 100
        Fully closed = 0
        Fully open = 100
        """
        await self._set_valve_position(
            value=value,
            attr_name="_cooling_position",
            input_pairing=Pairing.AL_ACTUATING_VALUE_COOLING,
        )

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the channel from a given output.

        This will return the name of the attribute, which was refreshed or None.
        """
        pairing_id = datapoint.get("pairingID")

        if pairing_id == Pairing.AL_INFO_VALUE_HEATING.value:
            return self._refresh_valve_position_from_datapoint(
                datapoint=datapoint,
                attr_name="_heating_position",
            )

        if pairing_id == Pairing.AL_INFO_VALUE_COOLING.value:
            return self._refresh_valve_position_from_datapoint(
                datapoint=datapoint,
                attr_name="_cooling_position",
            )

        return None
