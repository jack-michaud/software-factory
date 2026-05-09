#!/usr/bin/env python3
from pathlib import Path
import json, re, shutil, sys, hashlib
try:
    import yaml
except Exception:
    yaml = None
ROOT = Path(__file__).resolve().parents[2]
ROLES = ['pm','builder','orchestrator','reviewer','publisher']
REPO_NAMES = {'pm':'hermes-softwarefactorypm-profile','builder':'hermes-softwarefactorybuilder-profile','orchestrator':'hermes-softwarefactoryorchestrator-profile','reviewer':'hermes-softwarefactoryreviewer-profile','publisher':'hermes-softwarefactorypublisher-profile'}
def load_yaml(path):
    text = Path(path).read_text()
    if yaml:
        return yaml.safe_load(text)
    # minimal fallback for this prototype only
    data = {}
    cur = None
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith('#'): continue
        if line.startswith('  - ') and cur:
            data.setdefault(cur, []).append(line[4:].strip().strip('"\''))
        elif ':' in line and not line.startswith(' '):
            k,v=line.split(':',1); cur=k.strip(); data[cur]=v.strip() or []
    return data
def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    gen=ROOT/'generated'
    summary=[]
    for role in ROLES:
        repo=REPO_NAMES[role]
        path=gen/repo
        files=[p.relative_to(path).as_posix() for p in sorted(path.rglob('*')) if p.is_file()]
        classes=[]
        if any(f.startswith('skills/') for f in files): classes.append('skill changes')
        if 'SOUL.md' in files: classes.append('SOUL/permission changes')
        if 'distribution.yaml' in files: classes.append('manifest changes')
        if any(f in ['README.md','CHANGELOG.md','LICENSE'] for f in files): classes.append('docs/license changes')
        summary.append({'repo':repo,'role':role,'file_count':len(files),'change_classes':classes,'publish_action':'none - dry-run only'})
    out={'status':'dry-run','summary':summary,'note':'No existing public repo worktrees were configured, so this is a generated-output inventory rather than a git diff.'}
    (ROOT/'generated-diff-summary.json').write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
if __name__ == '__main__': main()
