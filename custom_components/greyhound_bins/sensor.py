"""Sensor platform for Greyhound Bins integration."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    BLACK_BIN_REFERENCE_DATE,
    BIN_TYPE_BLACK,
    BIN_TYPE_GREEN_BROWN,
    COLLECTION_INTERVAL_DAYS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Greyhound Bins sensors."""
    sensors = [
        GreyhoundBinSensor(BIN_TYPE_BLACK, "Black Bin"),
        GreyhoundBinSensor(BIN_TYPE_GREEN_BROWN, "Green & Brown Bins"),
        NextCollectionSensor(),
    ]
    
    async_add_entities(sensors, True)


class GreyhoundBinSensor(SensorEntity):
    """Representation of a Greyhound Bin collection sensor."""

    def __init__(self, bin_type: str, name: str) -> None:
        """Initialize the sensor."""
        self._bin_type = bin_type
        self._attr_name = f"Greyhound {name} Collection"
        self._attr_unique_id = f"greyhound_bins_{bin_type}"
        self._attr_icon = "mdi:delete" if bin_type == BIN_TYPE_BLACK else "mdi:recycle"
        self._next_collection = None
        self._days_until = None

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if self._next_collection:
            return self._next_collection.strftime("%A, %d %B %Y")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return additional attributes."""
        if not self._next_collection:
            return {}
        
        return {
            "days_until_collection": self._days_until,
            "collection_date": self._next_collection.strftime("%Y-%m-%d"),
            "collection_day": self._next_collection.strftime("%A"),
            "is_tomorrow": self._days_until == 1,
            "is_today": self._days_until == 0,
        }

    def _calculate_next_collection(self) -> datetime:
        """Calculate the next collection date for this bin type."""
        now = dt_util.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate offset from reference date
        if self._bin_type == BIN_TYPE_BLACK:
            # Black bin starts on reference date (2026-01-01)
            reference = BLACK_BIN_REFERENCE_DATE
        else:
            # Green & Brown bins start one week after black bin
            reference = BLACK_BIN_REFERENCE_DATE + timedelta(days=7)
        
        # Find the next collection date
        days_since_reference = (now - reference).days
        
        # If we're before the reference date, use the reference date
        if days_since_reference < 0:
            next_collection = reference
        else:
            # Calculate how many collection cycles have passed
            cycles_passed = days_since_reference // COLLECTION_INTERVAL_DAYS
            
            # Calculate the next collection date
            next_collection = reference + timedelta(days=(cycles_passed * COLLECTION_INTERVAL_DAYS))
            
            # If that date is in the past or today, move to the next cycle
            if next_collection <= now:
                next_collection = reference + timedelta(days=((cycles_passed + 1) * COLLECTION_INTERVAL_DAYS))
        
        return next_collection

    async def async_update(self) -> None:
        """Update the sensor."""
        self._next_collection = self._calculate_next_collection()
        now = dt_util.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self._days_until = (self._next_collection - now).days


class NextCollectionSensor(SensorEntity):
    """Sensor showing the next bin collection regardless of type."""

    def __init__(self) -> None:
        """Initialize the sensor."""
        self._attr_name = "Greyhound Next Bin Collection"
        self._attr_unique_id = "greyhound_bins_next_collection"
        self._attr_icon = "mdi:calendar-clock"
        self._next_collection = None
        self._bin_type = None
        self._days_until = None

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if self._next_collection:
            return self._next_collection.strftime("%A, %d %B %Y")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return additional attributes."""
        if not self._next_collection:
            return {}
        
        bin_name = "Black Bin" if self._bin_type == BIN_TYPE_BLACK else "Green & Brown Bins"
        
        return {
            "bin_type": bin_name,
            "days_until_collection": self._days_until,
            "collection_date": self._next_collection.strftime("%Y-%m-%d"),
            "collection_day": self._next_collection.strftime("%A"),
            "is_tomorrow": self._days_until == 1,
            "is_today": self._days_until == 0,
        }

    def _calculate_next_collection(self) -> tuple[datetime, str]:
        """Calculate the next collection date (either bin type)."""
        now = dt_util.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate next black bin collection
        black_reference = BLACK_BIN_REFERENCE_DATE
        days_since_black = (now - black_reference).days
        
        if days_since_black < 0:
            next_black = black_reference
        else:
            cycles_passed = days_since_black // COLLECTION_INTERVAL_DAYS
            next_black = black_reference + timedelta(days=(cycles_passed * COLLECTION_INTERVAL_DAYS))
            if next_black <= now:
                next_black = black_reference + timedelta(days=((cycles_passed + 1) * COLLECTION_INTERVAL_DAYS))
        
        # Calculate next green & brown bin collection
        green_brown_reference = BLACK_BIN_REFERENCE_DATE + timedelta(days=7)
        days_since_green = (now - green_brown_reference).days
        
        if days_since_green < 0:
            next_green_brown = green_brown_reference
        else:
            cycles_passed = days_since_green // COLLECTION_INTERVAL_DAYS
            next_green_brown = green_brown_reference + timedelta(days=(cycles_passed * COLLECTION_INTERVAL_DAYS))
            if next_green_brown <= now:
                next_green_brown = green_brown_reference + timedelta(days=((cycles_passed + 1) * COLLECTION_INTERVAL_DAYS))
        
        # Return whichever is sooner
        if next_black <= next_green_brown:
            return next_black, BIN_TYPE_BLACK
        else:
            return next_green_brown, BIN_TYPE_GREEN_BROWN

    async def async_update(self) -> None:
        """Update the sensor."""
        self._next_collection, self._bin_type = self._calculate_next_collection()
        now = dt_util.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self._days_until = (self._next_collection - now).days
