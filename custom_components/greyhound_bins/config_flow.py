"""Config flow for Greyhound Bins integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class GreyhoundBinsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Greyhound Bins."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            await self.async_set_unique_id("greyhound_bins")
            self._abort_if_unique_id_configured()
            
            return self.async_create_entry(
                title="Greyhound Bins",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
        )
