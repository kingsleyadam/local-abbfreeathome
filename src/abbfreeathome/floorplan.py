"""ABB-Free@Home FloorPlan class for managing floor and room data."""


class Floorplan:
    """Manages floor plan data for Free@Home devices and channels."""

    def __init__(self, floorplan_data: dict[str, dict] | None = None) -> None:
        """Initialize the FloorPlan class."""
        self._floors: dict[str, dict] = floorplan_data or {}

    @classmethod
    def from_config(cls, config: dict) -> "Floorplan":
        """Return FloorPlan class from configuration data."""
        _floorplan_data = config.get("floorplan", {}).get("floors", {})
        return cls(_floorplan_data)

    def get_floor_name(self, floor_id: str | None) -> str | None:
        """Get the floor name by floor ID."""
        if not floor_id:
            return None
        return self._floors.get(floor_id, {}).get("name")

    def get_room_name(self, floor_id: str | None, room_id: str | None) -> str | None:
        """Get the room name by floor ID and room ID."""
        if not floor_id or not room_id:
            return None

        _floor_data = self._floors.get(floor_id, {})
        _rooms = _floor_data.get("rooms", {})
        if _rooms is None:
            return None
        return _rooms.get(room_id, {}).get("name")

    def get_floors(self) -> dict[str, dict]:
        """Get all floors data."""
        return self._floors.copy()

    def has_floor(self, floor_id: str) -> bool:
        """Check if floor exists."""
        return floor_id in self._floors

    def has_room(self, floor_id: str, room_id: str) -> bool:
        """Check if room exists on the given floor."""
        if not self.has_floor(floor_id):
            return False
        _rooms = self._floors[floor_id].get("rooms", {})
        if _rooms is None:
            return False
        return room_id in _rooms

    def is_empty(self) -> bool:
        """Check if floor plan is empty."""
        return len(self._floors) == 0

    def __repr__(self) -> str:
        """Return a string representation of the floor plan."""
        _floor_count = len(self._floors)
        _room_count = 0

        for _floor in self._floors.values():
            _rooms = _floor.get("rooms", {})
            if _rooms is not None:
                _room_count += len(_rooms)

        return f"Floorplan(floors={_floor_count}, rooms={_room_count})"
