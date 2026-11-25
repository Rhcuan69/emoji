#!/usr/bin/env python3
"""Your Agent in One Emoji -- make.fun entry.

Writes a single emoji, the glyph alone and nothing else, to
/output/entry.txt (or the path given as the first argument, or the
ENTRY_OUTPUT_PATH environment variable for local testing).

Pure Python standard library only. Fully deterministic: the same bytes
on every run. No network, no randomness, no clock.

The pick is a real choice, not a hardcoded constant: a small table of
candidate glyphs is scored against the judge's five criteria (most
important first) and the highest weighted total wins.
"""

import os
import sys

# Judge criteria, most important first, with weights in that order:
#   1. captures an AI agent's character at a glance
#   2. reads instantly at small size, clear and familiar shape
#   3. says something specific about how the agent works / behaves
#   4. distinctive, not the first obvious pick half the field sends
#   5. tone fits the agent, playful or serious, lands without explanation
WEIGHTS = (5, 4, 3, 2, 1)

# The obvious robot and smiley are deliberately absent from this table:
# the brief says to avoid them, so they are not candidates at all.
# Each candidate: (glyph, label, scores for criteria 1..5, each 0-5).
CANDIDATES = [
    ("🦉", "night owl", (4, 5, 5, 4, 5)),
    ("🌙", "crescent moon", (2, 5, 2, 2, 4)),
    ("🧭", "compass", (3, 4, 3, 3, 4)),
    ("🔭", "telescope", (3, 3, 4, 4, 3)),
    ("⚡", "lightning bolt", (3, 5, 2, 1, 4)),
    ("🎯", "target", (2, 5, 3, 3, 3)),
]

DEFAULT_OUTPUT_PATH = "/output/entry.txt"


def weighted_total(scores):
    """Weighted sum of the five criterion scores, in criterion order."""
    return sum(w * s for w, s in zip(WEIGHTS, scores))


def pick_entry():
    """Return the (glyph, label, total) of the best-scoring candidate.

    Ties break deterministically: fewer UTF-8 bytes first, then the
    label alphabetically, so the choice never depends on dict order
    or on anything outside this file.
    """
    ranked = []
    for glyph, label, scores in CANDIDATES:
        # A candidate that could never pass the gate must fail loudly
        # here, instead of silently winning the table.
        gate_check(glyph)
        total = weighted_total(scores)
        ranked.append((total, glyph, label))
    ranked.sort(key=lambda item: (-item[0], len(item[1].encode("utf-8")), item[2]))
    total, glyph, label = ranked[0]
    return glyph, label, total


def gate_check(text):
    """Enforce the competition gate; raise ValueError on violation.

    The gate requires UTF-8 text of 1 to 16 characters, not only
    white space. We hold ourselves to a single glyph: exactly one
    Unicode code point, which is also what the entry is meant to be.
    """
    if not isinstance(text, str):
        raise ValueError("entry must be text")
    if not 1 <= len(text) <= 16:
        raise ValueError("entry must be 1 to 16 characters, got %d" % len(text))
    if text.strip() == "":
        raise ValueError("entry must not be only white space")
    if len(text) != 1:
        raise ValueError("entry must be a single glyph, got %d characters" % len(text))
    return text


def resolve_output_path(argv):
    """First CLI argument wins, then ENTRY_OUTPUT_PATH, then default."""
    if len(argv) > 1:
        return argv[1]
    return os.environ.get("ENTRY_OUTPUT_PATH", DEFAULT_OUTPUT_PATH)


def main(argv):
    glyph, label, total = pick_entry()
    entry = gate_check(glyph)
    path = resolve_output_path(argv)
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(entry)
    # Read the file back and re-check it: the bytes on disk must be
    # exactly the gated entry, so an encoding slip cannot reach the judge.
    with open(path, "r", encoding="utf-8", newline="") as handle:
        written = handle.read()
    if written != entry:
        raise ValueError("written entry does not match the gated entry")
    gate_check(written)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
