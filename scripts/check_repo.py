"""Check candidate Git files and README links. This is not a secret scanner."""
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
raw = subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'], cwd=ROOT)
paths = sorted(set(raw.decode().split('\0')) - {''})
errors = []
for name in paths:
    path = Path(name)
    lower = name.lower()
    if (any(part in {'.venv','node_modules','.data','__pycache__','.aws','.gcp'} for part in path.parts)
        or (path.name.startswith('.env') and path.name != '.env.example')
        or re.search(r'\.(?:db|sqlite3?)(?:-(?:wal|shm|journal))?$', lower)
        or path.suffix.lower() in {'.pem','.key','.p12','.pfx','.pyc'}
        or lower.endswith('.json') and any(x in lower for x in ('credentials','service-account','service_account','contextos-evidence'))):
        errors.append(f'Private/runtime file is a Git candidate: {name}')

for link in re.findall(r'\]\(([^)]+)\)', (ROOT/'README.md').read_text()):
    target = link.split('#',1)[0]
    if not target or re.match(r'^[a-zA-Z]+:', target):
        continue
    if not (ROOT / unquote(target)).exists():
        errors.append(f'Broken README target: {target}')

for required in ('README.md','.gitignore','CONTRIBUTING.md','SECURITY.md','.github/workflows/ci.yml','handoff.md','features.md','requirements.md','design/architecture.md'):
    if not (ROOT/required).is_file():
        errors.append(f'Missing repository file: {required}')

if errors:
    print('\n'.join(errors),file=sys.stderr)
    raise SystemExit(1)
print(f'PASS: {len(paths)} Git candidate files checked; README local links and required repository files exist.')
print('This checks paths and documentation links only; manually review content and Git history before publication.')
