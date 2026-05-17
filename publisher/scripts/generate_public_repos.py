#!/usr/bin/env python3
from pathlib import Path
import json, shutil, sys, hashlib

from simple_yaml import load_yaml_document

ROOT = Path(__file__).resolve().parents[2]
PUBLIC_REPOS_CONFIG = ROOT/'publisher/config/public-repos.yaml'
PUBLIC_ALLOWLIST_CONFIG = ROOT/'publisher/config/allowlist.yaml'
PROTECTED_PREFIXES = ['sessions/','memories/','logs/','local/','.ssh/','.hermes/kanban/']
DENY_PATH_PARTS = {'.env','auth.json','state.db','kanban.db','sessions','memories','logs','local','.ssh'}
DENY_SUFFIXES = ('.pem','.key','.p12','.pfx')


def load_yaml(path):
    text = Path(path).read_text()
    return load_yaml_document(text)


def public_repo_entries():
    data = load_yaml(PUBLIC_REPOS_CONFIG)
    roles = data.get('roles') or {}
    entries = []
    for role, cfg in roles.items():
        if not isinstance(cfg, dict):
            raise RuntimeError(f'public repo config for {role} must be a mapping')
        repo = cfg.get('repo')
        source_dir = cfg.get('source_dir') or f'profiles/{role}'
        if not repo:
            raise RuntimeError(f'public repo config for {role} missing repo')
        entries.append({'role': role, 'repo': repo, 'source_dir': source_dir, 'config': cfg})
    return entries


def load_allowlist():
    data = load_yaml(PUBLIC_ALLOWLIST_CONFIG)
    root_files = set(data.get('allowed_root_files') or [])
    dirs = set(data.get('allowed_dirs') or [])
    return root_files, dirs


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


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


def iter_distribution_owned_files(src, allowed_root_files, allowed_dirs):
    manifest = load_yaml(src/'distribution.yaml')
    owned = manifest.get('distribution_owned') or []
    if not isinstance(owned, list) or not owned:
        raise RuntimeError(f'{src.relative_to(ROOT)} distribution_owned missing or not list')
    # Some existing runtime profiles do not list distribution.yaml in
    # distribution_owned even though generated public repos must be installable
    # from their repository root. Include safe root files that exist, then the
    # role-owned inventory.
    candidates = [name for name in allowed_root_files if (src/name).is_file() and name != 'GENERATED_METADATA.json']
    candidates.extend(owned)
    seen = set()
    for item in candidates:
        rel = str(item).rstrip('/')
        if not rel_is_safe(rel, allowed_root_files, allowed_dirs):
            raise RuntimeError(f'{src.relative_to(ROOT)} distribution_owned path is not public-allowlisted: {item}')
        path = src/rel
        if path.is_symlink():
            raise RuntimeError(f'{src.relative_to(ROOT)} distribution_owned path is a symlink and cannot be published: {item}')
        if not path.exists():
            raise RuntimeError(f'{src.relative_to(ROOT)} distribution_owned path missing: {item}')
        if path.is_file():
            files = [path]
        else:
            files = []
            for p in sorted(path.rglob('*')):
                if p.is_symlink():
                    raise RuntimeError(f'{src.relative_to(ROOT)} symlink cannot be published: {p.relative_to(src).as_posix()}')
                if p.is_file():
                    files.append(p)
        for p in files:
            file_rel = p.relative_to(src).as_posix()
            if not rel_is_safe(file_rel, allowed_root_files, allowed_dirs):
                raise RuntimeError(f'{src.relative_to(ROOT)} file is not public-allowlisted: {file_rel}')
            if file_rel not in seen:
                seen.add(file_rel)
                yield p


def manifest_entry(src, target, transformations=None):
    source_rel = str(src.relative_to(ROOT))
    generated_rel = str(target.relative_to(ROOT))
    source_hash = sha256(src)
    generated_hash = sha256(target)
    entry = {
        'source': source_rel,
        'generated': generated_rel,
        # sha256 always refers to the generated file content. source_sha256
        # is recorded separately so transformed files cannot be confused with
        # byte-for-byte copies.
        'sha256': generated_hash,
        'generated_sha256': generated_hash,
        'source_sha256': source_hash,
    }
    if transformations:
        entry['transformations'] = transformations
        entry['content_relation'] = 'transformed_from_source'
    else:
        entry['content_relation'] = 'copied_verbatim'
    return entry


def copy_distribution_owned(src, dst, manifest_entries, allowed_root_files, allowed_dirs):
    for p in iter_distribution_owned_files(src, allowed_root_files, allowed_dirs):
        rel = p.relative_to(src).as_posix()
        target = dst/rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)
        manifest_entries.append(manifest_entry(p, target))


def update_manifest_entry(entries, generated_rel, replacement):
    for idx, entry in enumerate(entries):
        if entry.get('generated') == generated_rel:
            entries[idx] = replacement
            return
    entries.append(replacement)


def main():
    gen=ROOT/'generated'
    if gen.exists(): shutil.rmtree(gen)
    gen.mkdir()
    source_manifest=[]; repos=[]
    allowed_root_files, allowed_dirs = load_allowlist()
    entries_config = public_repo_entries()
    for repo_entry in entries_config:
        role = repo_entry['role']
        repo = repo_entry['repo']
        install_name = repo_entry['config'].get('install_name') or f'softwarefactory{role}'
        src = ROOT/repo_entry['source_dir']
        if not src.exists():
            raise RuntimeError(f'{role}: source_dir missing: {repo_entry["source_dir"]}')
        dst=gen/repo
        dst.mkdir(parents=True)
        entries=[]
        copy_distribution_owned(src,dst,entries,allowed_root_files,allowed_dirs)
        readme=dst/'README.md'
        if not readme.exists():
            raise RuntimeError(f'{role}: README.md is required for generated install guidance')
        readme.write_text(readme.read_text()+f"\n## Generated public repository shape\n\nThis root is current-Hermes-compatible: `distribution.yaml` is at repository root.\n\nInstall after publication:\n\n```bash\nhermes profile install https://github.com/<org>/{repo}.git --name {install_name}\n```\n\nUpdate after publication:\n\n```bash\nhermes profile update {install_name} --yes\n```\n\nPublic/private boundary: credentials, runtime state, logs, memories, sessions, Kanban DB/workspaces, sprite credentials, SSH keys, OAuth tokens, API keys, and private Obsidian notes are not included. Profile `.env` files are user-owned and are not overwritten by distribution updates; declare expected variables in `distribution.yaml` `env_requires` and document non-secret examples in README/install guidance.\n", encoding='utf-8')
        readme_entry = manifest_entry(
            src/'README.md',
            readme,
            transformations=['README install docs injected during generation'],
        )
        update_manifest_entry(entries, f'generated/{repo}/README.md', readme_entry)
        meta={'role':role,'repo':repo,'source_dir':repo_entry['source_dir'],'dry_run_only':True,'requires_human_approval_to_publish':True}
        (dst/'GENERATED_METADATA.json').write_text(json.dumps(meta, indent=2))
        source_manifest.extend(entries)
        source_manifest.append({
            'source': 'publisher/scripts/generate_public_repos.py',
            'generated': f'generated/{repo}/README.md',
            'note': 'README install docs injected during generation',
            'content_relation': 'generator_mutation',
        })
        repos.append({'role':role,'repo':repo,'path':str(dst),'files':len([p for p in dst.rglob('*') if p.is_file()])})
    manifest={'generated_root':str(gen),'repos':repos,'source_to_generated':source_manifest}
    (ROOT/'source-to-generated-manifest.json').write_text(json.dumps(manifest, indent=2))
    approval={'mode':'dry-run','publish_performed':False,'github_repos_created':False,'credentials_required':False,'human_approval_required_for_publish':True,'generated_repos':[r['repo'] for r in repos]}
    (ROOT/'dry-run-publish-approval-artifact.json').write_text(json.dumps(approval, indent=2))
    print(json.dumps(manifest, indent=2))
if __name__ == '__main__': main()
