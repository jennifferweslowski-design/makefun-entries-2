"""One Emoji, One Dream Vacation.

The emoji is the beach with umbrella. One glyph holds the whole
trip: sand, sea, shade, and nowhere to be. It is the vacation a
stranger pictures the moment they see it, and the one they would
book a flight for.
"""

EMOJI = "\U0001f3d6\ufe0f"
OUTFILE = "/output/entry.txt"
MOST_CHARS = 8
VARIATION = "\ufe0f"


def single_emoji(text):
    """True when the text is one emoji, allowing a variation selector."""
    core = text.replace(VARIATION, "")
    if len(core) != 1:
        return False
    point = ord(core)
    return point >= 0x1F000 or 0x2600 <= point <= 0x27BF


def main():
    if not 1 <= len(EMOJI) <= MOST_CHARS:
        raise SystemExit("emoji is %d characters, limit is %d" % (len(EMOJI), MOST_CHARS))
    if EMOJI.strip() != EMOJI:
        raise SystemExit("emoji has surrounding whitespace")
    if not single_emoji(EMOJI):
        raise SystemExit("entry is not a single emoji")
    import os

    os.makedirs(os.path.dirname(OUTFILE), exist_ok=True)
    with open(OUTFILE, "w", encoding="utf-8") as handle:
        handle.write(EMOJI)
    with open(OUTFILE, "rb") as handle:
        raw = handle.read()
    if raw.decode("utf-8") != EMOJI:
        raise SystemExit("entry.txt does not match the emoji")
    if raw.endswith(b"\n") or raw.endswith(b"\r"):
        raise SystemExit("entry.txt must not end with a newline")
    print("wrote %d characters (%d bytes) to %s" % (len(EMOJI), len(raw), OUTFILE))
    print(EMOJI)


if __name__ == "__main__":
    main()
