import pytest
from pkg_resources import resource_filename

from wps_tools.testing import run_wps_process, local_path
from sandpiper.processes.wps_evaluate_rule import EvaluateRule


@pytest.mark.parametrize(
    ("rule", "parse_tree", "variables",),
    [
        (
            "rule_snow",
            local_path("parse_tree.json"),
            local_path("collected_variables.json"),
        ),
    ],
)
def test_wps_evaluate_rule(rule, parse_tree, variables):
    datainputs = (
        f"rule={rule};"
        f"parse_tree=@xlink:href={parse_tree};"
        f"variables=@xlink:href={variables};"
    )
    run_wps_process(EvaluateRule(), datainputs)
