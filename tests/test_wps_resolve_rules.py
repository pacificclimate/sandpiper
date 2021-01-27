import pytest
from pkg_resources import resource_filename

from wps_tools.testing import run_wps_process, local_path
from sandpiper.processes.wps_resolve_rules import ResolveRules


@pytest.mark.online
@pytest.mark.parametrize(
    (
        "csv",
        "date_range",
        "region",
        "geoserver",
        "connection_string",
        "ensemble",
        "thredds",
    ),
    [
        (
            resource_filename("tests", "data/rules_small.csv"),
            "2050",
            "vancouver_island",
            "http://docker-dev01.pcic.uvic.ca:30123/geoserver/bc_regions/ows",
            "postgres://ce_meta_ro@db3.pcic.uvic.ca/ce_meta_12f290b63791",
            "p2a_rules",
            "False",
        ),
        (
            resource_filename("tests", "data/rules_small.csv"),
            "2050",
            "vancouver_island",
            "http://docker-dev01.pcic.uvic.ca:30123/geoserver/bc_regions/ows",
            "postgres://ce_meta_ro@db3.pcic.uvic.ca/ce_meta_12f290b63791",
            "p2a_rules",
            "True",
        ),
    ],
)
def test_wps_resolve_rules(
    mock_thredds_url_root,
    csv,
    date_range,
    region,
    geoserver,
    connection_string,
    ensemble,
    thredds,
):
    with open(csv, "r") as csv_file:
        datainputs = (
            f"csv_content={csv_file.read()};"
            f"date_range={date_range};"
            f"region={region};"
            f"geoserver={geoserver};"
            f"connection_string={connection_string};"
            f"ensemble={ensemble};"
            f"thredds={thredds};"
        )
        run_wps_process(ResolveRules(), datainputs)
