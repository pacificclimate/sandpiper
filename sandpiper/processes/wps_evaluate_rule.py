import os
import json
from pywps import Process, LiteralInput, LiteralOutput, ComplexInput, FORMATS
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError
from functools import partial

from p2a_impacts.fetch_data import get_dict_val
from p2a_impacts.evaluator import evaluate_rule
from wps_tools.logging import log_handler
from wps_tools.io import log_level, collect_args
from sandpiper.io import json_output
from sandpiper.utils import logger


class EvaluateRule(Process):
    """Evaluates the truth value of a climatological impact rule"""

    def __init__(self):
        self.status_percentage_steps = {
            "start": 0,
            "process": 10,
            "build_output": 95,
            "complete": 100,
        }

        inputs = [
            LiteralInput(
                "rules",
                "Rules",
                abstract="Rule expressions",
                min_occurs=1,
                max_occurs=100,
                data_type="string",
            ),
            ComplexInput(
                "parse_tree",
                "Parse Tree Dictionary",
                abstract="File path to dictionary used for rule getter function",
                supported_formats=[FORMATS.JSON],
            ),
            ComplexInput(
                "variables",
                "Variable Dictionary",
                abstract="File path to dictionary used for variables",
                supported_formats=[FORMATS.JSON],
            ),
            log_level,
        ]

        outputs = [json_output]

        super(EvaluateRule, self).__init__(
            self._handler,
            identifier="evaluate_rule",
            title="Evaluate Rule",
            abstract="Evaluate parse trees to determine truth value of a rule",
            keywords=["evaluate", "rule"],
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
        args = collect_args(request, self.workdir)
        rules, parse_tree_path, variables_path, loglevel = (
            args[key][0] if key != "rules" else args[key] for key in args.keys()
        )

        log_handler(
            self,
            response,
            "Starting Process",
            logger,
            log_level=loglevel,
            process_step="start",
        )

        try:
            with open(parse_tree_path) as json_file:
                parse_tree = json.load(json_file)
        except (TypeError, json.JSONDecodeError) as e:
            raise ProcessError(f"{type(e).__name__}: Invalid parse tree file. {e}")

        try:
            with open(variables_path) as json_file:
                collected_variables = json.load(json_file)
        except (TypeError, json.JSONDecodeError) as e:
            raise ProcessError(f"{type(e).__name__}: Invalid variables file. {e}")

        variable_getter = partial(get_dict_val, collected_variables)
        rule_getter = partial(get_dict_val, parse_tree)

        log_handler(
            self,
            response,
            "Evaluating expression",
            logger,
            log_level=loglevel,
            process_step="process",
        )

        try:
            truth_values = {
                rule: evaluate_rule(rule, rule_getter, variable_getter)
                for rule in rules
            }
        except NotImplementedError as e:
            raise ProcessError(
                f"{type(e).__name__}: Unable to process expression "
                "because it contains invalid characters"
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

        filepath = os.path.join(self.workdir, "truth_values.json")
        with open(filepath, "w") as f:
            json.dump(truth_values, f)

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
