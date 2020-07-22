from pywps import Process, LiteralInput, ComplexOutput, FORMATS
from pywps.app.Common import Metadata
import csv
import json
import logging
import requests
import os
from decimal import Decimal
from p2a_impacts.resolver import resolve_rules


LOGGER = logging.getLogger("PYWPS")


regions = {
    "bc": "British Columbia",
    "alberni_clayoquot": "Alberni-Clayoquot",
    "boreal_plains": "Boreal Plains",
    "bulkley_nechako": "Bulkley-Nechako",
    "capital": "Capital",
    "cariboo": "Cariboo",
    "central_coast": "Central Coast",
    "central_kootenay": "Central Kootenay",
    "central_okanagan": "Central Okanagan",
    "columbia_shuswap": "Columbia-Shuswap",
    "comox_valley": "Comox Valley",
    "cowichan_valley": "Cowichan Valley",
    "east_kootenay": "East Kootenay",
    "fraser_fort_george": "Fraser-Fort George",
    "fraser_valley": "Fraser Valley",
    "greater_vancouver": "Greater Vancouver",
    "kitimat_stikine": "Kitimat-Stikine",
    "kootenay_boundary": "Kootenay Boundary",
    "mt_waddington": "Mount Waddington",
    "nanaimo": "Nanaimo",
    "northern_rockies": "Northern Rockies",
    "north_okanagan": "North Okanagan",
    "okanagan_similkameen": "Okanagan-Similkameen",
    "peace_river": "Peace River",
    "powell_river": "Powell River",
    "skeena_queen_charlotte": "Skeena-Queen Charlotte",
    "squamish_lillooet": "Squamish-Lillooet",
    "stikine": "Stikine",
    "strathcona": "Strathcona",
    "sunshine_coast": "Sunshine Coast",
    "thompson_nicola": "Thompson-Nicola",
    "interior": "Interior",
    "northern": "Northern",
    "vancouver_coast": "Vancouver Coast",
    "vancouver_fraser": "Vancouver Fraser",
    "vancouver_island": "Vancouver Island",
    "central_interior": "Central Interior",
    "coast_and_mountains": "Coast and Mountains",
    "georgia_depression": "Georgia Depression",
    "northern_boreal_mountains": "Northern Boreal Mountains",
    "southern_interior": "Southern Interior",
    "southern_interior_mountains": "Southern Interior Mountains",
    "sub_boreal_mountains": "Sub Boreal Mountains",
    "taiga_plains": "Taiga Plains",
    "cariboo": "Cariboo",
    "kootenay_/_boundary": "Kootenay / Boundary",
    "northeast": "Northeast",
    "omineca": "Omineca",
    "skeena": "Skeena",
    "south_coast": "South Coast",
    "thompson_okanagan": "Thompson / Okanagan",
    "west_coast": "West Coast",
}


def get_region(region_name, url):
    """Given a region name and URL retrieve a csv row from Geoserver
       The region_name variable should be a selection from the regions
       dictionary object.  This object contains all the options available in
       Geoserver.
       The URL in the default case is for the Geoserver instance running on
       docker-dev01.
       The return value from this method is a csv row output from
       Geoserver.  The row contains several columns but the ones used are
       coast_bool and WKT.  These contain whether or not the region is coastal
       and the polygon describing the region respectively.
    """
    params = {
        "service": "WFS",
        "version": "1.0.0",
        "request": "GetFeature",
        "typename": "bc_regions:bc-regions-polygon",
        "maxFeatures": "100",
        "outputFormat": "csv",
    }
    data = requests.get(url, params=params)

    decoded_data = data.content.decode("utf-8")
    csv_data = csv.DictReader(decoded_data.splitlines(), delimiter=",")

    region = regions[region_name]

    for row in csv_data:
        if row["english_na"] == region:
            return row


class ResolveRules(Process):
    """Resolves climatological impacts rules"""

    def __init__(self):
        inputs = [
            LiteralInput(
                "csv",
                "CSV path",
                abstract="Path to CSV file",
                min_occurs=1,
                max_occurs=1,
                data_type="string",
            ),
            LiteralInput(
                "date_range",
                "Date Range",
                abstract="30 year period for data",
                allowed_values=["2020", "2050", "2080"],
                default="2080",
                data_type="string",
            ),
            LiteralInput(
                "region",
                "BC Region",
                abstract="Impacted region",
                min_occurs=1,
                max_occurs=1,
                allowed_values=["bc"],  # temp
                default="bc",
                data_type="string",
            ),
            LiteralInput(
                "geoserver",
                "Geoserver URL",
                abstract="Geoserver URL",
                min_occurs=1,
                max_occurs=1,
                default="http://docker-dev01.pcic.uvic.ca:30123/geoserver/bc_regions/ows",
                data_type="string",
            ),
            LiteralInput(
                "connection_string",
                "Connection String",
                abstract="Database connection string",
                min_occurs=1,
                max_occurs=1,
                default="postgres://ce_meta_ro@db3.pcic.uvic.ca/ce_meta",
                data_type="string",
            ),
            LiteralInput(
                "ensemble",
                "Ensemble",
                abstract="Ensemble name filter for data files",
                min_occurs=1,
                max_occurs=1,
                default="p2a_rules",
                data_type="string",
            ),
            LiteralInput(
                "log_level",
                "Log Level",
                abstract="Python logging level",
                min_occurs=1,
                max_occurs=1,
                allowed_values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                default="INFO",
                data_type="string",
            ),
        ]
        outputs = [
            ComplexOutput(
                "json",
                "JSON Output",
                abstract="JSON file",
                supported_formats=[FORMATS.JSON],
            )
        ]

        super(ResolveRules, self).__init__(
            self._handler,
            identifier="resolve_rules",
            title="Resolve Rules",
            abstract="Resolve climatological impacts rules",
            keywords=["resolve", "rules"],
            metadata=[
                Metadata("PyWPS", "https://pywps.org/"),
                Metadata("Birdhouse", "http://bird-house.github.io/"),
                Metadata("PyWPS Demo", "https://pywps-demo.readthedocs.io/en/latest/"),
            ],
            version="0.1.0",
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
        )

    def _handler(self, request, response):
        rules, date_range, region, geoserver, connection_string, ensemble, log_level = [
            input[0].data for input in request.inputs.values()
        ]

        region = get_region(region, geoserver)
        resolved = resolve_rules(
            rules, date_range, region, ensemble, connection_string, log_level
        )

        # Clean output before sending off
        for target in [key for key, value in resolved.items() if type(value) == Decimal]:
            resolved.update({target: str(resolved[target])})

        # Create output
        filepath = os.path.join(self.workdir, "resolved.json")
        with open(filepath, "w") as f:
            json.dump(resolved, f)

        response.outputs["json"].file = filepath
        return response
