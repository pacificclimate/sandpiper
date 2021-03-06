from pywps import Process, LiteralInput, LiteralOutput
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError

from p2a_impacts.parser import build_parse_tree
from wps_tools.logging import log_handler
from wps_tools.io import log_level
from sandpiper.utils import logger


class Parser(Process):
    """Breaks down a logical condition into a parse tree"""

    def __init__(self):
        self.status_percentage_steps = {
            "start": 0,
            "process": 10,
            "build_output": 95,
            "complete": 100,
        }

        inputs = [
            LiteralInput(
                "condition",
                "Condition",
                abstract="The condition used to break down",
                data_type="string",
            ),
            log_level,
        ]

        outputs = [
            LiteralOutput(
                "parse_tree",
                "Parse tree",
                abstract="Parse tree generated by a condition",
                data_type="string",
            ),
            LiteralOutput(
                "variables",
                "Variables",
                abstract="All variables used in the parse tree",
                data_type="string",
            ),
            LiteralOutput(
                "region_variable",
                "Region variable",
                abstract="The region the data is associated with",
                data_type="string",
            ),
        ]

        super(Parser, self).__init__(
            self._handler,
            identifier="parser",
            title="Parser",
            abstract="Process a condition into a parse tree",
            keywords=["parse", "tree"],
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
            self,
            response,
            "Starting Process",
            logger,
            log_level=loglevel,
            process_step="start",
        )

        condition = request.inputs["condition"][0].data

        log_handler(
            self,
            response,
            "Building parse tree",
            logger,
            log_level=loglevel,
            process_step="process",
        )

        try:
            parse_tree, vars, region_var = build_parse_tree(condition)
        except SyntaxError as e:
            raise ProcessError(f"{type(e).__name__}: Invalid syntax in condition")
        except ValueError as e:
            raise ProcessError(
                f"{type(e).__name__}: variable name should have 5 values, variable, "
                "time_of_year, temporal, spatial, and percentile"
            )
        except Exception as e:
            raise ProcessError(f"{type(e).__name__}: {e}")

        log_handler(
            self,
            response,
            "Cleaning and building final output",
            logger,
            log_level=loglevel,
            process_step="build_output",
        )

        response.outputs["parse_tree"].data = parse_tree
        response.outputs["variables"].data = vars
        response.outputs["region_variable"].data = region_var

        log_handler(
            self,
            response,
            "Process Complete",
            logger,
            log_level=loglevel,
            process_step="complete",
        )
        return response
