"""Explicit grants with committed approval-record identity and start snapshots."""
from dataclasses import dataclass,field
from copy import deepcopy
import hashlib
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[4]


def approval_record(reference):
    path=Path(reference)
    if path.is_absolute() or '..' in path.parts:raise PermissionError('approval must be a repository-relative committed record path')
    if path.parts[:2]!=('docs','decisions') or path.suffix!='.md':raise PermissionError('approval must name an owner-decision Markdown record in docs/decisions')
    target=(ROOT/path).resolve()
    if ROOT not in target.parents or not target.is_file():raise PermissionError('approval record does not exist')
    committed=subprocess.run(['git','show',f'HEAD:{path.as_posix()}'],cwd=ROOT,capture_output=True)
    if committed.returncode or committed.stdout!=target.read_bytes():
        raise PermissionError('approval record must match an existing committed file at HEAD')
    return dict(path=path.as_posix(),sha256=hashlib.sha256(committed.stdout).hexdigest(),
                commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())


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
    _approval: dict=field(default_factory=dict,init=False,repr=False,compare=False)
    _snapshots: dict=field(default_factory=dict,init=False,repr=False,compare=False)

    def __post_init__(self):
        if self.approval_reference:object.__setattr__(self,'_approval',approval_record(self.approval_reference))

    def require(self,scope):
        if scope not in ('fixtures','development'):raise ValueError('unknown execution scope')
        common=self.owner_revision and self.engines_ready_reviewed and self.integration_tested_reviewed and self.source_units_endpoints_ready and bool(self._approval)
        allowed=common and (self.owner_fixtures if scope=='fixtures' else self.owner_development and self.fixtures_passed)
        if not allowed:raise PermissionError(f'{scope} requires separate owner approval, reviewed readiness and applicable prior gates')

    def start(self,scope):
        self.require(scope)
        from .rev6_identity import assert_inputs
        self._snapshots[scope]=dict(assert_inputs(),approval_record=deepcopy(self._approval))
        return deepcopy(self._snapshots[scope])

    def snapshot(self,scope):
        self.require(scope)
        if scope not in self._snapshots:self.start(scope)
        return deepcopy(self._snapshots[scope])
