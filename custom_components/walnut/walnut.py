from uuid import UUID

from bleak.backends.device import BLEDevice
from bleak import BleakClient

BATTERY_CHARACTERISTIC_UUID = UUID("00002a19-0000-1000-8000-00805f9b34fb")

class Walnut:
    _device: BLEDevice
    _manufacturer_data: dict[int, bytes]

    _temperature: float
    _humidity: float
    _battery: int

    def __init__(self, device: BLEDevice) -> None:
        self._device = device
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

    def update_device(self, device: BLEDevice, manufacturer_data: dict[int, bytes]) -> None:
        self._device = device
        self._manufacturer_data = manufacturer_data

    async def fetch_values(self) -> None:
        async with BleakClient(self._device) as client:
            bat_char = await client.read_gatt_char(BATTERY_CHARACTERISTIC_UUID)
            self._battery = ord(bat_char)
        self._parse_manufacturer_data()

    @property
    def address(self) -> str:
        return self._device.address

    @property
    def temperature(self) -> float:
        return self._temperature

    @property
    def humidity(self) -> float:
        return self._humidity

    @property
    def rssi(self) -> int:
        return self._device.rssi

    @property
    def battery(self) -> int:
        return self._battery
