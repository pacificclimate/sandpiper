from .wps_resolve_rules import ResolveRules
from .wps_parser import Parser

processes = [
    ResolveRules(),
    Parser(),
]
