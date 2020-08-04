from pywps import Process, LiteralInput, ComplexOutput, FORMATS
from pywps.app.Common import Metadata
import csv
import json
import logging
import requests
import os
from decimal import Decimal
from p2a_impacts.resolver import resolve_rules
from p2a_impacts.utils import get_region, REGIONS


LOGGER = logging.getLogger("PYWPS")


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
                allowed_values=[region for region in REGIONS.keys()],
                default="bc",
                data_type="string",
            ),
            LiteralInput(
                "geoserver",
                "Geoserver URL",
                abstract="Geoserver URL",
                min_occurs=1,
                max_occurs=1,
                default="https://docker-dev03.pcic.uvic.ca/geoserver/bc_regions/ows",
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
        for target in [
            key for key, value in resolved.items() if type(value) == Decimal
        ]:
            resolved.update({target: str(resolved[target])})

        # Create output
        filepath = os.path.join(self.workdir, "resolved.json")
        with open(filepath, "w") as f:
            json.dump(resolved, f)

        response.outputs["json"].file = filepath
        return response
