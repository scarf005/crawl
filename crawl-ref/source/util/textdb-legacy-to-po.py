#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

from textdb_gettext import iter_english_entries, load_legacy_entries, msgctxt, source_root, syntax_comments, write_entry, write_header


def write_language_catalog(lang: str, output_dir: Path) -> None:
    root = source_root()
    legacy_entries = load_legacy_entries(lang, root)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{lang}.po"
    with tempfile.TemporaryDirectory() as temp_dir:
        bootstrap_path = Path(temp_dir) / f"{lang}.po"
        with bootstrap_path.open("w", encoding="utf-8") as handle:
            write_header(handle, lang)
            for spec, path, key, english_body in iter_english_entries(root):
                translated_body = legacy_entries.get((spec.name, key))
                if not translated_body or translated_body == english_body:
                    continue

                write_entry(
                    handle,
                    comments=[f"key: {key}", *syntax_comments(english_body)],
                    refs=[path.relative_to(root).as_posix()],
                    context=msgctxt(spec, key),
                    msgid_text=english_body,
                    msgstr_text=translated_body,
                )

        if output_path.exists():
            subprocess.run([
                "msgcat",
                "--use-first",
                str(bootstrap_path),
                str(output_path),
                "-o",
                str(output_path),
            ], check=True)
        else:
            shutil.move(str(bootstrap_path), str(output_path))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bootstrap gettext catalogs from legacy TextDB translations",
    )
    parser.add_argument("languages", nargs="+", help="language codes to convert")
    parser.add_argument(
        "--output-dir",
        default="po",
        help="directory for generated PO files, relative to source/",
    )
    args = parser.parse_args()

    output_dir = source_root() / args.output_dir
    for lang in args.languages:
        write_language_catalog(lang, output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
