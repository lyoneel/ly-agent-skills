#!/usr/bin/env python3
"""Shared constant loader for tg-notipy.

Reads assets/constant-limits.md and assets/constant-filetypes.md, the
single source of truth for fixed values. The script and the agent read
the same files; nothing re-declares a value owned by a constant file.

CLI:
    python3 scripts/tg_constants.py --dump limits|filetypes|all
"""

import argparse
import json
import os
import re
import sys

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(SKILL_ROOT, "assets")

FENCED_BLOCK = re.compile(r"^```text$([^`]*)^```$", re.MULTILINE | re.DOTALL)
KV_LINE = re.compile(r"^([^:\s][^:]*):\s*(.+?)\s*$")


def _read_constant_text(name):
    path = os.path.join(ASSETS_DIR, "constant-%s.md" % name)
    if not os.path.isfile(path):
        raise SystemExit("constant file missing: %s" % path)
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def read_constant_blocks(name):
    """Return every fenced text block in assets/constant-<name>.md
    as a list of non-empty, non-comment lines."""
    blocks = []
    for match in FENCED_BLOCK.finditer(_read_constant_text(name)):
        lines = [line.strip() for line in match.group(1).splitlines()]
        lines = [line for line in lines if line and not line.startswith("#")]
        blocks.append(lines)
    if not blocks:
        raise SystemExit("no fenced text blocks in constant file: %s" % name)
    return blocks


def _parse_kv(lines, filename):
    values = {}
    for line in lines:
        match = KV_LINE.match(line)
        if not match:
            raise SystemExit("malformed line in %s: %r" % (filename, line))
        key, raw = match.group(1), match.group(2)
        try:
            value = int(raw)
        except ValueError:
            try:
                value = float(raw)
            except ValueError:
                value = raw
        values[key] = value
    return values


def load_limits():
    """Return the limits dict with int/float values."""
    blocks = read_constant_blocks("limits")
    if len(blocks) != 1:
        raise SystemExit("constant-limits.md must hold exactly one block")
    limits = _parse_kv(blocks[0], "constant-limits.md")
    for key in ("message_max_chars", "caption_max_chars", "photo_upload_max_mb",
                "other_upload_max_mb", "self_hosted_upload_max_mb",
                "backoff_cap_seconds", "default_retries",
                "default_base_wait_seconds", "album_min_items",
                "album_max_items", "rate_limit_messages_per_second"):
        if key not in limits:
            raise SystemExit("constant-limits.md misses key: %s" % key)
    return limits


def load_filetypes():
    """Return (ext_to_type, mime_to_type) dicts."""
    blocks = read_constant_blocks("filetypes")
    if len(blocks) != 2:
        raise SystemExit(
            "constant-filetypes.md must hold exactly two blocks "
            "(extension map, MIME map)")
    return (_parse_kv(blocks[0], "constant-filetypes.md"),
            _parse_kv(blocks[1], "constant-filetypes.md"))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="tg_constants",
                                     description="dump tg-notipy constants")
    parser.add_argument("--dump", required=True,
                        choices=["limits", "filetypes", "all"],
                        help="which constant set to print as JSON")
    opts = parser.parse_args(argv)
    out = {}
    if opts.dump in ("limits", "all"):
        out["limits"] = load_limits()
    if opts.dump in ("filetypes", "all"):
        ext_map, mime_map = load_filetypes()
        out["filetypes"] = {"extensions": ext_map, "mime": mime_map}
    print(json.dumps(out, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
