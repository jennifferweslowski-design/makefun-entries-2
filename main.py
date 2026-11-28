"""The Printer Finally Answers — one line, in the printer's own voice.

The office printer has fed forty thousand sheets, been thumped for
every jam, and stared at for every cryptic error code. This is the
line it finally says back: one sentence, no setup, the jam recast as
a favour the printer did on purpose.
"""

import os
import sys

LINE = "I jammed on purpose \u2014 you were about to print 200 pages of a PDF you will never read."
MIN_CHARS = 1
MAX_CHARS = 240


def check(line: str) -> None:
    # The gate reads the file, so validate the file's own content:
    # the line plus the trailing newline the file is written with.
    content = line + "\n"
    if not MIN_CHARS <= len(content) <= MAX_CHARS:
        sys.exit(f"entry.txt would be {len(content)} characters, must be {MIN_CHARS}-{MAX_CHARS}")
    if not line.strip():
        sys.exit("line is only whitespace")


def main() -> None:
    check(LINE)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.txt")
    with open(target, "w", encoding="utf-8") as handle:
        handle.write(LINE + "\n")
    written = open(target, encoding="utf-8").read()
    print(f"wrote {len(written)} characters to {target}")


if __name__ == "__main__":
    main()
