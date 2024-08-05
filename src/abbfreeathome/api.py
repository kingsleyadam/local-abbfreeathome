"""Provides a class for interacting with the ABB-free@home API."""

import requests

from .bin.exceptions import (
    InvalidCredentialsException,
    SetDatapointFailureException,
    UserNotFoundException,
)

API_VERSION = "v1"


class FreeAtHomeApi:
    """Provides a class for interacting with the ABB-free@home API."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        sysap_uuid: str = "00000000-0000-0000-0000-000000000000",
    ) -> None:
        """Initialize the FreeAtHomeApi class."""
        self._sysap_uuid = sysap_uuid
        self._host = host.rstrip("/")
        self._username = username
        self._password = password

    def get_configuration(self) -> dict:
        """Get the Free@Home Configuration."""
        return self.request(path="/api/rest/configuration").get(self._sysap_uuid)

    def get_datapoint(
        self, device_id: str, channel_id: str, datapoint: str
    ) -> list[str]:
        """Get a specific datapoint from the api."""
        _response = self.request(
            path=f"/api/rest/datapoint/{self._sysap_uuid}/{device_id}.{channel_id}.{datapoint}",
            method="get",
        )

        return _response.get(self._sysap_uuid).get("values")

    def get_device_list(self) -> list:
        """Get the list of devices."""
        return self.request(path="/api/rest/devicelist").get(self._sysap_uuid)

    def get_device(self, device_serial: str):
        """Get a specific device from the api."""
        return (
            self.request(path=f"/api/rest/device/{self._sysap_uuid}/{device_serial}")
            .get(self._sysap_uuid)
            .get("devices")
            .get(device_serial)
        )

    def get_settings(self):
        """Get the settings from the api."""
        _response = requests.request(
            method="get", url=f"{self._host}/settings.json", timeout=10
        )
        _response.raise_for_status()

        return _response.json()

    def get_sysap(self):
        """Get the sysap from the api."""
        return self.request(path="/api/rest/sysap")

    def get_user(self, name: str) -> str:
        """Get a specific user from the api."""
        _settings = self.get_settings()

        _user = next(
            iter(user for user in _settings.get("users") if user.get("name") == name),
            None,
        )

        if _user is None:
            raise UserNotFoundException(f"User not found; {name}.")

        return _user

    def set_datapoint(
        self, device_id: str, channel_id: str, datapoint: str, value: str
    ) -> bool:
        """Set a specific datapoint in the api. This is used to control devices."""
        _response = self.request(
            path=f"/api/rest/datapoint/{self._sysap_uuid}/{device_id}.{channel_id}.{datapoint}",
            method="put",
            data=value,
        )

        if _response.get(self._sysap_uuid).get("result").lower() != "ok":
            raise SetDatapointFailureException(
                f"Failed to set datapoint; device_id: "
                f"{device_id}; "
                f"channel_id: {channel_id}; "
                f"datapoint: {datapoint}; "
                f"value: {value}"
            )

        return True

    def request(self, path, method: str = "get", data: any | None = None):
        """Make a request to the API."""
        _root_path = f"/fhapi/{API_VERSION}"
        _response = requests.request(
            method=method,
            url=f"{self._host}{_root_path}{path}",
            auth=(self._username, self._password),
            data=data,
            timeout=10,
        )

        try:
            _response.raise_for_status()
        except requests.exceptions.HTTPError as http_exception:
            if http_exception.response.status_code == 401:
                raise InvalidCredentialsException(
                    f"Invalid credentials for user: {self._username}"
                ) from http_exception
            raise

        return _response.json()


if __name__ == "__main__":
    pass
