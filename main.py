"""One Word for the Boss.

The word is "delegation". It is the whole job description: the boss
does not do the work, the boss distributes it, and somehow that
counts as leadership. One word, funny because it is true, and true
because everyone who has had a boss has watched it happen.
"""

WORD = "delegation"
DEST = "/output/entry.txt"
LIMIT = 30


def is_one_word(text):
    parts = text.split()
    return len(parts) == 1 and parts[0] == text


def main():
    if not is_one_word(WORD):
        raise SystemExit("entry must be exactly one word")
    if len(WORD) < 1 or len(WORD) > LIMIT:
        raise SystemExit("word is %d characters, limit is %d" % (len(WORD), LIMIT))
    if not WORD.isalpha():
        raise SystemExit("word must be letters only")
    if WORD != WORD.lower():
        raise SystemExit("word must be lowercase, not a sentence start")
    import os

    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, "w", encoding="utf-8") as f:
        f.write(WORD)
    with open(DEST, encoding="utf-8") as f:
        back = f.read()
    if back != WORD:
        raise SystemExit("entry.txt does not match the word")
    print("%s (%d characters) -> %s" % (WORD, len(WORD), DEST))


if __name__ == "__main__":
    main()
