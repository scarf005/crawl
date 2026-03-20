Bundled fallback font for local tiles gettext work.

- Font: `NotoSansMonoCJKkr-Regular.otf`
- Source: `https://github.com/notofonts/noto-cjk`
- License: SIL Open Font License 1.1; see `LICENSE`

The font is bundled as a runtime fallback for missing CJK glyphs in local
tiles builds, so translated startup and UI text remain readable even when the
configured system font lacks those glyphs.
