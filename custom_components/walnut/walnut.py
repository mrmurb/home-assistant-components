class Walnut:
    _address: str
    _manufacturer_data: dict[int, bytes]

    _temperature: float
    _humidity: float

    def __init__(self, address: str) -> None:
        self._address = address
        self._manufacturer_data = {}

    def _parse_manufacturer_data(self) -> None:
        data = self._manufacturer_data.get(979)
        if data is None:
            return

        idx = 0
        while idx < len(data):
            sensor_and_data = data[idx:idx + 4]
            sensor_id = int.from_bytes(sensor_and_data[0:2], 'big')
            sensor_data = sensor_and_data[2:4]

            if sensor_id == 1: # Temperature
                self._temperature = int.from_bytes(sensor_data, 'big') / 10
            elif sensor_id == 2:
                self._humidity = int.from_bytes(sensor_data, 'big') / 10

            idx += 4

    def update_manufacturer_data(self, manufacturer_data: dict[int, bytes]) -> None:
        self._manufacturer_data = manufacturer_data

    def fetch_values(self) -> None:
        self._parse_manufacturer_data()

    @property
    def address(self) -> str:
        return self._address

    @property
    def temperature(self) -> float:
        return self._temperature

    @property
    def humidity(self) -> float:
        return self._humidity