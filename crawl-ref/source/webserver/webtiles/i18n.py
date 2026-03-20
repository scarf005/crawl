import gettext
import json
import os
from functools import lru_cache

from webtiles.i18n_strings import WEBTILES_STRINGS


DOMAIN = "crawl-data"
CONTEXT_PREFIX = "webtiles:"


def _locale_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..",
                                        "locale"))


def _normalise_lang(lang):
    if not lang:
        return []

    lang = lang.strip()
    if not lang:
        return []

    lang = lang.split(";", 1)[0].strip()
    if not lang:
        return []

    lang = lang.replace("-", "_")
    variants = [lang]
    if len(lang) >= 2:
        short = lang[:2].lower()
        if short not in variants:
            variants.append(short)
    return variants


def _languages(handler):
    languages = []
    seen = set()

    try:
        override = handler.get_argument("lang", "")
    except Exception:
        override = ""

    for value in _normalise_lang(override):
        if value not in seen:
            seen.add(value)
            languages.append(value)

    accept_language = handler.request.headers.get("Accept-Language", "")
    for token in accept_language.split(","):
        for value in _normalise_lang(token):
            if value not in seen:
                seen.add(value)
                languages.append(value)

    return tuple(languages)


@lru_cache(maxsize=32)
def _translation(languages):
    locale_dir = _locale_dir()
    if not os.path.isdir(locale_dir):
        return gettext.NullTranslations()

    return gettext.translation(DOMAIN, locale_dir, languages=list(languages),
                               fallback=True)


def _pgettext(translation, context, msgid):
    combined = context + "\x04" + msgid
    translated = translation.gettext(combined)
    return msgid if translated == combined else translated


def translate(handler, context, msgid):
    return _pgettext(_translation(_languages(handler)),
                     CONTEXT_PREFIX + context, msgid)


def template_translator(handler):
    return lambda context, msgid: translate(handler, context, msgid)


def js_catalog(handler):
    catalog = {}
    for entry in WEBTILES_STRINGS:
        catalog[entry.context] = translate(handler, entry.context, entry.msgid)
    return catalog


def js_catalog_json(handler):
    return json.dumps(js_catalog(handler), ensure_ascii=False, sort_keys=True)
