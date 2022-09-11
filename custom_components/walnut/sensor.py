from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TEMP_CELSIUS, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN

from .models import (
    WalnutBaseEntity,
    WalnutDataUpdateCoordinator
)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_devices: AddEntitiesCallback) -> None:
    coordinator: WalnutDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    sensors: list[SensorEntityDescription] = [
        SensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_category=EntityCategory.DIAGNOSTIC,
            key="temperature",
            name="Temperature",
            native_unit_of_measurement=TEMP_CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        SensorEntityDescription(
            device_class=SensorDeviceClass.HUMIDITY,
            entity_category=EntityCategory.DIAGNOSTIC,
            key="humidity",
            name="Humidity",
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT
        )
    ]

    async_add_devices([
        TemperatureSensor(coordinator, sensors[0]),
        HumiditySensor(coordinator, sensors[1])
    ])

class TemperatureSensor(WalnutBaseEntity, SensorEntity):
    _attr_has_entity_name = True
    _coordinator: WalnutDataUpdateCoordinator

    def __init__(self, coordinator: WalnutDataUpdateCoordinator, description: SensorEntityDescription) -> None:
        super().__init__(coordinator)
        self._coordinator = coordinator
        self.entity_description = description
        self._attr_unique_id = f"{self._device.address}-{description.key}"

    @property
    def native_value(self) -> StateType:
        return self._device.temperature

class HumiditySensor(WalnutBaseEntity, SensorEntity):
    _attr_has_entity_name = True
    _coordinator: WalnutDataUpdateCoordinator

    def __init__(self, coordinator: WalnutDataUpdateCoordinator, description: SensorEntityDescription) -> None:
        super().__init__(coordinator)
        self._coordinator = coordinator
        self.entity_description = description
        self._attr_unique_id = f"{self._device.address}-{description.key}"

    @property
    def native_value(self) -> StateType:
        return self._device.humidity