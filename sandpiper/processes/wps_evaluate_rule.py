from pywps import Process, LiteralInput, LiteralOutput, ComplexInput, FORMATS
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError
from functools import partial
import json

from p2a_impacts.fetch_data import get_dict_val
from p2a_impacts.evaluator import evaluate_rule
from wps_tools.logging import log_handler
from wps_tools.io import log_level, collect_args
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
                "rule",
                "Rule",
                abstract="Rule expression",
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

        outputs = [
            LiteralOutput(
                "truth_values",
                "Truth Value Dictionary",
                abstract="Truth value of a parse tree for each rule",
                data_type="string",
            ),
        ]

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
        rules, parse_tree_path, variables_path, loglevel = collect_args(
            request, self.workdir
        ).values()

        log_handler(
            self,
            response,
            "Starting Process",
            logger,
            log_level=loglevel[0],
            process_step="start",
        )

        try:
            with open(parse_tree_path[0]) as json_file:
                parse_tree = json.load(json_file)
        except (TypeError, json.JSONDecodeError) as e:
            raise ProcessError(f"{type(e).__name__}: Invalid parse tree file. {e}")

        try:
            with open(variables_path[0]) as json_file:
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
            log_level=loglevel[0],
            process_step="process",
        )
        truth_values = {}

        for rule in rules:
            try:
                truth_value = evaluate_rule(rule, rule_getter, variable_getter)
                truth_values[rule] = truth_value
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
            log_level=loglevel[0],
            process_step="build_output",
        )

        response.outputs["truth_values"].data = truth_values

        log_handler(
            self,
            response,
            "Process Complete",
            logger,
            log_level=loglevel[0],
            process_step="complete",
        )
        return response
