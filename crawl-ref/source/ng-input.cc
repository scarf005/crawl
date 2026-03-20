#include "AppHdr.h"

#include "ng-input.h"

#include <cwctype>

#include "end.h"
#include "format.h"
#include "i18n-gettext.h"
#include "item-name.h" // make_name
#include "libutil.h"
#include "options.h"
#include "stringutil.h"
#include "unicode.h"
#include "version.h"

static string _replace_token(string text, const string &token,
                             const string &value)
{
    const size_t pos = text.find(token);
    if (pos != string::npos)
        text.replace(pos, token.size(), value);
    return text;
}

// Eventually, this should be something more grand. {dlb}
formatted_string opening_screen()
{
    string msg = i18n::translate(
        "startup:opening_screen",
        "<yellow>Hello, welcome to {crawl} {version}!</yellow>\n<brown>" CRAWL_COPYRIGHT);
    msg = _replace_token(msg, "{crawl}", CRAWL);
    msg = _replace_token(msg, "{version}", Version::Long);

    return formatted_string::parse_string(msg);
}

formatted_string options_read_status()
{
    string msg;
    FileLineInput f(Options.filename.c_str());

    if (!f.error())
    {
        msg += i18n::translate("startup:options_read_prefix",
                               "<lightgrey>Options read from \"");
#ifdef DGAMELAUNCH
        // For dgl installs, show only the last segment of the .crawlrc
        // file name so that we don't leak details of the directory
        // structure to (untrusted) users.
        msg += Options.basefilename;
#else
        msg += Options.filename;
#endif
        msg += i18n::translate("startup:options_read_suffix",
                               "\".</lightgrey>");
    }
    else
    {
        if (!Options.filename.empty())
        {
            msg += i18n::translate("startup:options_file_unreadable_prefix",
                                   "<lightred>Options file \"");
            msg += Options.filename;
            msg += i18n::translate("startup:options_file_unreadable_suffix",
                                   "\" is not readable; using defaults.</lightred>");
        }
        else
            msg += i18n::translate("startup:options_file_missing",
                                   "<lightred>Options file not found; using defaults.</lightred>");
    }

    msg += "\n";

    return formatted_string::parse_string(msg);
}

bool is_good_name(const string& name, bool blankOK)
{
    // verification begins here {dlb}:
    // Disallow names that would result in a save named just ".cs".
    if (strip_filename_unsafe_chars(name).empty())
        return blankOK && name.empty();
    return validate_player_name(name);
}

bool validate_player_name(const string &name)
{
#if defined(TARGET_OS_WINDOWS)
    // Quick check for CON -- blows up real good under DOS/Windows.
    if (strcasecmp(name.c_str(), "con") == 0
        || strcasecmp(name.c_str(), "nul") == 0
        || strcasecmp(name.c_str(), "prn") == 0
        || strnicmp(name.c_str(), "LPT", 3) == 0)
    {
        return false;
    }
#endif

    if (strwidth(name) > MAX_NAME_LENGTH)
        return false;

    char32_t c;
    for (const char *str = name.c_str(); int l = utf8towc(&c, str); str += l)
    {
        // The technical reasons are gone, but enforcing some sanity doesn't
        // hurt.
        if (!iswalnum(c) && c != '-' && c != '.' && c != '_' && c != ' ')
            return false;
    }

    return true;
}
