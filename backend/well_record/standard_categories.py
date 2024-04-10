
# Months during which there is no production; and ignoring shut-in
# status codes.
NO_PROD_IGNORE_SHUTIN = "NO_PROD_IGNORE_SHUTIN"

# Months during which there is no production; but if a well is shut-in,
# it counts as producing.
NO_PROD_BUT_SHUTIN_COUNTS = "NO_PROD_BUT_SHUTIN_COUNTS"


CATEGORY_DESCRIPTIONS = {
    NO_PROD_IGNORE_SHUTIN: "No production (ignore shut-in)",
    NO_PROD_BUT_SHUTIN_COUNTS: "No production (shut-in counts as production)",
}


__all__ = [
    "NO_PROD_IGNORE_SHUTIN",
    "NO_PROD_BUT_SHUTIN_COUNTS",
    "CATEGORY_DESCRIPTIONS",
]
