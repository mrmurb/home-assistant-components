from datetime import timedelta
import logging

from homeassistant.components.bluetooth import async_ble_device_from_address
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .walnut import Walnut

_LOGGER = logging.getLogger(__name__)

class WalnutDataUpdateCoordinator(DataUpdateCoordinator[Walnut]):
    _device: Walnut

    def __init__(self, hass: HomeAssistant, device: Walnut) -> None:
        self._device = device
        super().__init__(hass, _LOGGER, name="Walnut Bluetooth", update_interval=timedelta(minutes=1))

    async def _async_update_data(self):
        await self._device.fetch_values()
        return self._device

class WalnutBaseEntity(CoordinatorEntity[WalnutDataUpdateCoordinator]):
    _device: Walnut

    def __init__(self, coordinator: WalnutDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._device = coordinator.data
    
    @callback
    def _handle_coordinator_update(self) -> None:
        self._device = self.coordinator.data
        self.async_write_ha_state()
    
    @callback
    def available(self) -> bool:
        ble_device = async_ble_device_from_address(self._device.address)
        return ble_device is not None