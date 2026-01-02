# Greyhound Bins - Home Assistant Integration

[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)

A Home Assistant custom integration for tracking Greyhound bin collection schedules.

## Features

- 🗑️ **Black Bin Collection Tracking** - Know when your black bin is due for collection
- ♻️ **Green & Brown Bins Collection Tracking** - Track recycling and garden waste collections
- 📅 **Next Collection Sensor** - Always know which bin is next and when
- 🔔 **Automation Ready** - Use sensors to create reminders and notifications
- ⏰ **Accurate Scheduling** - Automatically calculates the alternating weekly schedule

## Schedule

The integration tracks the following schedule:
- **Black Bin**: Every other Thursday (starting Thursday 1st January 2026)
- **Green & Brown Bins**: Every other Thursday (starting Thursday 8th January 2026)

The bins alternate weekly, so you'll have a collection every Thursday, alternating between black and green/brown bins.

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add `https://github.com/joshS28/greyhound-bins` as an Integration
6. Click "Download"
7. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/greyhound_bins` directory to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Greyhound Bins"
4. Click to add the integration
5. The integration will be added with no additional configuration needed

## Sensors

The integration provides three sensors:

### 1. Greyhound Black Bin Collection
- **Entity ID**: `sensor.greyhound_black_bin_collection`
- **State**: Next collection date (e.g., "Thursday, 15 January 2026")
- **Attributes**:
  - `days_until_collection`: Number of days until collection
  - `collection_date`: Date in YYYY-MM-DD format
  - `collection_day`: Day of the week
  - `is_tomorrow`: Boolean indicating if collection is tomorrow
  - `is_today`: Boolean indicating if collection is today

### 2. Greyhound Green & Brown Bins Collection
- **Entity ID**: `sensor.greyhound_green_brown_bins_collection`
- **State**: Next collection date
- **Attributes**: Same as Black Bin sensor

### 3. Greyhound Next Bin Collection
- **Entity ID**: `sensor.greyhound_next_bin_collection`
- **State**: Next collection date (whichever bin is next)
- **Attributes**:
  - `bin_type`: Which bin is being collected ("Black Bin" or "Green & Brown Bins")
  - `days_until_collection`: Number of days until collection
  - `collection_date`: Date in YYYY-MM-DD format
  - `collection_day`: Day of the week
  - `is_tomorrow`: Boolean indicating if collection is tomorrow
  - `is_today`: Boolean indicating if collection is today

## Automation Examples

### Reminder the Night Before Collection

```yaml
automation:
  - alias: "Bin Collection Reminder"
    trigger:
      - platform: state
        entity_id: sensor.greyhound_next_bin_collection
        attribute: is_tomorrow
        to: true
    action:
      - service: notify.mobile_app
        data:
          title: "Bin Collection Tomorrow"
          message: >
            Don't forget to put out the {{ state_attr('sensor.greyhound_next_bin_collection', 'bin_type') }} 
            for collection tomorrow!
```

### Morning of Collection Reminder

```yaml
automation:
  - alias: "Bin Collection Today"
    trigger:
      - platform: time
        at: "07:00:00"
    condition:
      - condition: state
        entity_id: sensor.greyhound_next_bin_collection
        attribute: is_today
        state: true
    action:
      - service: notify.mobile_app
        data:
          title: "Bin Collection Today"
          message: >
            {{ state_attr('sensor.greyhound_next_bin_collection', 'bin_type') }} 
            collection is today!
```

## Support

If you encounter any issues or have suggestions, please [open an issue](https://github.com/joshS28/greyhound-bins/issues) on GitHub.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

Created by [@joshS28](https://github.com/joshS28)

---

[releases-shield]: https://img.shields.io/github/release/joshS28/greyhound-bins.svg?style=for-the-badge
[releases]: https://github.com/joshS28/greyhound-bins/releases
[license-shield]: https://img.shields.io/github/license/joshS28/greyhound-bins.svg?style=for-the-badge
