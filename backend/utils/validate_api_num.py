from .state_codes import STATE_CODES


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
    components = api_num.split("-")
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
    "validate_api_num",
]
