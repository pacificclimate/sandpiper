from .wps_resolve_rules import ResolveRules
from .wps_parser import Parser
from .wps_evaluate_rules import EvaluateRule

processes = [
    ResolveRules(),
    Parser(),
    EvaluateRule(),
]
