from backend.utils.state_codes import STATE_CODES
from .colorado import COLORADO_CONFIG

# from .north_dakota import NORTH_DAKOTA_CONFIG


# By API state code.
STATE_CODE_SCRAPER_CONFIGS = {
    "05": COLORADO_CONFIG,
    # "38": NORTH_DAKOTA_CONFIG  # Requires auth.
}

# By state name.
STATE_SCRAPER_CONFIGS = {
    STATE_CODES[code]: config for code, config in STATE_CODE_SCRAPER_CONFIGS.items()
}


__all__ = [
    "STATE_CODE_SCRAPER_CONFIGS",
    "STATE_SCRAPER_CONFIGS",
    "COLORADO_CONFIG",
    # "NORTH_DAKOTA_CONFIG",
]
