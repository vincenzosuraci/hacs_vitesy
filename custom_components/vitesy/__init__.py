import logging
_LOGGER = logging.getLogger(__name__)

from .const import (
    SENSOR,
    DOMAIN,
    CONF_ACCESS_TOKEN,
    CONF_ID_TOKEN,
)

try:
    from homeassistant.core import HomeAssistant
    from homeassistant.config_entries import ConfigEntry

    from .sensor import async_setup_entry as async_setup_sensors
    from .vitesy_device import VitesyDevice
    from .coordinator import VitesyCoordinator

    async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:

        access_token = config_entry.data[CONF_ACCESS_TOKEN]
        id_token = config_entry.data[CONF_ID_TOKEN]

        device = VitesyDevice(params={
            "access_token": access_token,
            "id_token": id_token
        })

        # Inizializza il coordinatore
        coordinator = VitesyCoordinator(hass, device)

        # Memorizza il coordinatore nel registro dei dati di Home Assistant
        hass.data.setdefault(DOMAIN, {})[config_entry.entry_id] = coordinator

        await coordinator.async_config_entry_first_refresh()

        await hass.config_entries.async_forward_entry_setups(config_entry, [SENSOR])

        return True


    async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
        await hass.config_entries.async_forward_entry_unload(config_entry, SENSOR)
        hass.data[DOMAIN].pop(config_entry.entry_id)

        return True

except ModuleNotFoundError:
    print("Execution outside the Home Assistant environment")