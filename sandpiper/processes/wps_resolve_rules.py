from pywps import Process, LiteralInput, ComplexInput, LiteralOutput, UOM, Format
from pywps.app.Common import Metadata
import csv
import json
from p2a_impacts.resolver import resolve_rules

import logging


LOGGER = logging.getLogger("PYWPS")


class ResolveRules(Process):
    """Resolves climatological impacts rules"""

    def __init__(self):
        inputs = [
            ComplexInput(
                "csv",
                "CSV ruleset",
                abstract="CSV file",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[Format('text/csv'),],
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
                "ensemble",
                "Ensemble",
                abstract="Ensemble name filter for data files",
                min_occurs=1,
                max_occurs=1,
                default="p2a_files",
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
            LiteralOutput(
                "output",
                "Output response",
                abstract="A friendly Hello from us.",
                keywords=["output", "result", "response"],
                data_type="string",
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


    @staticmethod
    def _handler(request, response):
        LOGGER.info("say hello")
        output_args(request)
        response.outputs["output"].data = "Hello " + request.inputs["name"][0].data
        response.outputs["output"].uom = UOM("unity")
        return response

def output_args(request):
    args = []
    args.append(request.inputs["csv"][0].data)
    args.append(request.inputs["date_range"][0].data)
    args.append(request.inputs["region"][0].data)
    args.append(request.inputs["geoserver"][0].data)
    args.append(request.inputs["ensemble"][0].data)
    args.append(request.inputs["log_level"][0].data)

    for arg in args:
        print(arg)
