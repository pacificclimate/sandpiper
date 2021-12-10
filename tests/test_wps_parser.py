import pytest

from wps_tools.testing import run_wps_process, process_err_test
from sandpiper.processes.wps_parser import Parser


def build_condition_input(conditions):
    if isinstance(conditions, str):  # Single input
        return f"conditions={conditions};"
    else:
        conditions_input = ""
        for condition in conditions:
            conditions_input += f"conditions={condition};"
        return conditions_input


# Any logical conditions with "=" do not work in this test for some unknown reason
@pytest.mark.parametrize(
    ("conditions"),
    [
        [
            "(temp_djf_iamean_s100p_hist < 5)",
            "(temp_djf_iamean_s0p_hist < -6)",
            "(temp_djf_iamean_s0p_hist < -6) %26%26 (temp_djf_iamean_s100p_hist > -6)",
        ]
    ],
)
def test_wps_parser(conditions):
    datainput = build_condition_input(conditions)
    run_wps_process(Parser(), datainput)


@pytest.mark.parametrize(
    ("conditions"),
    [
        "(temp_djf_iamean_s100p_hist $ 5)",
        "temp_djf_iamean_s100p_hist > 5)",
        "(temp_djf_iamean_s100p > 5)",
    ],
)
def test_wps_parser_err(conditions):
    datainput = build_condition_input(conditions)
    process_err_test(Parser, datainput)
