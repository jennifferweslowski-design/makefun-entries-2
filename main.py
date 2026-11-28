"""The Moon Finally Answers Back.

One line in the Moon's voice, answering at last. The setup is the
Moon's long patience -- four billion years of wishes, howls and
3 a.m. promises -- and the answer is the Moon refusing the job
everyone gave it: it is a rock, not a therapist.
"""

from pathlib import Path

MOON_LINE = (
    "Four billion years of wishes, howls, and 3 a.m. promises, "
    "and my answer is this: I am a rock, not a therapist."
)

DESTINATION = Path("/output/entry.txt")
UPPER = 240
LOWER = 1


def check(line):
    if len(line) < LOWER:
        raise ValueError("line is empty")
    if len(line) > UPPER:
        raise ValueError("line is %d characters, over the %d limit" % (len(line), UPPER))
    if line.strip() != line:
        raise ValueError("line has leading or trailing whitespace")
    if "  " in line:
        raise ValueError("line has a double space")
    if line[-1] not in ".!?":
        raise ValueError("line should end on terminal punctuation")
    for bad in ("\n", "\r", "\t"):
        if bad in line:
            raise ValueError("line must be a single line of text")


def main():
    check(MOON_LINE)
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    DESTINATION.write_text(MOON_LINE, encoding="utf-8")
    again = DESTINATION.read_text(encoding="utf-8")
    assert again == MOON_LINE, "entry.txt round-trip failed"
    print("Moon line: %d characters (limit %d)" % (len(MOON_LINE), UPPER))
    print(MOON_LINE)


if __name__ == "__main__":
    main()
