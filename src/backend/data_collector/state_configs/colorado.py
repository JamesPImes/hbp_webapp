def _prep_function(**kw):
    """
    The Colorado ECMC website uses the 2nd and 3rd components of the API
    number to fill out the production URL.
    """
    api_num = kw["api_num"]
    components = api_num.split("-")
    components.pop(0)
    return components


COLORADO_CONFIG = {
    "prod_url_template": "https://ecmc.state.co.us/cogisdb/Facility/Production?api_county_code={0}&api_seq_num={1}",
    "date_col": "First of Month",
    "oil_prod_col": "Oil Produced",
    "gas_prod_col": "Gas Produced",
    "days_produced_col": "Days Produced",
    "status_col": "Well Status",
    "auth": None,
    "shutin_codes": ["SI"],
    "oil_prod_min": 0,
    "gas_prod_min": 0,
    "url_component_function": _prep_function,
}


__all__ = [
    "COLORADO_CONFIG",
]
