import pytest
from tempfile import NamedTemporaryFile

from wps_tools.testing import run_wps_process, local_path, process_err_test
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


@pytest.mark.parametrize(
    ("rule", "parse_tree",), [("rule_snow", local_path("parse_tree.json"),),],
)
def test_file_err(rule, parse_tree):
    with NamedTemporaryFile(
        suffix=".json", prefix="tmp_copy", dir="/tmp", delete=True
    ) as var_file:
        datainputs = (
            f"rule={rule};"
            f"parse_tree=@xlink:href={parse_tree};"
            f"variables={var_file.name};"
        )
        process_err_test(EvaluateRule, datainputs)


@pytest.mark.parametrize(
    ("rule", "parse_tree", "variables",),
    [
        (
            "rule_snow",
            local_path("invalid_parse_tree.json"),
            local_path("collected_variables.json"),
        ),
    ],
)
def test_parse_string_err(rule, parse_tree, variables):
    datainputs = (
        f"rule={rule};"
        f"parse_tree=@xlink:href={parse_tree};"
        f"variables=@xlink:href={variables};"
    )
    process_err_test(EvaluateRule, datainputs)
