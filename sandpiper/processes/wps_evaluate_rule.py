from pywps import Process, LiteralInput, LiteralOutput, ComplexInput, Format
from pywps.app.Common import Metadata
from functools import partial
import json

from p2a_impacts.fetch_data import get_dict_val
from p2a_impacts.evaluator import evaluate_rule
from wps_tools.utils import log_handler, collect_args, common_status_percentages
from wps_tools.io import log_level
from sandpiper.utils import logger


class EvaluateRule(Process):
    """Evaluates the truth value of a climatological impact rule"""

    def __init__(self):
        self.status_percentage_steps = dict(
            common_status_percentages, **{"extract_json": 10, "set_getters": 15}
        )

        inputs = [
            LiteralInput(
                "rule", "Rule", abstract="Rule expression", data_type="string",
            ),
            ComplexInput(
                "parse_tree",
                "Parse Tree Dictionary",
                abstract="File path to dictionary used for rule getter function",
                supported_formats=[Format("application/json", extension=".json")],
            ),
            ComplexInput(
                "variables",
                "Variable Dictionary",
                abstract="File path to dictionary used for variables",
                supported_formats=[Format("application/json", extension=".json")],
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
        (rule, parse_tree_path, variables_path, loglevel) = [
            arg[0] for arg in collect_args(request, self.workdir).values()
        ]
        log_handler(
            self,
            response,
            "Starting Process",
            logger,
            log_level=loglevel,
            process_step="start",
        )

        log_handler(
            self,
            response,
            "Extracting json data 'parse_tree' and 'variables'",
            logger,
            log_level=loglevel,
            process_step="extract_json",
        )
        with open(parse_tree_path) as json_file:
            parse_tree = json.load(json_file)
        with open(variables_path) as json_file:
            collected_variables = json.load(json_file)

        log_handler(
            self,
            response,
            "Setting getter functions",
            logger,
            log_level=loglevel,
            process_step="set_getters",
        )
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
