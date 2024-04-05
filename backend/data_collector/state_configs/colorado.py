from bs4 import BeautifulSoup


def _url_prep_function(**kw):
    """
    The Colorado ECMC website uses the 2nd and 3rd components of the API
    number to fill out the production URL.
    :param kw: a dict that should contain the key ``'api_num'``, whose
     value is an API number for a Colorado well.
    :return: A list of the 2 components necessary to complete the URL of
     the production records for a given well (the 3-digit and 5-digit
     portions of the API number).
    """
    api_num = kw["api_num"]
    components = api_num.split("-")
    return components[1:2]


def _get_well_name_function(**kw) -> str | None:
    """
    Extract the well name from the HTML of the production records page
    for a given well.
    :param kw: a dict that should contain the key ``'html'``, whose
     value is the HTML of the production records page.
    :return: The well name if found; otherwise, None.
    """
    html = kw["html"]
    well_name = None
    soup = BeautifulSoup(html, 'html.parser')
    found_tag = soup.find("a", {"title": "View well scout card."})
    if found_tag is None:
        return well_name
    try:
        well_name_raw_contents = found_tag.contents
        well_name = str(well_name_raw_contents[0]).strip()
    except IndexError:
        pass
    return well_name


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
    "url_component_function": _url_prep_function,
    "well_name_function": _get_well_name_function,
}


__all__ = [
    "COLORADO_CONFIG",
]
