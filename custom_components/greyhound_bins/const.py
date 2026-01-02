"""Constants for the Greyhound Bins integration."""
from datetime import datetime

DOMAIN = "greyhound_bins"

# Reference date: Black bin on Thursday 1st Jan 2026
BLACK_BIN_REFERENCE_DATE = datetime(2026, 1, 1, 0, 0, 0)

# Bin types
BIN_TYPE_BLACK = "black"
BIN_TYPE_GREEN_BROWN = "green_brown"

# Collection happens every 2 weeks for each bin type
COLLECTION_INTERVAL_DAYS = 14
