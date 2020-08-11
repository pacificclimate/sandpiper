from pywps import Process, LiteralInput, ComplexOutput, FORMATS
from pywps.app.Common import Metadata
import csv
import json
import requests
import os
from decimal import Decimal
from p2a_impacts.resolver import resolve_rules
from p2a_impacts.utils import get_region, REGIONS
from wps_tools.utils import log_handler
from wps_tools.io import log_level


class ResolveRules(Process):
    """Resolves climatological impacts rules"""

    def __init__(self):
        self.status_percentage_steps = {
            "start": 0,
            "process": 10,
            "build_output": 95,
            "complete": 100,
        }
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
            log_level,
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
        loglevel = request.inputs["loglevel"][0].data
        log_handler(
            self, response, "Starting Process", process_step="start", log_level=loglevel
        )
        rules, date_range, region, geoserver, connection_string, ensemble, loglevel = [
            input[0].data for input in request.inputs.values()
        ]

        region = get_region(region, geoserver)
        log_handler(
            self,
            response,
            "Resolving impacts rules",
            process_step="process",
            log_level=loglevel,
        )
        resolved = resolve_rules(
            rules, date_range, region, ensemble, connection_string, loglevel
        )

        log_handler(
            self,
            response,
            "Cleaning and building final output",
            process_step="build_output",
            log_level=loglevel,
        )
        for target in [
            key for key, value in resolved.items() if type(value) == Decimal
        ]:
            resolved.update({target: str(resolved[target])})

        filepath = os.path.join(self.workdir, "resolved.json")
        with open(filepath, "w") as f:
            json.dump(resolved, f)

        response.outputs["json"].file = filepath
        log_handler(
            self,
            response,
            "Process Complete",
            process_step="complete",
            log_level=loglevel,
        )
        return response
