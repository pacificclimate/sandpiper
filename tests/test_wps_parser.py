import pytest

from wps_tools.testing import run_wps_process
from sandpiper.processes.wps_parser import Parser
from sandpiper.utils import process_err_test


# Any logical conditions with "=" do not work in this test for some unknown reason
@pytest.mark.parametrize(
    ("condition"), ["(temp_djf_iamean_s100p_hist < 5)",],
)
def test_wps_parser(condition):
    datainput = f"condition={condition};"
    run_wps_process(Parser(), datainput)


@pytest.mark.parametrize(
    ("condition"), ["(temp_djf_iamean_s100p_hist $ 5)",],
)
def test_wps_parser_char_err(condition):
    datainput = f"condition={condition};"
    process_err_test(Parser, datainput)


@pytest.mark.parametrize(
    ("condition"), ["temp_djf_iamean_s100p_hist > 5)",],
)
def test_wps_parser_syntax_err(condition):
    datainput = f"condition={condition};"
    process_err_test(Parser, datainput)


@pytest.mark.parametrize(
    ("condition"), ["(temp_djf_iamean_s100p > 5)",],
)
def test_wps_parser_var_name_err(condition):
    datainput = f"condition={condition};"
    process_err_test(Parser, datainput)
