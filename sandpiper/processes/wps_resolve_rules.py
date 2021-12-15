import json
import os
from tempfile import NamedTemporaryFile
from pywps import Process, LiteralInput, ComplexOutput, FORMATS
from pywps.app.Common import Metadata

from p2a_impacts.resolver import resolve_rules
from p2a_impacts.utils import get_region, REGIONS
from wps_tools.logging import log_handler
from wps_tools.io import log_level, collect_args, csv_input
from wps_tools.error_handling import custom_process_error
from sandpiper.utils import logger, update_connection


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
            csv_input,
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
                min_occurs=0,
                max_occurs=1,
                allowed_values=[region for region in REGIONS.keys()],
                default="bc",
                data_type="string",
            ),
            LiteralInput(
                "geoserver",
                "Geoserver URL",
                abstract="Geoserver URL",
                min_occurs=0,
                max_occurs=1,
                default="https://docker-dev03.pcic.uvic.ca/geoserver/bc_regions/ows",
                data_type="string",
            ),
            LiteralInput(
                "connection_string",
                "Connection String",
                abstract="Database connection string",
                min_occurs=0,
                max_occurs=1,
                data_type="string",
            ),
            LiteralInput(
                "ensemble",
                "Ensemble",
                abstract="Ensemble name filter for data files",
                min_occurs=0,
                max_occurs=1,
                default="p2a_rules",
                data_type="string",
            ),
            LiteralInput(
                "thredds",
                "Thredds",
                abstract="Data from thredds server. It is not recommended to change from the default (True)",
                min_occurs=0,
                max_occurs=1,
                default=True,
                data_type="boolean",
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
        (
            csv,
            date_range,
            region,
            geoserver,
            connection_string,
            ensemble,
            thredds,
            loglevel,
        ) = [arg for arg in collect_args(request.inputs, self.workdir).values()]

        connection_string = connection_string.replace(
            "*", "@"
        )  # asterisk used for initial string from automated test to avoid removing input.
        connection_string = update_connection(connection_string)

        log_handler(
            self,
            response,
            "Starting Process",
            logger,
            log_level=loglevel,
            process_step="start",
        )

        csv.seek(0)
        csv_content = csv.read()

        try:
            csv_content = csv_content.decode("utf-8")
        except (UnicodeDecodeError, AttributeError):
            pass

        with NamedTemporaryFile(mode="w+", suffix=".csv") as temp_csv:
            temp_csv.write(csv_content)
            temp_csv.seek(0)

            log_handler(
                self,
                response,
                "Resolving impacts rules",
                logger,
                log_level=loglevel,
                process_step="process",
            )
            try:
                resolved = resolve_rules(
                    temp_csv.name,
                    date_range,
                    get_region(region, geoserver),
                    ensemble,
                    connection_string,
                    thredds,
                    loglevel,
                )
            except Exception as e:
                custom_process_error(e)

        log_handler(
            self,
            response,
            "Cleaning and building final output",
            logger,
            log_level=loglevel,
            process_step="build_output",
        )

        filepath = os.path.join(self.workdir, "resolved.json")
        with open(filepath, "w") as f:
            json.dump(resolved, f)

        response.outputs["json"].file = filepath
        log_handler(
            self,
            response,
            "Process Complete",
            logger,
            log_level=loglevel,
            process_step="complete",
        )
        return response
