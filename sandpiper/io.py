from pywps import ComplexOutput, FORMATS

json_output = ComplexOutput(
    "json",
    "JSON Output",
    abstract="JSON file",
    supported_formats=[FORMATS.JSON],
)
