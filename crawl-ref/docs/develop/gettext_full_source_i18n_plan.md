# Full Gettext I18n Plan For DCSS Source

## Goal

Move Dungeon Crawl Stone Soup from partial, mixed translation support to a
gettext-based i18n model that covers the local client, WebTiles, and remaining
player-facing source strings in a staged way.

This document is the follow-up roadmap after the initial `TextDB` and startup
menu groundwork.

## Current State

The repository now has these building blocks:

- gettext runtime setup for `crawl-data`
- `TextDB` translation extraction and PO bootstrap tooling
- local startup menu gettext coverage
- initial WebTiles lobby gettext coverage
- bundled local-tiles CJK fallback font support

The project still does not have comprehensive gettext coverage for most of the
core C++ UI and message paths.

## Main Remaining Workstreams

### 1. Core local UI strings

Target the remaining high-visibility UI surfaces in `./crawl` first:

- newgame character choice flow
- weapon/species/background selection prompts
- help and command menus not already backed by `TextDB`
- skill, inventory, and overview menu headings
- death/win summary UI scaffolding

Implementation notes:

- continue using explicit gettext contexts instead of raw `_()` only
- prefer whole-sentence translations over stitched fragments
- add extraction manifests for source-owned UI strings, similar to
  `core_i18n_strings.py`

### 2. Runtime message translation

Most of Crawl's player-facing text still comes from hard-coded `mpr`/`mprf`
paths and English-specific helpers.

This needs a staged migration:

1. identify repeated, stable, whole-sentence messages that are easy to move
2. add `pgettext`/`ngettext` wrappers for source strings
3. migrate call sites with minimal English grammar coupling first
4. defer deeply compositional messages until grammar support is redesigned

High-value first targets:

- startup/load/save status lines
- menu feedback strings
- simple prompts and confirmation dialogs
- stable option/help labels

### 3. English grammar disentangling

Full i18n support will remain incomplete until DCSS stops assuming English
sentence assembly in core message generation.

Critical areas:

- article selection
- pluralization
- verb conjugation
- possessives and pronouns
- monster/item name insertion inside translated clauses

Future direction:

- replace fragment assembly with translator-visible full sentences where possible
- introduce `ngettext` for count-sensitive messages
- keep canonical ids for gameplay logic, and translate only display strings

### 4. Data-generated names and labels

Several gameplay labels are generated from structured data rather than `TextDB`.

Needs dedicated extraction/generation work for:

- species/job data
- monster display names
- form names
- ability labels
- tab and panel labels produced from enums or generated tables

Recommended approach:

- keep canonical source ids stable
- generate POT entries from data generators
- never use translated names as gameplay lookup keys

### 5. WebTiles completion

The current WebTiles coverage is intentionally narrow.

Next phases should include:

- in-game WebTiles overlays
- spectator/chat prompts beyond the lobby shell
- settings and account management flows
- JSON-delivered UI text for live client updates

The current shared `crawl-data` domain is enough for early rollout, but the
project should decide later whether to split into `crawl-core` and
`crawl-webtiles`.

### 6. Android and platform packaging

Android still uses its own resource strings.

Future work:

- decide whether PO is the source of truth and `strings.xml` is generated
- or maintain bidirectional sync tooling
- package `.mo` catalogs and fallback fonts for each supported platform
- document runtime locale search rules clearly

### 7. Font and shaping support

The current local-tiles fallback font solves missing glyphs for the startup UI,
but it is still a basic FreeType glyph fallback path.

Later work should evaluate:

- broader bundled fallback coverage beyond Korean-focused CJK fallback
- font fallback chains per script
- whether shaping-sensitive scripts need HarfBuzz-aware rendering paths
- font packaging size trade-offs per platform

## Recommended Delivery Phases

### Phase A: Finish high-visibility UI

- local startup/newgame menus
- remaining local menu chrome
- more WebTiles shell strings

### Phase B: Expand source extraction

- maintainable manifests for source-owned gettext strings
- CI checks that updated source strings regenerate POT cleanly
- translator documentation for source/UI strings vs `TextDB`

### Phase C: Migrate easy runtime messages

- simple prompts
- whole-sentence status lines
- plural-aware messages with `ngettext`

### Phase D: Grammar redesign

- reduce English-only helper dependence
- convert compositional messages into translatable sentence units

### Phase E: Structured data and platform parity

- generated gameplay labels
- Android
- full WebTiles parity

## Engineering Rules For Future I18n Patches

- preserve canonical gameplay ids in English/internal form
- translate display strings only
- prefer explicit context for short/common strings
- use whole messages, not fragments, whenever feasible
- keep local builds producing `.mo` catalogs by default
- require manual verification with at least one CJK locale and one
  non-CJK locale before merging major UI i18n work

## Verification Checklist For Future Phases

- `mold -run ccache make -j10 TILES=y`
- `make -C crawl-ref/source pot-data`
- `make -C crawl-ref/source compile-mo`
- verify local startup/newgame flow in Korean
- verify a non-English Latin-script locale
- verify WebTiles lobby rendering
- verify missing translations fall back to English cleanly

## Long-Term Success Criteria

DCSS can be considered meaningfully gettext-enabled when:

- most high-visibility local UI is translated through gettext
- WebTiles uses the same translation source of truth
- translators work primarily in PO files, not ad hoc parallel trees
- grammar-sensitive messages are migrated away from English-only assembly
- fonts and runtime packaging make translated text readable by default
