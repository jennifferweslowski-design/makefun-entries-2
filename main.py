"""One Word From Your Ex.

The word is "almost". It is the word an ex reaches for when the
truth is too long: almost the one, almost enough, almost stayed.
Six letters, no blame, no anger -- just the gap between what was
and what was supposed to be. Painfully honest, and it stings
because everyone has been an "almost" to somebody.
"""

import os
import sys

WORD = "almost"
OUT_PATH = "/output/entry.txt"
CHAR_LIMIT = 24


def fail(message):
    print("invalid entry: " + message, file=sys.stderr)
    raise SystemExit(1)


def main():
    if len(WORD) == 0:
        fail("the word is empty")
    if len(WORD) > CHAR_LIMIT:
        fail("the word is %d characters, over the %d limit" % (len(WORD), CHAR_LIMIT))
    if len(WORD.split()) != 1:
        fail("the entry must be one word, not a phrase")
    if not WORD.isalpha():
        fail("the word must be letters only")
    if WORD != WORD.strip():
        fail("the word has surrounding whitespace")
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as handle:
        handle.write(WORD)
    with open(OUT_PATH, encoding="utf-8") as handle:
        written = handle.read()
    if written != WORD:
        fail("entry.txt does not match the word")
    print("entry %r is %d characters" % (WORD, len(WORD)))


if __name__ == "__main__":
    main()
