# -*- coding: utf-8 -*-
#
#    ICRAR - International Centre for Radio Astronomy Research
#    (c) UWA - The University of Western Australia
#    Copyright by UWA (in the framework of the ICRAR)
#    All rights reserved
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston,
#    MA 02111-1307  USA
#

"""
Configuration file for sourcefinder.
"""
from os.path import exists, dirname, realpath, join
from configobj import ConfigObj
from utils.logger import config_logger

from database_boinc import boinc_database_def
from database_duchamp import duchamp_database_def
from database_sofia import sofia_database_def

LOG = config_logger(__name__)


class ConfigItem:
    def __init__(self, name, config_name, default):
        self.name = name
        self.config_name = config_name
        self.default = default

config_entries = [
    ############### Database Settings ###############
    ConfigItem("DB_USER_ID", "databaseUserid", "root"),
    ConfigItem("DB_PASSWORD", "databasePassword", ""),
    ConfigItem("DB_HOSTNAME", "databaseHostname", "localhost"),
    ConfigItem("DB_NAME", "databaseName", ""),
    ConfigItem("BOINC_DB_NAME", "boincDatabaseName", "duchamp"),

    ############### Directory Settings ###############
    ConfigItem("DIR_PARAM", "paramDirectory", "/home/ec2-user/sf_parameters"),
    ConfigItem("DIR_CUBE", "cubeDirectory", "/home/ec2-user/sf_cubes"),
    ConfigItem("DIR_BOINC_PROJECT_PATH", "boincPath", "/home/ec2-user/projects/duchamp"),

    ConfigItem("FANOUT", "fanout", 1024),

    ############### Work Generation Settings ###############
    ConfigItem("BOINC_DB_NAME", "wgThreshold", 500),

    ############### AMAZON SETTINGS ###############
    ConfigItem("BOINC_DB_NAME", "bucket", "icrar.sourcefinder.files"),

    ConfigItem("APP_NAME", "appName", "sourcefinder")
]

extra_paths = [
    ("DIR_APP_TEMPLATES", "app_templates/", "DIR_BOINC_PROJECT_PATH"),
    ("DIR_VMS", "vm/", "DIR_BOINC_PROJECT_PATH"),
    ("PROG_SIGN_EXECUTABLE", "bin/sign_executable", "DIR_BOINC_PROJECT_PATH"),
    ("PROG_UPDATE_VERSIONS", "bin/update_versions", "DIR_BOINC_PROJECT_PATH"),
    ("DIR_KEYS", "keys/", "DIR_BOINC_PROJECT_PATH"),
    ("DIR_DOWNLOAD", "download/", "DIR_BOINC_PROJECT_PATH"),
    ("DIR_LOG", "log_ip-10-0-131-204/", "DIR_BOINC_PROJECT_PATH")
]


def read_config_file(filename, config_dict):
    if exists(filename):
        # Load from config file
        config_obj = ConfigObj(filename)

        for item in config_entries:
            if item.config_name in config_obj:
                config_dict[item.name] = config_obj[item.config_name]
    else:
        # Create a default
        default = ConfigObj()
        default.filename = filename
        for item in config_entries:
            default[item.config_name] = item.default
            config_dict[item.name] = item.default

        default.write()

        LOG.info("Creating a default config file for: {0}".format(filename))

    return config_dict


def get_config(app=None):
    """
    Returns the appropriate config for the given application
    The config for each application is stored in a file named "app.settings".
    Settings common to all configs are stored in "common.settings".
    Common settings are loaded first, then overwritten by app settings if applicable.
    :param app: The app to use.
    :return:
    """

    config = {}

    common_file_name = join(dirname(realpath(__file__)), 'common.settings'.format(app))
    # Copy the fields from common.settings first
    read_config_file(common_file_name, config)

    # Add in the database tables
    config["database_boinc"] = boinc_database_def
    config["database_duchamp"] = duchamp_database_def
    config["database_sofia"] = sofia_database_def

    if app is not None:
        # Load app specific settings
        config_file_name = join(dirname(realpath(__file__)), '{0}.settings'.format(app))
        # Copy from the settings for this app
        read_config_file(config_file_name, config)

        config["DIR_APPS"] = join(config["DIR_BOINC_PROJECT_PATH"], "apps/{0}".format(app))

        # Set the database def for this module.
        config["database"] = config["database_{0}".format(config["APP_NAME"])]

    base_db_login = "mysql://" + \
                    config['DB_USER_ID'] + ":" + \
                    config['DB_PASSWORD'] + "@" + \
                    config['DB_HOSTNAME'] + "/"

    # Set up database connection string
    config["BASE_DB_LOGIN"] = base_db_login
    config["DB_LOGIN"] = base_db_login + config['DB_NAME']
    config["BOINC_DB_LOGIN"] = base_db_login + config['BOINC_DB_NAME']

    config["DIR_OLD_LOGS"] = "/home/ec2-user/old_logs/"
    config["DIR_VALIDATOR_INVALIDS"] = "/home/ec2-user/validator_invalids/"

    for item in extra_paths:
        config[item[0]] = join(config[item[2]], item[1])

    return config
