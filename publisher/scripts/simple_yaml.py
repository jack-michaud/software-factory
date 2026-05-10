"""Small dependency-free YAML reader for the publisher's simple config files.

This is intentionally narrow. It supports the source-controlled shapes used by
publisher config and profile distribution manifests: nested mappings, lists of
scalars, and lists of mappings with scalar values. Prefer PyYAML when available;
use this fallback so validation/generation stay reproducible in a bare Python 3
review runtime.
"""

from __future__ import annotations


def _strip_inline_comment(value: str) -> str:
    in_single = False
    in_double = False
    for idx, ch in enumerate(value):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            if idx == 0 or value[idx - 1].isspace():
                return value[:idx].rstrip()
    return value.strip()


def _parse_scalar(value: str):
    value = _strip_inline_comment(value)
    if value == "":
        return ""
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "None", "~"}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def load_simple_yaml(text: str) -> dict:
    root = {}
    stack = [(-1, root)]

    for lineno, raw in enumerate(text.splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if indent % 2:
            raise ValueError(f"line {lineno}: indentation must use multiples of two spaces")
        line = raw.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise ValueError(f"line {lineno}: invalid indentation")
        parent = stack[-1][1]

        if line.startswith("- "):
            if not isinstance(parent, list):
                raise ValueError(f"line {lineno}: list item without list parent")
            item = line[2:].strip()
            if ":" in item:
                key, value = item.split(":", 1)
                mapping = {}
                key = key.strip()
                value = value.strip()
                mapping[key] = _parse_scalar(value) if value else {}
                parent.append(mapping)
                stack.append((indent, mapping))
                if value == "":
                    stack.append((indent + 2, mapping[key]))
            else:
                parent.append(_parse_scalar(item))
            continue

        if ":" not in line:
            raise ValueError(f"line {lineno}: expected key: value")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not isinstance(parent, dict):
            raise ValueError(f"line {lineno}: mapping entry without mapping parent")
        if value:
            parent[key] = _parse_scalar(value)
        else:
            # The next indented non-empty line decides whether this is a list or
            # mapping. Source manifests only use two-space indentation.
            child = [] if _next_content_line_starts_list(text, raw) else {}
            parent[key] = child
            stack.append((indent, child))

    return root


def _next_content_line_starts_list(text: str, current_raw: str) -> bool:
    lines = text.splitlines()
    try:
        start = lines.index(current_raw) + 1
    except ValueError:
        return False
    current_indent = len(current_raw) - len(current_raw.lstrip(" "))
    for nxt in lines[start:]:
        if not nxt.strip() or nxt.lstrip().startswith("#"):
            continue
        indent = len(nxt) - len(nxt.lstrip(" "))
        return indent > current_indent and nxt.strip().startswith("- ")
    return False


def load_yaml_document(text: str) -> dict:
    try:
        import yaml  # type: ignore
    except Exception:
        yaml = None
    if yaml:
        return yaml.safe_load(text) or {}
    return load_simple_yaml(text)
