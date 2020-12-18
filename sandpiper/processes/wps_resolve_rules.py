from pywps import Process, LiteralInput, ComplexInput, ComplexOutput, FORMATS, Format
from pywps.app.Common import Metadata
import json
import os
from p2a_impacts.resolver import resolve_rules
from p2a_impacts.utils import get_region, REGIONS
from wps_tools.utils import log_handler, collect_args
from wps_tools.io import log_level
from sandpiper.utils import logger


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
            ComplexInput(
                "csv",
                "CSV path",
                abstract="Path to CSV file",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[Format("text/csv", extension=".csv")],
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
                default="postgres://ce_meta_ro@db3.pcic.uvic.ca/ce_meta_12f290b63791",
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
            rules,
            date_range,
            region,
            geoserver,
            connection_string,
            ensemble,
            thredds,
            loglevel,
        ) = [arg[0] for arg in collect_args(request, self.workdir).values()]

        log_handler(
            self,
            response,
            "Starting Process",
            logger,
            log_level=loglevel,
            process_step="start",
        )

        region = get_region(region, geoserver)
        log_handler(
            self,
            response,
            "Resolving impacts rules",
            logger,
            log_level=loglevel,
            process_step="process",
        )
        resolved = resolve_rules(
            rules, date_range, region, ensemble, connection_string, thredds, loglevel
        )

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
