# Gettext Plan For Low-Hanging I18n Work

## Purpose

This document proposes a first, deliberately narrow gettext integration for
Dungeon Crawl Stone Soup. The goal is to move the easiest currently translatable
text onto standard gettext tooling without trying to solve every i18n problem in
one pass.

The plan focuses on the parts of Crawl that already behave like externalized
content:

- `TextDB` entries backed by English source files in `source/dat/descript/`
- `TextDB` entries backed by English source files in `source/dat/database/`
  where the content is descriptive and key-addressable

The plan explicitly does not try to gettext-enable all player-facing strings.
That would require a larger redesign of message construction, grammar handling,
and frontend-specific UI strings.

## Why Start Here

The current translation system already centralizes a large class of text in
`TextDB` (`source/database.cc`). These strings have several properties that make
them a good first gettext target:

1. They already live outside C++ source files.
2. They are keyed, so they can be extracted deterministically.
3. They already have partial volunteer translations in parallel language
   directories.
4. They already fallback to English when a translation is missing.
5. They are much less entangled with English sentence assembly than most
   hard-coded `mpr`/`mprf` messages.

This means we can adopt gettext for a meaningful slice of existing translation
work while keeping the risky parts of i18n out of scope for the first phase.

## Current State Summary

### Current translation mechanism

- The player chooses a language with the `language` option in
  `source/initfile.cc`.
- `Options.lang_name` is a two-letter language code such as `de` or `ko`.
- `databaseSystemInit()` initializes multiple `TextDB` instances at startup.
- Each `TextDB` reads English source files from `source/dat/descript/` or
  `source/dat/database/`, builds a DBM cache, and optionally overlays a
  translation DB from `source/dat/descript/<lang>/` or
  `source/dat/database/<lang>/`.
- Lookup first checks the translation DB, then falls back to English.

Relevant files:

- `source/database.cc`
- `source/database.h`
- `source/initfile.cc`
- `source/options.h`
- `docs/develop/translation.txt`

### TextDB features that matter for migration

The existing format is more than a flat key-value mapping. It supports:

- entry delimiters via `%%%%`
- alias entries via `<other key>`
- nested key references via `[[other key]]`
- embedded Lua via `{{ ... }}`
- weighted random substitution via `@foo@`

These features are important because the gettext plan must preserve them.

### Why not start with hard-coded messages

Hard-coded C++ messages are not the low-hanging part because much of Crawl's UI
text is assembled with English-specific helpers from `source/english.cc` and
`source/english.h`, including:

- `article_a()`
- `pluralise()`
- `pluralise_monster()`
- `conjugate_verb()`
- `apostrophise()`
- `apply_description()`

Gettext can translate whole sentences well, but it does not automatically solve
English-specific message assembly. Converting those paths is a later project.

## Scope

### In scope for the first gettext phase

The first phase should cover only `TextDB` categories with relatively direct,
descriptive text and low grammar coupling.

Recommended initial targets:

- `descriptions`
  - `features.txt`
  - `items.txt`
  - `unident.txt`
  - `unrand.txt`
  - `monsters.txt`
  - `spells.txt`
  - `gods.txt`
  - `branches.txt`
  - `skills.txt`
  - `ability.txt`
  - `cards.txt`
  - `commands.txt`
  - `clouds.txt`
  - `status.txt`
  - `monstatus.txt`
  - `mutations.txt`
  - `passives.txt`
- `gamestart`
  - `species.txt`
  - `backgrounds.txt`
- `help`
  - `help.txt`
- `faq`
  - `FAQ.txt`
- `hints`
  - `hints.txt`
- `egos`
  - `egos.txt`

These are all currently routed through stable `TextDB` lookups.

### Explicitly out of scope for the first phase

- direct C++ `mpr` and `mprf` message strings
- WebTiles lobby and browser-client UI strings
- Android launcher/app-shell strings
- YAML-generated names and descriptions in species/jobs/forms/monsters
- grammar-heavy runtime-generated messages
- item, monster, and player name generation logic
- fake-language support redesign
- replacement of all legacy `TextDB` translation directories at once

### Conditionally deferred TextDB areas

These should stay on the legacy system until the first gettext slice is stable:

- `speak`
- `shout`
- `misc`
- `randart`
- `quotes`

Reasons:

- more randomness and substitution behavior
- more flavor text that may rely on special formatting expectations
- `quotes` already have separate translation guidance

## Success Criteria

This phase is successful if all of the following are true:

1. Crawl can load gettext catalogs for selected `TextDB` domains without
   changing unrelated locale behavior.
2. Selected `TextDB` lookups prefer gettext translations and fall back to the
   English source text when no gettext translation exists.
3. Existing `TextDB` features like aliasing, `[[key]]`, and embedded Lua still
   work.
4. Translators can use standard gettext tools (`xgettext`, `msgmerge`,
   `msgfmt`, PO editors).
5. The build installs `.mo` files in a conventional location.
6. Legacy translation directories can continue to exist for out-of-scope DBs.

## Design Principles

### 1. Keep English source files as the source of truth

The English files under `source/dat/descript/` and `source/dat/database/`
should remain the authoritative content source for now.

Reasons:

- the game already expects them
- translators and developers already edit them
- they encode `TextDB` semantics directly
- they are still needed for English fallback and for the legacy non-gettext DBs

### 2. Use gettext only for translated payloads, not for key storage

We should not try to replace the English `TextDB` source files with gettext in
the first phase. Instead:

- English `TextDB` files continue to provide keys and raw English bodies.
- Gettext provides translated bodies for selected keys.
- Existing `TextDB` lookup and post-processing continues to run.

This produces the least disruption while still moving translators to PO files.

### 3. Preserve option-based language selection

The existing `language` option should remain the game-level language selector.
The first phase should not force translation selection to depend entirely on the
host OS locale.

### 4. Avoid locale-wide side effects

Crawl already uses locale-sensitive behavior for things like encoding and some
numeric formatting. The first gettext phase should avoid changing the process
locale in a way that could affect unrelated formatting or parsing.

## Proposed Architecture

### Translation domains

Introduce a dedicated gettext domain for the new data-backed translations.

Recommended initial domain layout:

- `crawl-data` for gettext-backed `TextDB` content in scope for this plan
- keep room for later domains such as `crawl-core`, `crawl-webtiles`, and
  `crawl-android`

Only `crawl-data` is needed for this phase.

### Catalog lookup model

For selected `TextDB` categories, gettext lookup should use both context and the
English message body.

Recommended mapping:

- `msgctxt`: `textdb:<db-name>:<key>`
- `msgid`: exact English body from the source file
- `msgstr`: translated body

Examples:

- `msgctxt "textdb:descriptions:acid dragon scales"`
- `msgctxt "textdb:help:autofight"`
- `msgctxt "textdb:gamestart:human"`

This avoids context collisions where two different keys happen to share the
same English body.

### Why use both key and English body

Using only the key is not enough because gettext works best when the English
source is also the reviewable canonical text.

Using only the English body is not enough because:

- identical English strings from different DBs could diverge later
- context is useful to translators
- migrations from legacy translations are easier with stable per-key context

### Runtime lookup order

For selected DBs, the recommended lookup order is:

1. fetch raw English body from the English `TextDB`
2. if the entry is an alias (`<key>`), preserve alias behavior before gettext
3. try gettext lookup using the English body and `textdb:<db>:<key>` context
4. if no gettext translation exists, keep the English body
5. run existing `TextDB` substitution/post-processing on the chosen body:
   - `[[key]]`
   - `{{ lua }}`
   - `@foo@` replacement where applicable

This keeps existing behavior intact while allowing gettext to translate the raw
entry text.

### Language selection strategy

The game should continue to read `Options.lang_name` from the `language`
setting.

For gettext, the first phase should:

- keep the host locale setup already present in `main.cc`
- set `LANGUAGE=<two-letter code>` before the first gettext-backed lookup
- bind the gettext domain once at startup
- set catalog codeset to UTF-8

Why this approach is recommended:

- it preserves Crawl's current game-level language override
- it avoids requiring users to install a matching full OS locale like
  `de_DE.UTF-8`
- it minimizes risk to locale-sensitive numeric code paths

Important note: this plan assumes gettext is initialized after options are read
and before `databaseSystemInit()` starts using translated data.

## File-Level Implementation Plan

### 1. Add a tiny gettext wrapper layer

Add a dedicated wrapper instead of scattering direct `gettext` calls through the
code.

Recommended new files:

- `source/i18n-gettext.h`
- `source/i18n-gettext.cc`

Responsibilities:

- initialize gettext domains
- normalize the chosen game language
- set `LANGUAGE` from `Options.lang_name`
- expose helpers such as:
  - `void init_gettext();`
  - `string gettext_p(const char *domain, const string &context,
    const string &msgid);`
  - `bool gettext_enabled_for_textdb(const TextDB &db);`

The wrapper should centralize portability checks and keep `database.cc` free of
low-level libintl details.

### 2. Hook gettext init into startup

Adjust startup flow so gettext initialization runs after options are known but
before `databaseSystemInit()` uses translatable DBs.

Likely touchpoints:

- `source/main.cc`
- `source/startup.cc`
- possibly option parsing code in `source/initfile.cc` if initialization order
  requires it

The implementation should make it clear that gettext domain binding is a startup
step, not a per-lookup step.

### 3. Teach `TextDB` which DBs are gettext-backed

`TextDB` currently knows only about its db name, directory, input files, parent,
and translation overlay.

Extend the model so each DB can advertise one of three modes:

- legacy-only
- gettext-backed
- mixed legacy/gettext during migration

Recommended approach:

- add a translation mode enum to `TextDB`
- annotate each `AllDBs[]` entry in `source/database.cc`

Example intent:

- `descriptions`, `gamestart`, `help`, `faq`, `hints`, `egos` -> gettext-backed
- `speak`, `shout`, `misc`, `randart`, `quotes` -> legacy-only initially

### 4. Add a raw-entry translation hook in `database.cc`

The central change belongs in `source/database.cc`.

Introduce a helper with behavior roughly like:

- fetch English raw entry body
- skip gettext for alias records if needed
- if DB mode is gettext-backed, query `crawl-data` using `msgctxt`
  `textdb:<db>:<key>` and the English body as `msgid`
- return translated-or-English body

This should happen before existing post-processing functions run.

Recommended touchpoints inside `database.cc`:

- `TextDB` metadata definition
- `_query_database()`
- `_getWeightedString()` if/when weighted DBs enter scope later

For the low-hanging phase, only `_query_database()` needs gettext integration.

### 5. Keep legacy translation overlays for out-of-scope DBs

Do not remove the current `translation = new TextDB(this)` model globally.

Instead:

- keep legacy overlay lookup for DBs still marked legacy-only
- bypass or disable translation overlay lookup for gettext-backed DBs

This reduces risk and allows an incremental migration.

### 6. Add a TextDB-to-POT extractor

`xgettext` cannot parse Crawl's `%%%%` text DB format directly. We need a custom
extractor script.

Recommended new file:

- `source/util/textdb-pot.py`

Responsibilities:

- parse English `TextDB` files using the same entry rules as `database.cc`
- emit a POT file for selected DBs
- generate stable `msgctxt` values
- preserve multiline bodies exactly
- skip comments and non-entry text
- optionally add extracted comments showing source file and key

Recommended extractor behavior:

- one POT entry per final English key/body pair
- no POT entry for alias records unless we decide translators need to see them
- preserve `[[...]]`, `{{...}}`, and `@foo@` markers literally in the `msgid`
- add translator comments warning not to break those markers

Example translator comment:

`#. Preserve [[key]], {{ lua }}, and @marker@ syntax exactly.`

### 7. Add a migration script from legacy text directories to PO

To avoid throwing away existing volunteer work, write a one-off migration tool.

Recommended new file:

- `source/util/textdb-legacy-to-po.py`

Responsibilities:

- read English source DB files
- read legacy translated files under `source/dat/descript/<lang>/` and
  `source/dat/database/<lang>/`
- match entries by English key
- emit or update `source/po/<lang>.po` entries with:
  - `msgctxt` based on db name and key
  - `msgid` from English body
  - `msgstr` from translated body

This script does not need to be part of the normal build forever, but it should
exist long enough to bootstrap the initial PO files.

### 8. Add build targets for catalog generation

Update `source/Makefile` to support gettext workflow.

Recommended new targets:

- `pot-data`
- `update-po`
- `compile-mo`
- `install-mo`

Recommended behavior:

- `pot-data`: run `textdb-pot.py` and write `source/po/crawl-data.pot`
- `update-po`: merge `source/po/*.po` against the latest POT via `msgmerge`
- `compile-mo`: build `source/po/<lang>.gmo` or
  `source/po/<lang>/LC_MESSAGES/crawl-data.mo`
- `install-mo`: install compiled catalogs under
  `$(datadir_fp)/locale/<lang>/LC_MESSAGES/` or the chosen system data dir

The install location should be consistent with the platform packaging story.

### 9. Add packaging support

Update packaging metadata so gettext tooling is available and `.mo` files are
installed.

Likely touchpoints:

- `source/debian/control`
- possibly Debian install manifests or rules if needed

Expected changes:

- add gettext tools to build dependencies
- make sure locale files are included in the package payload

### 10. Update developer documentation

Once the implementation exists, `docs/develop/translation.txt` should be updated
to describe the new translator workflow for gettext-backed content.

The old workflow should remain documented for any DBs still on the legacy path
during migration.

## Suggested Data Coverage For Phase 1

### Tier 1: safest first slice

Start with these DBs only:

- `descriptions`
- `gamestart`
- `help`
- `faq`
- `hints`
- `egos`

These have direct lookup APIs and relatively low runtime complexity.

### Tier 2: possible after Tier 1 lands

Only consider after the first slice is stable:

- `misc`
- `speak`
- `shout`

These involve more randomized or flavor-heavy content and deserve a separate
follow-up.

### Leave for later

- `randart`
- `quotes`

`randart` has naming implications and `quotes` have distinct policy concerns.

## Detailed Runtime Behavior

### Current behavior to preserve

For the selected DBs, the user-visible behavior should remain:

- English by default
- translated text when `language` is set and a translation exists
- English fallback for missing translations
- existing Lua, alias, and nested-reference behavior unchanged

### Proposed control flow for `getLongDescription()`-style lookups

1. caller asks for a key
2. `TextDB` fetches the English raw value from the English DB cache
3. if the raw value is an alias record, resolve alias as today
4. if the DB is gettext-backed, try `gettext_p("crawl-data", ctxt, msgid)`
5. if gettext returns untranslated text, keep the English body
6. run `[[key]]` substitution on the chosen body
7. run embedded Lua if the caller requested it
8. return the final string

This preserves Crawl's existing runtime semantics.

### Handling nested references

If a translated body contains `[[other key]]`, nested lookup should continue to
work by running the normal DB lookup for the nested key.

This means nested entries can mix:

- translated parent body
- translated nested entry if available
- English nested entry if not yet translated

That behavior matches Crawl's current partial-translation model.

### Handling alias entries

Alias entries are best treated as structure, not translatable content.

Recommended rule:

- if a raw entry is exactly `<other key>` in alias form, do not send it through
  gettext
- resolve the alias in the existing DB machinery
- then translate the target entry as normal

This avoids pointless duplicate translation entries.

### Handling embedded Lua

Embedded Lua should be preserved literally in the `msgid` and `msgstr`.

Recommended translator guidance:

- translators may move the Lua snippet within the sentence if needed
- translators must not change the surrounding `{{` and `}}`
- translators should avoid changing Lua code unless they understand its
  semantics and a translation truly requires it

This is not ideal long-term, but it is acceptable for the low-hanging phase.

## Developer Workflow After This Change

### Updating English source text

Developers continue editing the English source files in:

- `source/dat/descript/`
- `source/dat/database/`

Then they regenerate the POT and merge updates into PO files.

### Updating translations

Translators work in standard PO files under `source/po/` instead of editing
`source/dat/descript/<lang>/...` directly for the gettext-backed DBs.

Expected workflow:

1. update English source text
2. run `make pot-data`
3. run `make update-po`
4. edit `source/po/<lang>.po`
5. run `make compile-mo`
6. test in game with `language = <lang>`

### Mixed migration period

During migration, both workflows may coexist:

- gettext-backed DBs use PO files
- legacy-only DBs still use language directories

This should be documented clearly to avoid confusion.

## Testing Plan

### Unit-like extractor tests

Add tests for `textdb-pot.py` and the migration script using small fixture files.

Important cases:

- simple single-line entry
- multiline entry
- comments and blank lines
- alias entry `<other key>`
- entry with `[[other key]]`
- entry with `{{ lua }}`
- entry with `@marker@`

### Engine behavior tests

Add targeted tests around `database.cc` behavior where practical.

Important cases:

- gettext-backed DB returns translated value when catalog entry exists
- gettext-backed DB falls back to English when catalog entry is missing
- alias behavior remains correct
- nested `[[key]]` substitution still works after translation lookup
- embedded Lua still executes after translation lookup

### Manual smoke test matrix

Recommended manual checks:

1. run game in English with no `language` option
2. run with `language = de` or another existing translated language
3. inspect feature/item/god/monster descriptions
4. inspect game start species/background descriptions
5. inspect help and hint text
6. verify untranslated entries still show English
7. verify no crashes during DB regeneration

### Regression checks

Verify these remain unchanged for the first phase:

- startup locale behavior
- numeric parsing/formatting paths
- legacy translation DB lookup for out-of-scope DBs
- WebTiles behavior
- Android behavior

## Rollout Strategy

### Step 1: land infrastructure only

Land wrapper code, extractor scripts, build targets, and runtime hooks with one
very small catalog.

Goal:

- prove that gettext-backed `TextDB` lookup works end to end

### Step 2: migrate Tier 1 DBs

Generate the first real `crawl-data.pot`, convert existing translations, and
switch the selected Tier 1 DBs to gettext-backed mode.

### Step 3: deprecate legacy directories for migrated DBs

After one or two release cycles, decide whether to:

- keep legacy translated files as temporary bootstrap artifacts, or
- remove them for DBs that are fully migrated to PO files

### Step 4: evaluate next slice

Only after the above is stable should the project decide whether `misc`,
`speak`, and `shout` should also move.

## Risks And Mitigations

### Risk: gettext selection depends on system locale behavior

Mitigation:

- keep `language` as the primary game option
- use `LANGUAGE` for message selection instead of forcing a host locale change
- initialize gettext before first catalog lookup

### Risk: translation entries break `TextDB` syntax markers

Mitigation:

- add translator comments in the POT
- add extractor tests for marker preservation
- add manual smoke tests for entries containing markers

### Risk: mixed gettext and legacy systems become confusing

Mitigation:

- make DB migration mode explicit in code
- document exactly which DBs use which workflow
- stage migration by DB category instead of partial per-file guessing

### Risk: search helpers behave oddly with translated text

`getLongDescKeysByRegex()` and `getLongDescBodiesByRegex()` already have known
limitations for translated content.

Mitigation:

- do not try to fix translated regex search in this phase
- document that this remains an existing limitation

### Risk: packaging misses `.mo` files

Mitigation:

- add explicit install targets
- verify package contents in CI or release testing

## Open Questions

These do not block the first implementation, but they should be resolved before
or during review:

1. Should the installed locale path live under the existing Crawl data dir or a
   more standard shared locale dir on each platform?
2. Do we want one `crawl-data` domain now and split it later, or should we add
   more domains immediately for future-proofing?
3. Should alias entries ever appear in the POT for translator visibility, or
   should they always remain structural only?
4. Do we want a permanent migration script from legacy translation directories,
   or only a one-time bootstrap tool?
5. When Tier 1 is migrated, should the game warn if legacy translated files for
   the same DBs still exist?

## Follow-Up Work Deliberately Deferred

This plan is a stepping stone. After it lands, likely follow-up projects are:

- gettext for hard-coded C++ UI and message strings
- gettext or generated catalogs for WebTiles HTML/JS strings
- PO-backed generation for YAML-derived species/job/form/monster display strings
- audit and redesign of English-specific grammar composition
- Android string generation from PO or bidirectional PO/XML sync

Those are important, but they are not the low-hanging slice.

## Recommended First Patch Series

If this plan is implemented, the initial patch sequence should probably be:

1. add gettext wrapper and build plumbing
2. add `textdb-pot.py`
3. add minimal runtime hook for one `TextDB` category
4. add migration script and bootstrap one language catalog
5. expand to the full Tier 1 DB list
6. update translation docs

That sequence keeps each reviewable step small and makes failures easy to
localize.
