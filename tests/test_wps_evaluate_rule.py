import pytest
from tempfile import NamedTemporaryFile

from wps_tools.testing import run_wps_process, local_path, process_err_test
from sandpiper.processes.wps_evaluate_rule import EvaluateRule


def build_rule_input(rules):
    if isinstance(rules, str):  # Single input
        return f"rules={rules};"
    else:
        rule_input = ""
        for rule in rules:
            rule_input += f"rules={rule};"
        return rule_input


@pytest.mark.parametrize(
    ("rules", "parse_tree", "variables",),
    [
        (
            "rule_snow",
            local_path("parse_tree.json"),
            local_path("collected_variables.json"),
        ),
        (
            ["rule_snow", "rule_rain", "rule_hybrid"],
            local_path("parse_tree.json"),
            local_path("collected_variables.json"),
        ),
    ],
)
def test_wps_evaluate_rule(rules, parse_tree, variables):
    datainputs = (
        # rewrite to accept list (see quail)
        f"{build_rule_input(rules)}"
        f"parse_tree=@xlink:href={parse_tree};"
        f"variables=@xlink:href={variables};"
    )
    run_wps_process(EvaluateRule(), datainputs)


@pytest.mark.parametrize(
    ("rules", "parse_tree",), [("rule_snow", local_path("parse_tree.json"))],
)
def test_file_err(rules, parse_tree):
    with NamedTemporaryFile(
        suffix=".json", prefix="tmp_copy", dir="/tmp", delete=True
    ) as var_file:
        datainputs = (
            f"{build_rule_input(rules)}"
            f"parse_tree=@xlink:href={parse_tree};"
            f"variables={var_file.name};"
        )
        process_err_test(EvaluateRule, datainputs)


@pytest.mark.parametrize(
    ("rules", "parse_tree", "variables",),
    [
        (
            "rule_snow",
            local_path("invalid_parse_tree.json"),
            local_path("collected_variables.json"),
        ),
    ],
)
def test_parse_string_err(rules, parse_tree, variables):
    datainputs = (
        f"{build_rule_input(rules)}"
        f"parse_tree=@xlink:href={parse_tree};"
        f"variables=@xlink:href={variables};"
    )
    process_err_test(EvaluateRule, datainputs)
