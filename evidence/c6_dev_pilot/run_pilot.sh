cd /private/tmp/claude-501/-Users-new-RiderProjects-ai-RPG-test/a2ba012a-5e55-4b7e-ab29-4f76eb1d2e49/scratchpad
PY=/Users/new/RiderProjects/ai_RPG_test/.venv/bin/python
$PY c6_pilot.py 24 320 9.6 0 pilot_contact.json > pilot_contact.log 2>&1
$PY c6_pilot.py 24 320 9.6 1.0 pilot_disk1.json > pilot_disk1.log 2>&1
echo done
