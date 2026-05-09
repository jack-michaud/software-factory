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

DENY_PATH_PARTS = {'.env','auth.json','state.db','kanban.db','sessions','memories','logs','local','.ssh'}
DENY_SUBSTRINGS = ['Obsidian Vault','.hermes/kanban','SPRITE_CREDENTIAL','SPRITE_TOKEN','FLY_API_TOKEN','GITHUB_TOKEN','OAUTH_TOKEN','OPENAI_API_KEY','ANTHROPIC_API_KEY','BEGIN OPENSSH PRIVATE KEY','BEGIN RSA PRIVATE KEY','BEGIN PRIVATE KEY']
SECRET_REGEXES = [re.compile(r'(?i)(api[_-]?key|oauth[_-]?token|github[_-]?token)\s*[:=]\s*(?!<placeholder-api-key>|<org>|<repo>)[A-Za-z0-9_./+\-]{12,}'), re.compile(r'-----BEGIN (OPENSSH|RSA|DSA|EC|PRIVATE) KEY-----')]
def scan_dir(base):
    findings=[]; files=0
    for p in sorted(base.rglob('*')):
        if p.is_dir(): continue
        files += 1
        rel=p.relative_to(base).as_posix()
        parts=set(p.relative_to(base).parts)
        if parts & DENY_PATH_PARTS:
            findings.append({'path':rel,'type':'forbidden_path_part','matched':sorted(parts & DENY_PATH_PARTS)})
        try:
            text=p.read_text(errors='ignore')
        except Exception:
            continue
        for sub in DENY_SUBSTRINGS:
            if sub in text:
                findings.append({'path':rel,'type':'forbidden_substring','matched':sub})
        for rx in SECRET_REGEXES:
            m=rx.search(text)
            if m:
                findings.append({'path':rel,'type':'secret_pattern','matched':m.group(0)[:80]})
    return files, findings
def main():
    targets=[ROOT/'profiles', ROOT/'generated']
    all_findings=[]; counts={}
    for target in targets:
        files, findings=scan_dir(target)
        counts[str(target.relative_to(ROOT))]=files
        all_findings.extend([{'target':str(target.relative_to(ROOT)), **f} for f in findings])
    report={'status':'pass' if not all_findings else 'fail','scanned_files':counts,'findings':all_findings,'documented_placeholder_allowlist':['<org>','<repo>','<placeholder-api-key>']}
    (ROOT/'secret-scan-report.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0 if not all_findings else 1
if __name__ == '__main__': sys.exit(main())
