import io
import pytest
from contextlib import redirect_stderr

from wps_tools.testing import run_wps_process


def process_err_test(process, datainputs):
    err = io.StringIO()
    with redirect_stderr(err):
        with pytest.raises(Exception):
            run_wps_process(process(), datainputs)
    print(err.getvalue())
    assert "pywps.app.exceptions.ProcessError" in err.getvalue()
