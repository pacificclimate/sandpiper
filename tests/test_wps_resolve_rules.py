import pytest
from importlib.resources import files

from wps_tools.testing import run_wps_process
from sandpiper.processes.wps_resolve_rules import ResolveRules


@pytest.mark.online
@pytest.mark.parametrize(
    (
        "csv",
        "date_range",
        "region",
        "geoserver",
        "ensemble",
    ),
    [
        (
            str((files("tests") / "data/rules_small.csv").resolve()),
            "2050",
            "vancouver_island",
            "https://beehive.pacificclimate.org/plan2adapt/bc_regions/ows",
            "p2a_rules",
        ),
    ],
)
@pytest.mark.parametrize("thredds", [True, False])
def test_wps_resolve_rules(
    mock_thredds_url_root,
    csv,
    date_range,
    region,
    geoserver,
    ensemble,
    thredds,
):
    with open(csv, "r") as csv_file:
        datainputs = (
            f"csv={csv_file.read()};"
            f"date_range={date_range};"
            f"region={region};"
            f"geoserver={geoserver};"
            f"ensemble={ensemble};"
            f"thredds={thredds};"
        )
        run_wps_process(ResolveRules(), datainputs)
