import os
import json
from pywps import Process, LiteralInput, LiteralOutput
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError

from p2a_impacts.parser import build_parse_tree
from wps_tools.logging import log_handler
from wps_tools.io import log_level
from sandpiper.io import json_output
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
                "conditions",
                "Conditions",
                abstract="The conditions used to break down",
                min_occurs=1,
                max_occurs=100,
                data_type="string",
            ),
            log_level,
        ]

        outputs = [json_output]

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

        conditions = request.inputs["conditions"]

        log_handler(
            self,
            response,
            "Building parse tree",
            logger,
            log_level=loglevel,
            process_step="process",
        )

        try:
            parsed_vars = {}
            for condition in conditions:
                parse_tree, vars, region_var = build_parse_tree(condition.data)
                parsed_vars[condition.data] = {
                    "parse_tree": parse_tree,
                    "variables": vars,
                    "region_variable": region_var,
                }
        except SyntaxError as e:
            raise ProcessError(
                f"{type(e).__name__}: Invalid syntax in condition {conditions.index(condition)}"
            )
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

        filepath = os.path.join(self.workdir, "parsed_vars.json")
        with open(filepath, "w") as f:
            json.dump(parsed_vars, f)

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
