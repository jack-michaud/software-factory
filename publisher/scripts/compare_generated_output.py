#!/usr/bin/env python3
from pathlib import Path
import json, sys

from simple_yaml import load_yaml_document

ROOT = Path(__file__).resolve().parents[2]
PUBLIC_REPOS_CONFIG = ROOT/'publisher/config/public-repos.yaml'


def load_yaml(path):
    return load_yaml_document(Path(path).read_text())


def public_repo_entries():
    roles = (load_yaml(PUBLIC_REPOS_CONFIG).get('roles') or {})
    return [{'role': role, 'repo': cfg['repo']} for role, cfg in roles.items()]


def main():
    gen=ROOT/'generated'
    summary=[]
    for entry in public_repo_entries():
        role=entry['role']
        repo=entry['repo']
        path=gen/repo
        if not path.exists():
            summary.append({'repo':repo,'role':role,'file_count':0,'change_classes':['missing generated repo'],'publish_action':'none - dry-run only'})
            continue
        files=[p.relative_to(path).as_posix() for p in sorted(path.rglob('*')) if p.is_file()]
        classes=[]
        if any(f.startswith('skills/') for f in files): classes.append('skill changes')
        if 'SOUL.md' in files: classes.append('SOUL/permission changes')
        if 'distribution.yaml' in files: classes.append('manifest changes')
        if any(f in ['README.md','CHANGELOG.md','LICENSE'] for f in files): classes.append('docs/license changes')
        if any(f.startswith('templates/') for f in files): classes.append('template changes')
        if any(f.startswith('scripts/') for f in files): classes.append('script changes')
        summary.append({'repo':repo,'role':role,'file_count':len(files),'change_classes':classes,'publish_action':'none - dry-run only'})
    out={'status':'dry-run','summary':summary,'note':'No existing public repo worktrees were configured, so this is a generated-output inventory rather than a git diff.'}
    (ROOT/'generated-diff-summary.json').write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
if __name__ == '__main__': main()
