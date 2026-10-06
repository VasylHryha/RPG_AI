"""Explicit run prerequisites. Unit contracts/construct-only checks need no grant."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Execution:
    owner_revision: bool=False
    owner_fixtures: bool=False
    owner_development: bool=False
    engines_ready_reviewed: bool=False
    integration_tested_reviewed: bool=False
    fixtures_passed: bool=False
    source_units_endpoints_ready: bool=False
    approval_reference: str=''

    def require(self,scope):
        if scope not in ('fixtures','development'):raise ValueError('unknown execution scope')
        common=self.owner_revision and self.engines_ready_reviewed and self.integration_tested_reviewed and self.source_units_endpoints_ready and bool(self.approval_reference)
        allowed=common and (self.owner_fixtures if scope=='fixtures' else self.owner_development and self.fixtures_passed)
        if not allowed:raise PermissionError(f'{scope} requires separate owner approval, reviewed readiness and applicable prior gates')
