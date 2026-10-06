"""Revision-7 execution gate. No fixture execution before Claude implementation review."""
from dataclasses import dataclass,field
from pathlib import Path
from copy import deepcopy
import hashlib
import json
from .rev6_execution import approval_record
from .rev7_identity import HERE,assert_inputs

@dataclass(frozen=True)
class Execution:
    engines_ready_reviewed:bool=False
    integration_tested_reviewed:bool=False
    fixtures_passed:bool=False
    owner_development:bool=False
    approval_reference:str='docs/decisions/0031-owner-run-approval-policy.md'
    integration_review: str=''
    fixture_receipt: str=''
    receipt_dir: str=''
    _snapshots:dict=field(default_factory=dict,init=False,repr=False,compare=False)

    def require(self,scope):
        if scope not in ('fixtures','development'):raise ValueError('unknown execution scope')
        if scope in self._snapshots:return
        if not self.engines_ready_reviewed or not self.integration_tested_reviewed or not self.integration_review:raise PermissionError('revision-7 integration/dependencies must be implemented, tested and reviewed')
        review=Path(self.integration_review)
        text=review.read_text()
        if text.splitlines()[0] not in ('APPROVE','APPROVE_WITH_NOTES','READY_FOR_FIXTURES') or 'Reviewer family: Claude' not in text:raise PermissionError('passing Claude implementation review required')
        pin_digest=hashlib.sha256((HERE/'REV7_SOURCE_IDENTITY.json').read_bytes()).hexdigest()
        if f'Reviewed execution-pin SHA256: {pin_digest}' not in text:raise PermissionError('Claude review does not bind the current execution pin')
        if not self.receipt_dir:raise PermissionError('pre-execution receipt directory required')
        approval=approval_record(self.approval_reference)
        if '0030' in approval['path']:raise PermissionError('0030 covers only revision 6.5')
        if scope=='development':
            if not self.fixtures_passed or not self.owner_development:raise PermissionError('development requires passing fixtures and applicable owner approval')
            validate_fixture_receipt(self.fixture_receipt,pin_digest)

    def start(self,scope):
        self.require(scope)
        if scope in self._snapshots:raise PermissionError('execution already started; no repeated fixture run')
        directory=Path(self.receipt_dir).resolve()
        if HERE.parent not in directory.parents:raise ValueError('execution receipts must stay within growing_shapes')
        directory.mkdir(parents=True,exist_ok=True)
        inventory_path=directory/'PRE_EXECUTION_SEED_INVENTORY.json'
        if inventory_path.exists():raise PermissionError('existing execution receipt; never overwrite or rerun')
        identity=assert_inputs()
        review=Path(self.integration_review)
        report=HERE/'REV7_INTEGRATION_REPORT.md'
        if report.read_text().splitlines()[0]!='READY_FOR_REVIEW':raise PermissionError('integration NOT_READY')
        checks=json.loads((HERE/'REV7_SYNTHETIC_CHECKS.json').read_text())
        if checks['status']!='PASS':raise PermissionError('synthetic tests not passing')
        if checks.get('scientific_input_sha256')!=identity['sha256'] or checks.get('execution_pin_sha256')!=identity['pin_sha256']:raise PermissionError('synthetic receipt does not bind tested scientific bytes')
        if scope=='development':identity['fixture_receipt']=validate_fixture_receipt(self.fixture_receipt,identity['pin_sha256'])
        identity.update(approval_record=approval_record(self.approval_reference),review_sha256=hashlib.sha256(review.read_bytes()).hexdigest())
        data=json.dumps(identity['inventory'],sort_keys=True,indent=2,allow_nan=False)+'\n'
        with inventory_path.open('x') as stream:stream.write(data)
        with (directory/'START_IDENTITY.json').open('x') as stream:stream.write(json.dumps(identity,sort_keys=True,indent=2,allow_nan=False)+'\n')
        self._snapshots[scope]=identity
        return deepcopy(identity)

    def snapshot(self,scope):
        self.require(scope)
        if scope not in self._snapshots:raise PermissionError('call execution.start before any result')
        return deepcopy(self._snapshots[scope])


def validate_fixture_receipt(reference,pin_digest):
    if not reference:raise PermissionError('revision-7 fixture receipt required for development')
    path=Path(reference)
    if not path.is_file():raise PermissionError('fixture receipt missing')
    value=json.loads(path.read_text())
    if value.get('revision')!='7.4' or value.get('identity_snapshot',{}).get('pin_sha256')!=pin_digest:raise PermissionError('fixture receipt revision/execution pin mismatch')
    results=value.get('results',{})
    if set(results)!=set(('N1','F1','F2','F3','F4','F5','F6','F7','F8','F9')) or value.get('not_run') or value.get('stops'):raise PermissionError('fixture sequence incomplete or stopped')
    expected={name:'DESCRIPTIVE' if name in ('F6','F8','F9') else 'PASS' for name in results}
    if any(not isinstance(row,dict) or row.get('verdict')!=expected[name] for name,row in results.items()):raise PermissionError('fixture receipt contains FAIL/INVALID or missing stage measurement')
    return dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
