import pytest

from wps_tools.testing import run_wps_process
from sandpiper.processes.wps_parser import Parser

# Any logical conditions with "=" do not work in this test for some unknown reason
@pytest.mark.parametrize(
    ("condition"), ["(temp_djf_iamean_s100p_hist < 5)",],
)
def test_wps_parser(condition):
    datainput = f"condition={condition};"
    run_wps_process(Parser(), datainput)
