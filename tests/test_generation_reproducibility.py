import subprocess, sys
from pathlib import Path

def test_generator_runs():
    root = Path(__file__).resolve().parents[1]
    subprocess.run([sys.executable, str(root/"publisher/scripts/generate_public_repos.py")], check=True)
    assert (root/"generated/hermes-softwarefactorypm-profile/distribution.yaml").exists()
