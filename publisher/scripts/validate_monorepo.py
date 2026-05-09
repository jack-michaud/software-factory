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

def fail(msg, errors):
    errors.append(msg)

def validate_source_to_generated_manifest(errors, warnings):
    manifest_path = ROOT/'source-to-generated-manifest.json'
    if not manifest_path.exists():
        warnings.append('source-to-generated-manifest.json not present; run generator to validate generated hashes')
        return {'status': 'not_present'}
    try:
        manifest = json.loads(manifest_path.read_text())
    except Exception as e:
        fail(f'source-to-generated-manifest.json parse failed: {e}', errors)
        return {'status': 'parse_failed'}
    checked = 0
    transformed = 0
    for idx, entry in enumerate(manifest.get('source_to_generated') or []):
        generated_rel = entry.get('generated')
        if not generated_rel:
            fail(f'manifest entry {idx}: missing generated path', errors)
            continue
        generated_path = ROOT/generated_rel
        if not generated_path.exists():
            fail(f'manifest entry {idx}: generated path missing: {generated_rel}', errors)
            continue
        generated_hash = sha256(generated_path)
        for field in ['sha256', 'generated_sha256']:
            if field in entry:
                checked += 1
                if entry[field] != generated_hash:
                    fail(f'manifest entry {idx}: {field} mismatch for {generated_rel}: expected generated file hash {generated_hash}, found {entry[field]}', errors)
        if 'sha256' not in entry and 'generated_sha256' not in entry:
            # Some provenance-only entries intentionally describe generator mutations
            # rather than a full source->file copy. They must say so explicitly.
            if entry.get('content_relation') != 'generator_mutation':
                fail(f'manifest entry {idx}: no generated hash field for {generated_rel}', errors)
        source_rel = entry.get('source')
        if source_rel and 'source_sha256' in entry:
            source_path = ROOT/source_rel
            if not source_path.exists():
                fail(f'manifest entry {idx}: source path missing: {source_rel}', errors)
            else:
                source_hash = sha256(source_path)
                if entry['source_sha256'] != source_hash:
                    fail(f'manifest entry {idx}: source_sha256 mismatch for {source_rel}: expected {source_hash}, found {entry["source_sha256"]}', errors)
        if generated_rel.endswith('/README.md') and entry.get('source', '').endswith('/README.md'):
            transformed += 1
            if 'README install docs injected during generation' not in entry.get('transformations', []):
                fail(f'manifest entry {idx}: README transformation missing from manifest for {generated_rel}', errors)
    if transformed != len(ROLES):
        fail(f'manifest expected {len(ROLES)} transformed generated README entries, found {transformed}', errors)
    return {'status': 'checked', 'hash_fields_checked': checked, 'transformed_readmes': transformed}
def main():
    errors=[]; warnings=[]; role_results={}
    protected_prefixes = ['sessions/','memories/','logs/','local/','.ssh/','.hermes/kanban/']
    common_required = {'skills/devops/software-factory/','skills/devops/kanban-worker/','skills/devops/kanban-profile-workflow/','skills/autonomous-ai-agents/hermes-agent/'}
    for role in ROLES:
        rdir=ROOT/'profiles'/role
        manifest_path=rdir/'distribution.yaml'
        if not manifest_path.exists(): fail(f'{role}: missing distribution.yaml', errors); continue
        try:
            manifest=load_yaml(manifest_path)
        except Exception as e:
            fail(f'{role}: distribution.yaml parse failed: {e}', errors); continue
        owned=manifest.get('distribution_owned') or []
        if not isinstance(owned, list) or not owned: fail(f'{role}: distribution_owned missing or not list', errors)
        for key in ['name','version','description','license']:
            if not manifest.get(key): fail(f'{role}: manifest missing {key}', errors)
        source = manifest.get('source', {})
        if isinstance(source, dict):
            source_role = source.get('role')
        else:
            # Minimal YAML fallback used when PyYAML is unavailable cannot parse nested mappings;
            # verify source.role directly from manifest text in that case.
            source_role = role if f'  role: {role}' in manifest_path.read_text() else None
        if source_role != role:
            fail(f'{role}: source.role mismatch', errors)
        for path in owned:
            if path in ['.','/'] or path.startswith('/') or '..' in Path(path).parts:
                fail(f'{role}: non-explicit or unsafe distribution_owned path {path}', errors)
            if any(path.startswith(p) or path == p.rstrip('/') for p in protected_prefixes):
                fail(f'{role}: distribution_owned includes protected runtime path {path}', errors)
            target=rdir/path.rstrip('/')
            if not target.exists(): fail(f'{role}: distribution_owned path missing {path}', errors)
        missing_common=sorted(common_required-set([p for p in owned]))
        if missing_common: fail(f'{role}: missing common owned skills {missing_common}', errors)
        soul=(rdir/'SOUL.md').read_text() if (rdir/'SOUL.md').exists() else ''
        if role in ['pm','orchestrator','reviewer'] and 'must not run sprite' not in soul:
            fail(f'{role}: SOUL lacks no-sprite-mutation language', errors)
        if role == 'builder' and 'checkpoint before and after' not in soul:
            fail('builder: SOUL lacks checkpoint/mutation ownership language', errors)
        if role == 'publisher' and ('explicit human approval' not in soul or 'must not mutate sprites' not in soul):
            fail('publisher: SOUL lacks approval/no-sprite language', errors)
        role_results[role]={'manifest':str(manifest_path),'owned_count':len(owned),'repo':REPO_NAMES[role]}
    # Validate public/private policy files are present and name both allowed public
    # shapes and forbidden private/runtime state.
    policy_files = [ROOT/'publisher/config/allowlist.yaml', ROOT/'publisher/config/denylist.yaml', ROOT/'publisher/config/public-repos.yaml']
    for policy in policy_files:
        if not policy.exists():
            fail(f'missing policy file {policy.relative_to(ROOT)}', errors)
    allow_text = (ROOT/'publisher/config/allowlist.yaml').read_text() if (ROOT/'publisher/config/allowlist.yaml').exists() else ''
    deny_text = (ROOT/'publisher/config/denylist.yaml').read_text() if (ROOT/'publisher/config/denylist.yaml').exists() else ''
    for token in ['distribution.yaml','SOUL.md','README.md','skills/']:
        if token not in allow_text:
            fail(f'allowlist missing {token}', errors)
    for token in ['.env','auth.json','state.db','sessions/','memories/','logs/','local/','kanban.db']:
        if token not in deny_text:
            fail(f'denylist missing {token}', errors)
    # If generated output exists, validate current-Hermes remote-install shape and
    # README install docs. Generation may be run before or after this validator.
    gen = ROOT/'generated'
    generated_results = {}
    allowed_root = {'distribution.yaml','SOUL.md','README.md','LICENSE','CHANGELOG.md','GENERATED_METADATA.json'}
    if gen.exists():
        for role in ROLES:
            repo = REPO_NAMES[role]
            gdir = gen/repo
            if not gdir.exists():
                fail(f'generated repo missing for {role}: {repo}', errors); continue
            if not (gdir/'distribution.yaml').exists():
                fail(f'{repo}: missing root distribution.yaml', errors)
            readme = (gdir/'README.md').read_text() if (gdir/'README.md').exists() else ''
            if f'hermes profile install https://github.com/<org>/{repo}.git' not in readme:
                fail(f'{repo}: README missing generated public install command', errors)
            for p in gdir.rglob('*'):
                if p.is_file():
                    rel = p.relative_to(gdir).as_posix()
                    if '/' not in rel and rel not in allowed_root:
                        fail(f'{repo}: root file not allowlisted: {rel}', errors)
                    if '/' in rel and not rel.startswith('skills/'):
                        fail(f'{repo}: nested path not allowlisted: {rel}', errors)
            generated_results[role] = {'repo': repo, 'path': str(gdir), 'root_distribution_yaml': (gdir/'distribution.yaml').exists()}
    else:
        generated_results = 'not generated yet'
    manifest_validation = validate_source_to_generated_manifest(errors, warnings)
    out={'status':'pass' if not errors else 'fail','errors':errors,'warnings':warnings,'roles':role_results,'generated':generated_results,'source_to_generated_manifest':manifest_validation}
    report=ROOT/'validation-report.json'; report.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    return 0 if not errors else 1
if __name__ == '__main__': sys.exit(main())
