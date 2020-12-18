from pywps import Process, LiteralInput, LiteralOutput, ComplexInput, Format, FORMATS
from pywps.app.Common import Metadata
from functools import partial
import json

from p2a_impacts.fetch_data import get_dict_val
from p2a_impacts.evaluator import evaluate_rule
from wps_tools.utils import log_handler
from wps_tools.io import log_level
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
                "rule", "Rule", abstract="Rule expression", data_type="string",
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
                "truth_value",
                "Truth Value",
                abstract="Truth value of a parse tree",
                data_type="boolean",
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
        loglevel = request.inputs["loglevel"][0].data
        log_handler(
            self,
            response,
            "Starting Process",
            logger,
            log_level=loglevel,
            process_step="start",
        )

        rule = request.inputs["rule"][0].data
        parse_tree_path = request.inputs["parse_tree"][0].file
        variables_path = request.inputs["variables"][0].file

        with open(parse_tree_path) as json_file:
            parse_tree = json.load(json_file)
        with open(variables_path) as json_file:
            collected_variables = json.load(json_file)

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

        truth_value = evaluate_rule(rule, rule_getter, variable_getter)

        log_handler(
            self,
            response,
            "Cleaning and building final output",
            logger,
            log_level=loglevel,
            process_step="build_output",
        )

        response.outputs["truth_value"].data = truth_value

        log_handler(
            self,
            response,
            "Process Complete",
            logger,
            log_level=loglevel,
            process_step="complete",
        )
        return response
