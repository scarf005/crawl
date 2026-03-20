/**
 * @file
 * @brief Gettext helpers for incremental i18n migration.
 **/

#pragma once

#include <string>

namespace i18n
{
void init_gettext();
bool textdb_gettext_enabled();
std::string translate_textdb_entry(const char *db_name,
                                   const std::string &key,
                                   const std::string &english_body);
}
