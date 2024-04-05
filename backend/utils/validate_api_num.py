
STATE_CODES = {
    "01": "Alabama",
    "02": "Arizona",
    "03": "Arkansas",
    "04": "California",
    "05": "Colorado",
    "06": "Connecticut",
    "07": "Delaware",
    "08": "District of Columbia",
    "09": "Florida",
    "10": "Georgia",
    "11": "Idaho",
    "12": "Illinois",
    "13": "Indiana",
    "14": "Iowa",
    "15": "Kansas",
    "16": "Kentucky",
    "17": "Louisiana",
    "18": "Maine",
    "19": "Maryland",
    "20": "Massachusetts",
    "21": "Michigan",
    "22": "Minnesota",
    "23": "Mississippi",
    "24": "Missouri",
    "25": "Montana",
    "26": "Nebraska",
    "27": "Nevada",
    "28": "New Hampshire",
    "29": "New Jersey",
    "30": "New Mexico",
    "31": "New York",
    "32": "North Carolina",
    "33": "North Dakota",
    "34": "Ohio",
    "35": "Oklahoma",
    "36": "Oregon",
    "37": "Pennsylvania",
    "38": "Rhode Island",
    "39": "South Carolina",
    "40": "South Dakota",
    "41": "Tennessee",
    "42": "Texas",
    "43": "Utah",
    "44": "Vermont",
    "45": "Virginia",
    "46": "Washington",
    "47": "West Virginia",
    "48": "Wisconsin",
    "49": "Wyoming",
    "50": "Alaska",
    "51": "Hawaii",
    "55": "Alaska Offshore",
    "56": "Pacific Coast Offshore",
    "60": "Northern Gulf of Mexico",
    "61": "Atlantic Coast Offshore",
}


def validate_api_num(api_num: str) -> bool:
    """
    Validate that a given API number follows the appropriate schema,
    such as:

     - 05-123-45678

     - 05-123-45678-00-01

    Moreover, the state code (the first 2 digits) must be valid (i.e.,
    ``'01'`` through ``'51'``, ``'55'``, ``'56'``, ``'60'``, or
    ``'61'``). This function will NOT check whether the county code (the
    second component, being 3 digits) or the unique well identifier (the
    third component, being 5 digits) refer to valid counties or wells.

    :param api_num: The string to validate.

    :return: True if valid; False otherwise.
    """
    if not isinstance(api_num, str):
        return False
    components = api_num.split('-')
    if len(components) not in (3, 5):
        return False
    if components[0] not in STATE_CODES.keys():
        return False
    if len(components[1]) != 3 or len(components[2]) != 5:
        return False
    if len(components) == 5 and (len(components[3]) != 2 or len(components[4]) != 2):
        return False
    return True


__all__ = [
    'STATE_CODES',
    'validate_api_num',
]
