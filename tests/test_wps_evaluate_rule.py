import pytest
from pkg_resources import resource_filename

from wps_tools.testing import run_wps_process
from sandpiper.processes.wps_evaluate_rule import EvaluateRule


@pytest.mark.parametrize(
    ("rule", "parse_tree", "variables",),
    [
        (
            "rule_snow",
            resource_filename("tests", "data/parse_tree.json"),
            resource_filename("tests", "data/collected_variables.json"),
        ),
    ],
)
def test_wps_evaluate_rule(rule, parse_tree, variables):
    datainputs = f"rule={rule};" f"parse_tree={parse_tree};" f"variables={variables};"
    run_wps_process(EvaluateRule(), datainputs)
