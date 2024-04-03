from bs4 import BeautifulSoup


def _url_prep_function(**kw):
    """
    North Dakota's DMR website requires their own file number, the 'NDIC
    number'.  This will require passing ``ndic_num=<file number>`` to
    the ``.get_well_data()`` method, in addition to the API number.
    :param kw: a dict that should contain the key ``'ndic_num'``, whose
     value is the NDIC's file number for a North Dakota well.
    :return: A list of the 1 component necessary to complete the URL of
     the production records for a given well.
    """
    return kw["ndic_num"]


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

    # Well name is in the first <b> tag following "Current Well Name:".
    soup = BeautifulSoup(html[html.find("Current Well Name:") :], "html.parser")
    found_tag = soup.find("b")
    if found_tag is None:
        return well_name
    try:
        well_name_raw_contents = found_tag.contents
        well_name = str(well_name_raw_contents[0]).strip()
    except IndexError:
        pass
    return well_name


NORTH_DAKOTA_CONFIG = {
    "prod_url_template": "https://www.dmr.nd.gov/oilgas/feeservices/getwellprod.asp?filenumber={0}",
    "date_col": "Date",
    "oil_prod_col": "BBLS Oil",
    "gas_prod_col": "MCF Prod",
    "days_produced_col": "Days",
    "auth": None,
    "status_col": None,
    "shutin_codes": [],
    "oil_prod_min": 0,
    "gas_prod_min": 0,
    "url_component_function": _url_prep_function,
    "well_name_function": _get_well_name_function,
}
