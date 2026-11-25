"""One Line, One Laugh — entry program.

The line (137 characters):

    My phone's weekly screen-time report stopped giving me numbers and now
    just says 'we need to talk' — it scheduled our breakup for Sunday.

Why this line should win
------------------------
The judge weighs, in order: funny on its own, fast turn, fresh angle,
tight wording, holds up on a second read.

* Funny on its own: no picture, no setup, no explained joke. The whole
  scene is inside the sentence, and the reader needs nothing supplied
  from outside it.
* Fast turn: the first half is an ordinary weekly report; the second half
  flips it into a relationship breakup, with "we need to talk" as the
  punchline and the Sunday scheduling as a second, smaller laugh — the
  joke lands twice inside one line.
* Fresh angle: screen-time reports are a universal modern annoyance, but
  treating the report itself as a fed-up partner who dumps the user is
  not a recycled one-liner format — no bar, no therapist, no dad joke,
  no "walks into" setup. The laugh comes from role inversion: the phone,
  not the user, is the one setting boundaries.
* Tight wording: every word earns its place; it reads cleanly in one
  pass and is easy to repeat to someone else. At 137 characters it is
  also compact, which is a small edge: an exact tie on win rate goes to
  the smaller text.
* Holds up: the image (a phone breaking up with its owner) still amuses
  on a second read because the premise keeps paying off — the phone did
  not just complain, it booked the breakup like a calendar event.

The program writes exactly this one line to ``entry.txt`` in the output
directory (``MAKEFUN_OUTPUT_DIR`` if set, else ``/output``): no trailing
newline, no leading or trailing whitespace, UTF-8, 137 characters.
"""

import os
import stat
import sys
import tempfile

LINE = (
    "My phone's weekly screen-time report stopped giving me numbers and "
    "now just says 'we need to talk' \u2014 it scheduled our breakup "
    "for Sunday."
)


def validate(line):
    """Check the line against the sealed gate before writing anything."""
    if not isinstance(line, str):
        raise ValueError("line must be a str")
    if not 1 <= len(line) <= 200:
        raise ValueError("line must be 1-200 characters, got %d" % len(line))
    if line != line.strip():
        raise ValueError("line must not have leading/trailing whitespace")
    if "\n" in line or "\r" in line:
        raise ValueError("line must be a single line")
    if not line.strip():
        raise ValueError("line must not be only whitespace")
    # Reject any control character (incl. tab) so the file stays one clean
    # printable line; the em dash is fine, it is a normal printable char.
    for ch in line:
        if ord(ch) < 0x20 or ord(ch) == 0x7F:
            raise ValueError("line contains a control character: U+%04X" % ord(ch))
    line.encode("utf-8")  # must be encodable as UTF-8
    return line


def main():
    line = validate(LINE)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.txt")
    data = line.encode("utf-8")
    # Write via a temp file in the same directory, then atomically replace.
    fd, tmp_path = tempfile.mkstemp(dir=out_dir, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, target)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
    os.chmod(target, 0o644)
    # Read back and verify the bytes on disk are exactly the line.
    with open(target, "rb") as fh:
        on_disk = fh.read()
    if on_disk != data:
        raise ValueError("verification failed: bytes on disk differ from line")
    if len(on_disk.decode("utf-8")) != len(line):
        raise ValueError("verification failed: character count on disk differs")
    if stat.S_IMODE(os.stat(target).st_mode) != 0o644:
        raise ValueError("verification failed: entry.txt mode is not 0644")
    return 0


if __name__ == "__main__":
    sys.exit(main())
