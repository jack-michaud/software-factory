from pathlib import Path

def test_no_runtime_dirs_in_profiles():
    root = Path(__file__).resolve().parents[1] / "profiles"
    forbidden = {"sessions", "memories", "logs", "local", ".ssh"}
    for p in root.rglob("*"):
        assert not (set(p.parts) & forbidden)
