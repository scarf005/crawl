/**
 * @file
 * @brief Gettext helpers for incremental i18n migration.
 **/

#include "AppHdr.h"

#include "i18n-gettext.h"

#include <clocale>
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

bool textdb_enabled;
std::string locale_dir;

std::string _textdb_context(const char *db_name, const std::string &key)
{
    return std::string("textdb:") + db_name + ":" + key;
}

#if defined(__GLIBC__)
void _set_language_env(const char *lang)
{
    if (lang && lang[0])
        setenv("LANGUAGE", lang, 1);
    else
        unsetenv("LANGUAGE");
}
#endif
} // namespace

void init_gettext()
{
#if defined(__GLIBC__)
    if (locale_dir.empty())
    {
        locale_dir = datafile_path("locale", false, false, dir_exists);
        if (!locale_dir.empty())
        {
            bindtextdomain(TEXTDB_DOMAIN, locale_dir.c_str());
            bind_textdomain_codeset(TEXTDB_DOMAIN, "UTF-8");
            textdomain(TEXTDB_DOMAIN);
        }
    }
#endif

    reload_gettext();
}

void reload_gettext()
{
    textdb_enabled = false;

#if defined(__GLIBC__)
    _set_language_env(Options.lang_name);
    setlocale(LC_MESSAGES, "");

    if (!locale_dir.empty() && Options.lang_name && Options.lang_name[0])
        textdb_enabled = true;
#endif
}

bool textdb_gettext_enabled()
{
    return textdb_enabled;
}

std::string current_language_code()
{
    return Options.lang_name && Options.lang_name[0] ? Options.lang_name : "en";
}

std::string translate(const char *context, const std::string &english_body)
{
#if defined(__GLIBC__)
    if (!textdb_enabled || english_body.empty())
        return english_body;

    const std::string msgid = std::string(context) + '\004' + english_body;
    const char *translated = dgettext(TEXTDB_DOMAIN, msgid.c_str());
    if (!translated || msgid == translated)
        return english_body;

    return translated;
#else
    UNUSED(context);
    return english_body;
#endif
}

std::string translate_textdb_entry(const char *db_name,
                                   const std::string &key,
                                   const std::string &english_body)
{
    const std::string translated = translate(_textdb_context(db_name, key).c_str(),
                                             english_body);
    if (translated == english_body)
        return "";

    return translated;
}
} // namespace i18n
