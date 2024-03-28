def _prep_function(**kw):
    """
    North Dakota's DMR website requires their own file number, the 'NDIC
    number'.  This will require passing ``ndic_num=<file number>`` to
    the ``.get_well_data()`` method, in addition to the API number.
    """
    return kw["ndic_num"]


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
    "url_component_function": _prep_function,
}
