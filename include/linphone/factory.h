/*
linphone
Copyright (C) 2016 Belledonne Communications <info@belledonne-communications.com>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
*/

#ifndef LINPHONE_FACTORY_H
#define LINPHONE_FACTORY_H

#include "linphone/core.h"

#ifdef _cplusplus
extern "C" {
#endif

/**
 * @addtogroup initializing
 * @{
 */

/**
 * #LinphoneFactory is a singleton object devoted to the creation of all the object
 * of Liblinphone that cannot created by #LinphoneCore or #LinphoneCore itself.
 */
typedef struct _LinphoneFactory LinphoneFactory;

/**
 * Create the #LinphoneFactory if that has not been done and return
 * a pointer on it.
 * @return A pointer on the #LinphoneFactory
 */
LINPHONE_PUBLIC LinphoneFactory *linphone_factory_get(void);

/**
 * Instanciate a #LinphoneCore object.
 *
 * The LinphoneCore object is the primary handle for doing all phone actions.
 * It should be unique within your application.
 * @param factory The #LinphoneFactory singleton.
 * @param cbs a #LinphoneCoreCbs object holding your application callbacks. A reference
 * will be taken on it until the destruciton of the core or the unregistration
 * with linphone_core_remove_cbs().
 * @param config_path a path to a config file. If it does not exists it will be created.
 *        The config file is used to store all settings, call logs, friends, proxies... so that all these settings
 *	       become persistent over the life of the LinphoneCore object.
 *	       It is allowed to set a NULL config file. In that case LinphoneCore will not store any settings.
 * @param factory_config_path a path to a read-only config file that can be used to
 *        to store hard-coded preference such as proxy settings or internal preferences.
 *        The settings in this factory file always override the one in the normal config file.
 *        It is OPTIONAL, use NULL if unneeded.
 * @see linphone_core_new_with_config
 */
LINPHONE_PUBLIC LinphoneCore *linphone_factory_create_core(const LinphoneFactory *factory, LinphoneCoreCbs *cbs,
						const char *config_path, const char *factory_config_path);

/**
 * Instantiates a LinphoneCore object with a given LpConfig.
 *
 * @param factory The #LinphoneFactory singleton.
 * The LinphoneCore object is the primary handle for doing all phone actions.
 * It should be unique within your application.
 * @param cbs a #LinphoneCoreCbs object holding your application callbacks. A reference
 * will be taken on it until the destruciton of the core or the unregistration
 * with linphone_core_remove_cbs().
 * @param config a pointer to an LpConfig object holding the configuration of the LinphoneCore to be instantiated.
 * @see linphone_core_new
 */
LINPHONE_PUBLIC LinphoneCore *linphone_factory_create_core_with_config(const LinphoneFactory *factory, LinphoneCoreCbs *cbs, LinphoneConfig *config);

/**
 * Instanciate a #LinphoneCoreCbs object.
 * @return a new #LinponeCoreCbs.
 */
LINPHONE_PUBLIC LinphoneCoreCbs *linphone_factory_create_core_cbs(const LinphoneFactory *factory);

/**
 * Parse a string holding a SIP URI and create the according #LinphoneAddress object.
 * @param factory The #LinphoneFactory singleton.
 * @param addr A string holding the SIP URI to parse.
 * @return A new #LinphoneAddress.
 */
LINPHONE_PUBLIC LinphoneAddress *linphone_factory_create_address(const LinphoneFactory *factory, const char *addr);

/**
 * @}
 */

#ifdef _cplusplus
}
#endif


#endif // LINPHONE_FACTORY_H