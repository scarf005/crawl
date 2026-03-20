/**
 * @file
 * @brief Gettext helpers for incremental i18n migration.
 **/

#include "AppHdr.h"

#include "i18n-gettext.h"

#include <cstdlib>

#if defined(__GLIBC__)
#include <libintl.h>
#endif

#include "files.h"
#include "options.h"

namespace i18n
{
namespace
{
static const char *const TEXTDB_DOMAIN = "crawl-data";

bool gettext_initialised;
bool textdb_enabled;

std::string _textdb_context(const char *db_name, const std::string &key)
{
    return std::string("textdb:") + db_name + ":" + key;
}

#if defined(__GLIBC__)
void _set_language_env(const char *lang)
{
    if (!lang || !lang[0])
        return;

    setenv("LANGUAGE", lang, 1);
}
#endif
} // namespace

void init_gettext()
{
    if (gettext_initialised)
        return;

    gettext_initialised = true;

#if defined(__GLIBC__)
    if (!Options.lang_name || !Options.lang_name[0])
        return;

    const std::string locale_dir = datafile_path("locale", false, false,
                                                 dir_exists);
    if (locale_dir.empty())
        return;

    _set_language_env(Options.lang_name);
    bindtextdomain(TEXTDB_DOMAIN, locale_dir.c_str());
    bind_textdomain_codeset(TEXTDB_DOMAIN, "UTF-8");
    textdomain(TEXTDB_DOMAIN);
    textdb_enabled = true;
#endif
}

bool textdb_gettext_enabled()
{
    return textdb_enabled;
}

std::string translate_textdb_entry(const char *db_name,
                                   const std::string &key,
                                   const std::string &english_body)
{
#if defined(__GLIBC__)
    if (!textdb_enabled || english_body.empty())
        return "";

    const std::string msgid = _textdb_context(db_name, key)
                              + '\004' + english_body;
    const char *translated = dgettext(TEXTDB_DOMAIN, msgid.c_str());
    if (!translated || msgid == translated)
        return "";

    return translated;
#else
    UNUSED(db_name);
    UNUSED(key);
    UNUSED(english_body);
    return "";
#endif
}
} // namespace i18n
