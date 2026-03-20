#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class TextDbSpec:
    name: str
    directory: str
    files: tuple[str, ...]


TEXTDB_SPECS = (
    TextDbSpec(
        name="descriptions",
        directory="dat/descript",
        files=(
            "features.txt",
            "items.txt",
            "unident.txt",
            "unrand.txt",
            "monsters.txt",
            "spells.txt",
            "gods.txt",
            "branches.txt",
            "skills.txt",
            "ability.txt",
            "cards.txt",
            "commands.txt",
            "clouds.txt",
            "status.txt",
            "monstatus.txt",
            "mutations.txt",
            "passives.txt",
        ),
    ),
    TextDbSpec(
        name="gamestart",
        directory="dat/descript",
        files=("species.txt", "backgrounds.txt"),
    ),
    TextDbSpec(
        name="help",
        directory="dat/database",
        files=("help.txt",),
    ),
    TextDbSpec(
        name="FAQ",
        directory="dat/database",
        files=("FAQ.txt",),
    ),
    TextDbSpec(
        name="hints",
        directory="dat/descript",
        files=("hints.txt", "tutorial.txt"),
    ),
    TextDbSpec(
        name="egos",
        directory="dat/descript",
        files=("egos.txt",),
    ),
)


def source_root() -> Path:
    return Path(__file__).resolve().parent.parent


def msgctxt(spec: TextDbSpec, key: str) -> str:
    return f"textdb:{spec.name}:{key}"


def parse_text_db(path: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    key = None
    value_lines: list[str] = []
    in_entry = False

    with path.open(encoding="utf-8") as handle:
        for raw_line in handle.read().splitlines():
            if raw_line.startswith("#"):
                continue

            if raw_line.startswith("%%%%"):
                if key:
                    entries.append((key, "".join(value_lines).lstrip("\n")))
                key = None
                value_lines = []
                in_entry = True
                continue

            if not in_entry:
                continue

            if key is None:
                key = raw_line.strip().lower()
            else:
                value_lines.append(raw_line.rstrip(" \t\n\r") + "\n")

    if key:
        entries.append((key, "".join(value_lines).lstrip("\n")))

    return entries


def iter_english_entries(
    root: Path | None = None,
) -> Iterable[tuple[TextDbSpec, Path, str, str]]:
    root = root or source_root()
    for spec in TEXTDB_SPECS:
        for filename in spec.files:
            path = root / spec.directory / filename
            for key, body in parse_text_db(path):
                yield spec, path, key, body


def load_legacy_entries(lang: str, root: Path | None = None) -> dict[tuple[str, str], str]:
    root = root or source_root()
    entries: dict[tuple[str, str], str] = {}
    for spec in TEXTDB_SPECS:
        lang_dir = root / spec.directory / lang
        if not lang_dir.is_dir():
            continue
        for filename in spec.files:
            path = lang_dir / filename
            if not path.exists():
                continue
            for key, body in parse_text_db(path):
                entries[(spec.name, key)] = body
    return entries


def po_quote(text: str) -> str:
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    lines = escaped.split("\n")

    quoted = ['""']
    for line in lines[:-1]:
        quoted.append(f'"{line}\\n"')
    if lines[-1]:
        quoted.append(f'"{lines[-1]}"')
    return "\n".join(quoted)


def write_header(handle, language: str) -> None:
    header = (
        'msgid ""\n'
        'msgstr ""\n'
        '"Project-Id-Version: crawl-data\\n"\n'
        '"Report-Msgid-Bugs-To: \\n"\n'
        f'"Language: {language}\\n"\n'
        '"MIME-Version: 1.0\\n"\n'
        '"Content-Type: text/plain; charset=UTF-8\\n"\n'
        '"Content-Transfer-Encoding: 8bit\\n"\n'
    )
    handle.write(header)


def write_entry(handle, *, comments: list[str], refs: list[str], context: str,
                msgid_text: str, msgstr_text: str) -> None:
    for comment in comments:
        handle.write(f"#. {comment}\n")
    for ref in refs:
        handle.write(f"#: {ref}\n")
    handle.write(f"msgctxt {po_quote(context)}\n")
    handle.write(f"msgid {po_quote(msgid_text)}\n")
    handle.write(f"msgstr {po_quote(msgstr_text)}\n\n")


def syntax_comments(body: str) -> list[str]:
    comments = []
    if "[[" in body and "]]" in body:
        comments.append("Preserve [[key]] references exactly.")
    if "{{" in body and "}}" in body:
        comments.append("Preserve {{ lua }} delimiters exactly.")
    if "@" in body:
        comments.append("Preserve @marker@ substitutions exactly.")
    return comments
