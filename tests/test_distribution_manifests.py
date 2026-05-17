from pathlib import Path


def test_role_manifests_exist():
    root = Path(__file__).resolve().parents[1]
    for role in ["worker"]:
        assert (root / "profiles" / role / "distribution.yaml").exists()
