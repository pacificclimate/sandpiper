import logging
import os
from pywps.app.exceptions import ProcessError


logger = logging.getLogger("PYWPS")
logger.setLevel(logging.NOTSET)

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s: sandpiper: %(message)s", "%Y-%m-%d %H:%M:%S"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


def update_connection(connection_string):
    """Updates the conenction string after args collection

    The connection string can be set as a parameter in the bird OR as an
    environment variable. This method ensures that we check both options with
    priority given to the parameter.
    """
    connection_string = (
        connection_string
        if connection_string != ""
        else os.environ.get("CONNECTION_STRING")
    )

    if not connection_string:
        raise ProcessError(
            f"No connection_string found. You must set the connection_string through the environment or as a parameter."
        )

    return connection_string
