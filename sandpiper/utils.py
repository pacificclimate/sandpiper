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
