#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core_i18n_strings import CORE_STRINGS
from webserver.webtiles.i18n_strings import WEBTILES_STRINGS
from textdb_gettext import iter_english_entries, msgctxt, source_root, syntax_comments, write_entry, write_header


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate crawl-data gettext POT")
    parser.add_argument("--output", "-o", help="output POT path")
    args = parser.parse_args()

    output = open(args.output, "w", encoding="utf-8") if args.output else sys.stdout
    try:
        write_header(output, "")
        root = source_root()
        for spec, path, key, body in iter_english_entries(root):
            write_entry(
                output,
                comments=[f"key: {key}", *syntax_comments(body)],
                refs=[path.relative_to(root).as_posix()],
                context=msgctxt(spec, key),
                msgid_text=body,
                msgstr_text="",
            )

        for entry in CORE_STRINGS:
            comments = []
            if entry.comment:
                comments.append(entry.comment)
            write_entry(
                output,
                comments=comments,
                refs=[entry.path],
                context=entry.context,
                msgid_text=entry.msgid,
                msgstr_text="",
            )

        for entry in WEBTILES_STRINGS:
            comments = []
            if entry.comment:
                comments.append(entry.comment)
            write_entry(
                output,
                comments=comments,
                refs=[entry.path],
                context="webtiles:" + entry.context,
                msgid_text=entry.msgid,
                msgstr_text="",
            )
    finally:
        if args.output:
            output.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
