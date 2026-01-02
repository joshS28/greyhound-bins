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
        now_dt = dt_util.now()
        now_date = now_dt.date()
        
        # Reference date: Thursday 1st Jan 2026
        reference_date = BLACK_BIN_REFERENCE_DATE.date()
        
        # Calculate offset from reference date
        if self._bin_type == BIN_TYPE_BLACK:
            reference = reference_date
        else:
            # Green & Brown bins start one week after black bin
            reference = reference_date + timedelta(days=7)
        
        # Find the next collection date
        days_since_reference = (now_date - reference).days
        
        if days_since_reference < 0:
            next_collection_date = reference
        else:
            # Calculate how many collection cycles have passed
            cycles_passed = days_since_reference // COLLECTION_INTERVAL_DAYS
            
            # Calculate the potential collection date
            next_collection_date = reference + timedelta(days=(cycles_passed * COLLECTION_INTERVAL_DAYS))
            
            # If that date is in the past, move to the next cycle
            if next_collection_date < now_date:
                next_collection_date = reference + timedelta(days=((cycles_passed + 1) * COLLECTION_INTERVAL_DAYS))
        
        # Convert back to a datetime at midnight for the state
        return datetime.combine(next_collection_date, datetime.min.time())

    async def async_update(self) -> None:
        """Update the sensor."""
        self._next_collection = self._calculate_next_collection()
        now_date = dt_util.now().date()
        self._days_until = (self._next_collection.date() - now_date).days


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
        now_date = dt_util.now().date()
        reference_date = BLACK_BIN_REFERENCE_DATE.date()
        
        # Calculate next black bin collection
        black_reference = reference_date
        days_since_black = (now_date - black_reference).days
        
        if days_since_black < 0:
            next_black = black_reference
        else:
            cycles_passed = days_since_black // COLLECTION_INTERVAL_DAYS
            next_black = black_reference + timedelta(days=(cycles_passed * COLLECTION_INTERVAL_DAYS))
            if next_black < now_date:
                next_black = black_reference + timedelta(days=((cycles_passed + 1) * COLLECTION_INTERVAL_DAYS))
        
        # Calculate next green & brown bin collection
        green_brown_reference = reference_date + timedelta(days=7)
        days_since_green = (now_date - green_brown_reference).days
        
        if days_since_green < 0:
            next_green_brown = green_brown_reference
        else:
            cycles_passed = days_since_green // COLLECTION_INTERVAL_DAYS
            next_green_brown = green_brown_reference + timedelta(days=(cycles_passed * COLLECTION_INTERVAL_DAYS))
            if next_green_brown < now_date:
                next_green_brown = green_brown_reference + timedelta(days=((cycles_passed + 1) * COLLECTION_INTERVAL_DAYS))
        
        # Return whichever is sooner
        if next_black <= next_green_brown:
            return datetime.combine(next_black, datetime.min.time()), BIN_TYPE_BLACK
        else:
            return datetime.combine(next_green_brown, datetime.min.time()), BIN_TYPE_GREEN_BROWN

    async def async_update(self) -> None:
        """Update the sensor."""
        self._next_collection, self._bin_type = self._calculate_next_collection()
        now_date = dt_util.now().date()
        self._days_until = (self._next_collection.date() - now_date).days
