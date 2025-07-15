"""Test code for the Floorplan class."""

from src.abbfreeathome.floorplan import Floorplan


def test_floorplan_fixture_realistic_data(mock_floorplan):
    """Test that the floorplan fixture works correctly with realistic data."""
    # Test floor name lookup
    assert mock_floorplan.get_floor_name("01") == "Ground Floor"
    assert mock_floorplan.get_floor_name("02") == "1st Floor"
    assert mock_floorplan.get_floor_name("03") == "2nd Floor"
    assert mock_floorplan.get_floor_name("04") == "3rd Floor"
    assert mock_floorplan.get_floor_name("99") is None  # Non-existent floor

    # Test room name lookup
    assert mock_floorplan.get_room_name("01", "18") == "Living Room"
    assert mock_floorplan.get_room_name("01", "0C") == "Kitchen"
    assert mock_floorplan.get_room_name("02", "06") == "Living Room"
    assert mock_floorplan.get_room_name("03", "0D") == "Primary Bedroom"
    assert mock_floorplan.get_room_name("04", "1B") == "Laundry Room"
    assert mock_floorplan.get_room_name("01", "99") is None  # Non-existent room
    assert mock_floorplan.get_room_name("99", "01") is None  # Non-existent floor


def test_floorplan_empty_initialization():
    """Test Floorplan initialization with empty data."""
    floorplan = Floorplan()

    assert floorplan.get_floor_name("01") is None
    assert floorplan.get_room_name("01", "02") is None
    assert floorplan.get_floors() == {}


def test_floorplan_from_config():
    """Test creating Floorplan from configuration data."""
    config = {
        "floorplan": {
            "floors": {
                "01": {"name": "Test Floor", "rooms": {"01": {"name": "Test Room"}}}
            }
        }
    }

    floorplan = Floorplan.from_config(config)

    assert floorplan.get_floor_name("01") == "Test Floor"
    assert floorplan.get_room_name("01", "01") == "Test Room"


def test_floorplan_from_config_missing_data():
    """Test creating Floorplan from config with missing floorplan data."""
    config = {}

    floorplan = Floorplan.from_config(config)

    assert floorplan.get_floor_name("01") is None
    assert floorplan.get_room_name("01", "01") is None


def test_floorplan_edge_cases():
    """Test Floorplan edge cases."""
    floorplan_data = {
        "01": {
            "name": "Floor Without Rooms"
            # Missing rooms key
        },
        "02": {"name": "Floor With Empty Rooms", "rooms": {}},
    }

    floorplan = Floorplan(floorplan_data)

    # Floor without rooms
    assert floorplan.get_floor_name("01") == "Floor Without Rooms"
    assert floorplan.get_room_name("01", "01") is None

    # Floor with empty rooms
    assert floorplan.get_floor_name("02") == "Floor With Empty Rooms"
    assert floorplan.get_room_name("02", "01") is None


def test_floorplan_none_parameters():
    """Test Floorplan with None parameters."""
    floorplan = Floorplan({"01": {"name": "Test Floor"}})

    assert floorplan.get_floor_name(None) is None
    assert floorplan.get_room_name(None, "01") is None
    assert floorplan.get_room_name("01", None) is None
    assert floorplan.get_room_name(None, None) is None


def test_floorplan_get_floors_copy():
    """Test that get_floors returns a copy, not the original data."""
    floorplan_data = {"01": {"name": "Test Floor"}}

    floorplan = Floorplan(floorplan_data)
    floors_copy = floorplan.get_floors()

    # Modify the copy
    floors_copy["02"] = {"name": "Added Floor"}

    # Original should be unchanged
    assert floorplan.get_floor_name("02") is None


def test_floorplan_has_floor():
    """Test checking if floor exists."""
    floorplan_data = {"01": {"name": "Test Floor"}, "02": {"name": "Another Floor"}}

    floorplan = Floorplan(floorplan_data)

    # Existing floors
    assert floorplan.has_floor("01") is True
    assert floorplan.has_floor("02") is True

    # Non-existent floor
    assert floorplan.has_floor("99") is False

    # Empty floorplan
    empty_floorplan = Floorplan()
    assert empty_floorplan.has_floor("01") is False


def test_floorplan_has_room():
    """Test checking if room exists on a floor."""
    floorplan_data = {
        "01": {
            "name": "Test Floor",
            "rooms": {"01": {"name": "Room 1"}, "02": {"name": "Room 2"}},
        },
        "02": {
            "name": "Floor Without Rooms"
            # Missing rooms key
        },
    }

    floorplan = Floorplan(floorplan_data)

    # Existing rooms
    assert floorplan.has_room("01", "01") is True
    assert floorplan.has_room("01", "02") is True

    # Non-existent room on existing floor
    assert floorplan.has_room("01", "99") is False

    # Room on non-existent floor
    assert floorplan.has_room("99", "01") is False

    # Room on floor without rooms
    assert floorplan.has_room("02", "01") is False


def test_floorplan_is_empty():
    """Test checking if floor plan is empty."""
    # Empty floorplan
    empty_floorplan = Floorplan()
    assert empty_floorplan.is_empty() is True

    # Empty floorplan with empty dict
    empty_floorplan2 = Floorplan({})
    assert empty_floorplan2.is_empty() is True

    # Non-empty floorplan
    floorplan_data = {"01": {"name": "Test Floor"}}
    non_empty_floorplan = Floorplan(floorplan_data)
    assert non_empty_floorplan.is_empty() is False


def test_floorplan_repr():
    """Test string representation of floor plan."""
    # Empty floorplan
    empty_floorplan = Floorplan()
    repr_str = repr(empty_floorplan)
    assert repr_str == "Floorplan(floors=0, rooms=0)"

    # Single floor with rooms
    floorplan_data = {
        "01": {
            "name": "Test Floor",
            "rooms": {"01": {"name": "Room 1"}, "02": {"name": "Room 2"}},
        }
    }
    single_floor = Floorplan(floorplan_data)
    repr_str = repr(single_floor)
    assert repr_str == "Floorplan(floors=1, rooms=2)"

    # Multiple floors with different room counts
    multi_floor_data = {
        "01": {
            "name": "Floor 1",
            "rooms": {"01": {"name": "Room 1"}, "02": {"name": "Room 2"}},
        },
        "02": {"name": "Floor 2", "rooms": {"01": {"name": "Room 1"}}},
        "03": {
            "name": "Floor 3"
            # No rooms
        },
    }
    multi_floor = Floorplan(multi_floor_data)
    repr_str = repr(multi_floor)
    assert repr_str == "Floorplan(floors=3, rooms=3)"

    # Floor with explicit None rooms (to test the None branch)
    none_rooms_data = {
        "01": {
            "name": "Floor with None rooms",
            "rooms": None,  # Explicitly None
        },
        "02": {"name": "Floor with rooms", "rooms": {"01": {"name": "Room 1"}}},
    }
    none_rooms_floor = Floorplan(none_rooms_data)
    repr_str = repr(none_rooms_floor)
    # Only count rooms from floor 02
    assert repr_str == "Floorplan(floors=2, rooms=1)"


def test_floorplan_comprehensive_coverage(mock_floorplan):
    """Test comprehensive coverage of all methods with the mock fixture."""
    # Test has_floor with realistic data
    assert mock_floorplan.has_floor("01") is True
    assert mock_floorplan.has_floor("04") is True
    assert mock_floorplan.has_floor("99") is False

    # Test has_room with realistic data
    assert mock_floorplan.has_room("01", "18") is True  # Living Room
    assert mock_floorplan.has_room("03", "0D") is True  # Primary Bedroom
    assert mock_floorplan.has_room("01", "99") is False  # Non-existent room
    assert mock_floorplan.has_room("99", "01") is False  # Non-existent floor

    # Test is_empty with realistic data
    assert mock_floorplan.is_empty() is False

    # Test __repr__ with realistic data
    repr_str = repr(mock_floorplan)
    assert repr_str == "Floorplan(floors=4, rooms=18)"


def test_floorplan_edge_cases_comprehensive():
    """Test additional edge cases for comprehensive coverage."""
    # Floor with missing room data
    floorplan_data = {
        "01": {
            "name": "Floor with None rooms",
            "rooms": None,  # rooms is None instead of missing
        }
    }

    floorplan = Floorplan(floorplan_data)
    assert floorplan.has_room("01", "01") is False
    assert floorplan.get_room_name("01", "01") is None
