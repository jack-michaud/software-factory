import hashlib
import json
import subprocess
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_manifest_hashes_generated_files_after_readme_transformations():
    root = Path(__file__).resolve().parents[1]
    subprocess.run([sys.executable, str(root / "publisher/scripts/generate_public_repos.py")], check=True)

    manifest = json.loads((root / "source-to-generated-manifest.json").read_text())
    entries = manifest["source_to_generated"]

    readme_entries = [
        entry for entry in entries
        if entry["generated"].endswith("/README.md") and entry.get("source", "").endswith("/README.md")
    ]
    assert len(readme_entries) == 6

    for entry in entries:
        generated = root / entry["generated"]
        assert generated.exists(), entry
        if "sha256" in entry:
            assert entry.get("sha256") == sha256(generated), entry
        if "generated_sha256" in entry:
            assert entry.get("generated_sha256") == sha256(generated), entry
        if "sha256" not in entry and "generated_sha256" not in entry:
            assert entry.get("content_relation") == "generator_mutation", entry
        if "source" in entry and "source_sha256" in entry:
            source = root / entry["source"]
            assert source.exists(), entry
            assert entry.get("source_sha256") == sha256(source), entry

    for entry in readme_entries:
        readme = (root / entry["generated"]).read_text()
        assert "Generated public repository shape" in readme
        assert "README install docs injected during generation" in entry.get("transformations", [])
        assert entry["sha256"] != entry["source_sha256"]
