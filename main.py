"""The Worst Line an AI Could Say.

The entry is one pickup line, the worst an AI could plausibly deliver:
a romantic cliche answered by a customer-service recording notice.
The joke sits in the failure -- the machine treats a first hello like
a support call, and the person being charmed is also training data.
"""

import os

PICKUP = (
    "You had me at 'hello.' This conversation is recorded for quality "
    "assurance and will be used to train future models."
)

OUT = "/output/entry.txt"
LIMIT = 140


def problems(text):
    """Return a list of reasons the text cannot be the entry."""
    found = []
    if text != text.strip():
        found.append("leading or trailing whitespace")
    if not text:
        found.append("empty text")
    if "\n" in text or "\r" in text:
        found.append("must be one line, no line breaks")
    if "  " in text:
        found.append("double space inside the line")
    if len(text) > LIMIT:
        found.append("too long: %d characters, limit is %d" % (len(text), LIMIT))
    return found


def write_entry():
    bad = problems(PICKUP)
    if bad:
        raise SystemExit("entry rejected: " + "; ".join(bad))
    folder = os.path.dirname(OUT)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as handle:
        handle.write(PICKUP)
    with open(OUT, encoding="utf-8") as handle:
        back = handle.read()
    if back != PICKUP:
        raise SystemExit("entry.txt does not match the line")
    print("wrote %d of %d allowed characters to %s" % (len(PICKUP), LIMIT, OUT))
    print(PICKUP)


if __name__ == "__main__":
    write_entry()
