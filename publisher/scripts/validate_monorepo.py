#!/usr/bin/env python3
from pathlib import Path
import json, re, shutil, sys, hashlib

from simple_yaml import load_yaml_document

ROOT = Path(__file__).resolve().parents[2]
PUBLIC_REPOS_CONFIG = ROOT/'publisher/config/public-repos.yaml'
PUBLIC_ALLOWLIST_CONFIG = ROOT/'publisher/config/allowlist.yaml'
PROTECTED_PREFIXES = ['sessions/','memories/','logs/','local/','.ssh/','.hermes/kanban/']
DENY_PATH_PARTS = {'.env','auth.json','state.db','kanban.db','sessions','memories','logs','local','.ssh'}
DENY_SUFFIXES = ('.pem','.key','.p12','.pfx')
RUNTIME_ROLES = {'worker'}
COMMON_RUNTIME_REQUIRED = {'skills/devops/software-factory-kanban-workflow/','skills/devops/kanban-worker/','skills/devops/remote-sprite-development/','skills/autonomous-ai-agents/hermes-agent/'}
ROLE_SOUL_CHECKS = {
    'worker': [('software-factory-kanban-workflow', 'SOUL lacks Kanban workflow skill requirement'), ('third failed attempt', 'SOUL lacks bounded retry/escalation language')],
}


def load_yaml(path):
    text = Path(path).read_text()
    return load_yaml_document(text)


def fail(msg, errors):
    errors.append(msg)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def public_repo_entries(errors):
    try:
        data = load_yaml(PUBLIC_REPOS_CONFIG)
    except Exception as e:
        fail(f'public repo config parse failed: {e}', errors)
        return []
    roles = data.get('roles') or {}
    entries = []
    for role, cfg in roles.items():
        if not isinstance(cfg, dict):
            fail(f'public repo config for {role} must be a mapping', errors)
            continue
        repo = cfg.get('repo')
        source_dir = cfg.get('source_dir') or f'profiles/{role}'
        validation_profile = cfg.get('validation_profile') or ('runtime-role' if role in RUNTIME_ROLES else f'{role}-role')
        if not repo:
            fail(f'public repo config for {role} missing repo', errors)
        entries.append({'role': role, 'repo': repo, 'source_dir': source_dir, 'validation_profile': validation_profile, 'config': cfg})
    return entries


def load_allowlist(errors):
    try:
        data = load_yaml(PUBLIC_ALLOWLIST_CONFIG)
    except Exception as e:
        fail(f'allowlist config parse failed: {e}', errors)
        return set(), set()
    return set(data.get('allowed_root_files') or []), set(data.get('allowed_dirs') or [])


def normalized_dir(path):
    return path if path.endswith('/') else f'{path}/'


def rel_is_safe(rel, allowed_root_files, allowed_dirs):
    if rel in {'.','/'} or rel.startswith('/') or '..' in Path(rel).parts:
        return False
    parts = set(Path(rel).parts)
    if parts & DENY_PATH_PARTS:
        return False
    if rel.endswith(DENY_SUFFIXES):
        return False
    if any(rel.startswith(prefix) or rel == prefix.rstrip('/') for prefix in PROTECTED_PREFIXES):
        return False
    if '/' not in rel:
        return rel in allowed_root_files
    return any(rel.startswith(normalized_dir(d)) for d in allowed_dirs)


def validate_source_to_generated_manifest(errors, warnings, repo_entries):
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
    transformed_repos = set()
    expected_repos = {entry['repo'] for entry in repo_entries if entry.get('repo')}
    manifest_repos = {repo.get('repo') for repo in manifest.get('repos') or []}
    if manifest_repos != expected_repos:
        fail(f'manifest generated repos mismatch public-repos.yaml: expected {sorted(expected_repos)}, found {sorted(manifest_repos)}', errors)
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
            repo_name = generated_rel.split('/')[1] if generated_rel.startswith('generated/') else None
            if repo_name:
                transformed_repos.add(repo_name)
            if 'README install docs injected during generation' not in entry.get('transformations', []):
                fail(f'manifest entry {idx}: README transformation missing from manifest for {generated_rel}', errors)
    if transformed_repos != expected_repos:
        fail(f'manifest expected transformed generated README entries for repos {sorted(expected_repos)}, found {sorted(transformed_repos)}', errors)
    return {'status': 'checked', 'hash_fields_checked': checked, 'transformed_readmes': transformed, 'expected_transformed_readmes': len(expected_repos)}


def main():
    errors=[]; warnings=[]; role_results={}
    repo_entries = public_repo_entries(errors)
    allowed_root_files, allowed_dirs = load_allowlist(errors)
    for repo_entry in repo_entries:
        role = repo_entry['role']
        rdir=ROOT/repo_entry['source_dir']
        manifest_path=rdir/'distribution.yaml'
        if not manifest_path.exists(): fail(f'{role}: missing distribution.yaml at {repo_entry["source_dir"]}', errors); continue
        try:
            manifest=load_yaml(manifest_path)
        except Exception as e:
            fail(f'{role}: distribution.yaml parse failed: {e}', errors); continue
        owned=manifest.get('distribution_owned') or []
        if not isinstance(owned, list) or not owned: fail(f'{role}: distribution_owned missing or not list', errors)
        for key in ['name','version']:
            if not manifest.get(key): fail(f'{role}: manifest missing {key}', errors)
        if role in RUNTIME_ROLES:
            for key in ['description','license']:
                if not manifest.get(key): fail(f'{role}: manifest missing {key}', errors)
        source = manifest.get('source', {})
        if isinstance(source, dict):
            source_role = source.get('role')
            generated_repo = source.get('generated_repo')
        else:
            source_role = role if f'  role: {role}' in manifest_path.read_text() else None
            generated_repo = None
        if source_role != role:
            fail(f'{role}: source.role mismatch', errors)
        if generated_repo not in (None, repo_entry['repo']):
            fail(f'{role}: source.generated_repo mismatch: expected {repo_entry["repo"]}, found {generated_repo}', errors)
        for path in owned:
            rel = str(path).rstrip('/')
            if not rel_is_safe(rel, allowed_root_files, allowed_dirs):
                fail(f'{role}: distribution_owned path is unsafe or not public-allowlisted: {path}', errors)
            target=rdir/rel
            if target.is_symlink():
                fail(f'{role}: distribution_owned path is a symlink and cannot be published: {path}', errors)
            if not target.exists(): fail(f'{role}: distribution_owned path missing {path}', errors)
            elif target.is_dir():
                for child in target.rglob('*'):
                    if child.is_symlink():
                        fail(f'{role}: distribution_owned contains symlink that cannot be published: {child.relative_to(rdir).as_posix()}', errors)
                    elif child.is_file() and not rel_is_safe(child.relative_to(rdir).as_posix(), allowed_root_files, allowed_dirs):
                        fail(f'{role}: distribution_owned file is unsafe or not public-allowlisted: {child.relative_to(rdir).as_posix()}', errors)
        if role in RUNTIME_ROLES:
            missing_common=sorted(COMMON_RUNTIME_REQUIRED-set([p for p in owned]))
            if missing_common: fail(f'{role}: missing common owned skills {missing_common}', errors)
        soul=(rdir/'SOUL.md').read_text() if (rdir/'SOUL.md').exists() else ''
        for token, message in ROLE_SOUL_CHECKS.get(role, []):
            if token not in soul:
                fail(f'{role}: {message}', errors)
        role_results[role]={'manifest':str(manifest_path),'owned_count':len(owned),'repo':repo_entry['repo'],'validation_profile':repo_entry['validation_profile']}
    # Validate public/private policy files are present and name both allowed public
    # shapes and forbidden private/runtime state.
    policy_files = [ROOT/'publisher/config/allowlist.yaml', ROOT/'publisher/config/denylist.yaml', ROOT/'publisher/config/public-repos.yaml']
    for policy in policy_files:
        if not policy.exists():
            fail(f'missing policy file {policy.relative_to(ROOT)}', errors)
    allow_text = (ROOT/'publisher/config/allowlist.yaml').read_text() if (ROOT/'publisher/config/allowlist.yaml').exists() else ''
    deny_text = (ROOT/'publisher/config/denylist.yaml').read_text() if (ROOT/'publisher/config/denylist.yaml').exists() else ''
    for token in ['distribution.yaml','SOUL.md','README.md','skills/','templates/','scripts/']:
        if token not in allow_text:
            fail(f'allowlist missing {token}', errors)
    for token in ['.env','auth.json','state.db','sessions/','memories/','logs/','local/','kanban.db']:
        if token not in deny_text:
            fail(f'denylist missing {token}', errors)
    # If generated output exists, validate current-Hermes remote-install shape and
    # README install docs. Generation may be run before or after this validator.
    gen = ROOT/'generated'
    generated_results = {}
    if gen.exists():
        for repo_entry in repo_entries:
            role = repo_entry['role']
            repo = repo_entry['repo']
            gdir = gen/repo
            if not gdir.exists():
                fail(f'generated repo missing for {role}: {repo}', errors); continue
            if not (gdir/'distribution.yaml').exists():
                fail(f'{repo}: missing root distribution.yaml', errors)
            readme = (gdir/'README.md').read_text() if (gdir/'README.md').exists() else ''
            if f'hermes profile install https://github.com/<org>/{repo}.git' not in readme:
                fail(f'{repo}: README missing generated public install command', errors)
            for p in gdir.rglob('*'):
                if p.is_symlink():
                    fail(f'{repo}: generated symlink not allowed: {p.relative_to(gdir).as_posix()}', errors)
                elif p.is_file():
                    rel = p.relative_to(gdir).as_posix()
                    if not rel_is_safe(rel, allowed_root_files, allowed_dirs) and rel != 'GENERATED_METADATA.json':
                        fail(f'{repo}: generated file not public-allowlisted: {rel}', errors)
            generated_results[role] = {'repo': repo, 'path': str(gdir), 'root_distribution_yaml': (gdir/'distribution.yaml').exists()}
    else:
        generated_results = 'not generated yet'
    manifest_validation = validate_source_to_generated_manifest(errors, warnings, repo_entries)
    out={'status':'pass' if not errors else 'fail','errors':errors,'warnings':warnings,'roles':role_results,'generated':generated_results,'source_to_generated_manifest':manifest_validation}
    report=ROOT/'validation-report.json'; report.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    return 0 if not errors else 1
if __name__ == '__main__': sys.exit(main())
