/**
 * @file
 * @brief Gettext helpers for incremental i18n migration.
 **/

#pragma once

#include <string>

namespace i18n
{
void init_gettext();
void reload_gettext();
bool textdb_gettext_enabled();
std::string current_language_code();
std::string translate(const char *context, const std::string &english_body);
std::string translate_textdb_entry(const char *db_name,
                                   const std::string &key,
                                   const std::string &english_body);
}
