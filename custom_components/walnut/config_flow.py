"""Config flow for Walnut integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.bluetooth import async_discovered_service_info
from homeassistant.components.bluetooth.models import BluetoothServiceInfoBleak
from homeassistant.const import CONF_ADDRESS
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, SERVICE_UUID

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Walnut."""

    VERSION = 1
    
    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered_addresses: list[str] = []

    def _create_entry(self, address: str) -> FlowResult:
        """Create an entry for a discovered device."""

        return self.async_create_entry(
            title=address,
            data={
                CONF_ADDRESS: address,
            },
        )

    async def async_step_bluetooth(self, discovery_info: BluetoothServiceInfoBleak) -> FlowResult:
        """Handle the bluetooth discovery step."""
        _LOGGER.debug("discovered by bluetooth")
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        self._discovery_info = discovery_info
        self.context["title_placeholders"] = {
            "name": "hello"
        }
        return await self.async_step_user()

    async def async_step_pick_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle step to pick discovered device."""

        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()

            return self._create_entry(address)
        
        current_addresses = self._async_current_ids()
        for discovery_info in async_discovered_service_info(self.hass, connectable=True):
            if SERVICE_UUID in discovery_info.service_uuids:
                address = discovery_info.address
                if (address not in current_addresses and address not in self._discovered_addresses):
                    self._discovered_addresses.append(address)

        addresses = {
            address
            for address in self._discovered_addresses
            if address not in current_addresses
        }

        if not addresses:
            return self.async_abort(reason="no_devices_found")

        return self.async_show_form(
            step_id="pick_device",
            data_schema=vol.Schema({vol.Required(CONF_ADDRESS): vol.In(addresses)})
        )
    
    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle a flow initialized by the user."""
        return await self.async_step_pick_device()