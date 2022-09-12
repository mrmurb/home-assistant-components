"""The Walnut integration."""
from __future__ import annotations

from homeassistant.components.bluetooth import (
    async_ble_device_from_address,
    async_register_callback
)
from homeassistant.components.bluetooth.match import BluetoothCallbackMatcher
from homeassistant.components.bluetooth.models import BluetoothChange, BluetoothScanningMode, BluetoothServiceInfoBleak
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_ADDRESS
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .walnut import Walnut
from .models import WalnutDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Walnut from a config entry."""

    hass.data.setdefault(DOMAIN, {}).setdefault(entry.entry_id, {})

    ble_device = async_ble_device_from_address(hass, entry.data[CONF_ADDRESS])
    
    if not ble_device:
        raise ConfigEntryNotReady(
            f"Couldn't find a nearby device for address: {entry.data[CONF_ADDRESS]}"
        )

    device = Walnut(ble_device)

    @callback
    def _async_update_ble(service_info: BluetoothServiceInfoBleak, change: BluetoothChange) -> None:
        if change != BluetoothChange.ADVERTISEMENT:
            return
        device.update_device(service_info.device, service_info.manufacturer_data)

    async_register_callback(
        hass,
        _async_update_ble,
        BluetoothCallbackMatcher(address=ble_device.address),
        BluetoothScanningMode.PASSIVE
    )

    coordinator = WalnutDataUpdateCoordinator(hass, device)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
    