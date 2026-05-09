#!/usr/bin/env python3
from pathlib import Path
import json, shutil, sys, hashlib
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

def allowed(rel):
    return rel in {'distribution.yaml','SOUL.md','README.md','LICENSE','CHANGELOG.md'} or rel.startswith('skills/')

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

def copy_tree(src, dst, manifest_entries):
    for p in sorted(src.rglob('*')):
        if p.is_dir(): continue
        rel=p.relative_to(src).as_posix()
        if not allowed(rel): continue
        target=dst/rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p,target)
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
    for role in ROLES:
        repo=REPO_NAMES[role]
        src=ROOT/'profiles'/role
        dst=gen/repo
        dst.mkdir(parents=True)
        entries=[]
        copy_tree(src,dst,entries)
        readme=dst/'README.md'
        readme.write_text(readme.read_text()+f"\n## Generated public repository shape\n\nThis root is current-Hermes-compatible: `distribution.yaml` is at repository root.\n\nInstall after publication:\n\n```bash\nhermes profile install https://github.com/<org>/{repo}.git --name softwarefactory{role}\n```\n\nUpdate after publication:\n\n```bash\nhermes profile update softwarefactory{role} --yes\n```\n\nPublic/private boundary: credentials, runtime state, logs, memories, sessions, Kanban DB/workspaces, sprite credentials, SSH keys, OAuth tokens, API keys, and private Obsidian notes are not included.\n", encoding='utf-8')
        readme_entry = manifest_entry(
            src/'README.md',
            readme,
            transformations=['README install docs injected during generation'],
        )
        update_manifest_entry(entries, f'generated/{repo}/README.md', readme_entry)
        meta={'role':role,'repo':repo,'source_dir':f'profiles/{role}','dry_run_only':True,'requires_human_approval_to_publish':True}
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
