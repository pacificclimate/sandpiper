import pytest
from pkg_resources import resource_filename

from wps_tools.testing import run_wps_process
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
        "log_level",
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
            "INFO",
        ),
        (
            resource_filename("tests", "data/rules_small.csv"),
            "2050",
            "vancouver_island",
            "http://docker-dev01.pcic.uvic.ca:30123/geoserver/bc_regions/ows",
            "postgres://ce_meta_ro@db3.pcic.uvic.ca/ce_meta_12f290b63791",
            "p2a_rules",
            "True",
            "INFO",
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
    log_level,
):
    datainputs = (
        f"csv={csv};"
        f"date_range={date_range};"
        f"region={region};"
        f"geoserver={geoserver};"
        f"connection_string={connection_string};"
        f"ensemble={ensemble};"
        f"thredds={thredds};"
        f"log_level={log_level};"
    )
    run_wps_process(ResolveRules(), datainputs)
