import logging
import io
import pytest
from contextlib import redirect_stderr

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
