import logging
import io
import re
import pytest
from contextlib import redirect_stderr
from pywps.app.exceptions import ProcessError

from wps_tools.testing import run_wps_process


logger = logging.getLogger("PYWPS")
logger.setLevel(logging.NOTSET)

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s: sandpiper: %(message)s", "%Y-%m-%d %H:%M:%S"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


def process_err_test(process, datainputs):
    err = io.StringIO()
    with redirect_stderr(err), pytest.raises(Exception):
        run_wps_process(process(), datainputs)
    assert "pywps.app.exceptions.ProcessError" in err.getvalue()
    err.close()


def custom_process_error(err):
    """ProcessError from pywps only allows a limited list of valid chars
    in custom msgs or it reverts to it's default msg. By matching the end
    of a msg only and removing the '()' brackets and ' quote we can show
    some of the original error message to the user"""
    err_match = re.compile(r"[^:\n].*$").findall(str(err))
    err_msg = err_match[0].replace("(", "").replace(")", "").replace("'", "")
    raise ProcessError(f"{type(err).__name__}: {err_msg}")
