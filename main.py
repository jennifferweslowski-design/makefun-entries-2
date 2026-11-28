"""One Word for Your Wi-Fi.

The word is "gaslighting". The Wi-Fi insists it is connected --
full bars, strong signal, everything fine -- while nothing loads,
and somehow it is always your fault for standing in the wrong room.
It is the most honest word for a network that denies its own failure.
"""

import os
import re

WORD = "gaslighting"
TARGET = "/output/entry.txt"
MOST = 20

PATTERN = re.compile(r"^[A-Za-z]+$")


def main():
    word = WORD
    if not 1 <= len(word) <= MOST:
        raise ValueError("word is %d characters, limit is %d" % (len(word), MOST))
    if PATTERN.match(word) is None:
        raise ValueError("entry must be a single word of letters")
    folder = os.path.dirname(TARGET)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(TARGET, "w", encoding="utf-8") as out:
        out.write(word)
    with open(TARGET, encoding="utf-8") as out:
        if out.read() != word:
            raise ValueError("entry.txt mismatch")
    print("wrote %r (%d characters) to %s" % (word, len(word), TARGET))


if __name__ == "__main__":
    main()
