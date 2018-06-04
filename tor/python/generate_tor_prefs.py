#!/usr/bin/env python3
# Copyright 2018 Steven Sheffey
# This file is part of meek_datagen.
# 
# meek_datagen is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# meek_datagen is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with meek_datagen.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import json

def user_pref(key: str, value) -> str:
    """
    Generates a user preference entry from a key and value
    :param key: the preference key
    :type key: str
    :param value: the preference value
    :type value: Any
    :returns: A user preference string
    :rtype str:
    """
    return "user_pref(\"{}\", {});".format(key, json.dumps(value))

def main():
    # Initialize argument parser
    parser = argparse.ArgumentParser(description="Generates \"prefs.js\" configs for Tor Browser")
    parser.add_argument("bridge_type", type=str, help="The bridge to use for connecting to the TOR network")
    # Apply parser
    args = parser.parse_args()
    print(user_pref("extensions.torlauncher.prompt_at_startup", False))
    print(user_pref("extensions.torlauncher.default_bridge_type", args.bridge_type))
    print(user_pref("browser.startup.page", "0"))
    print(user_pref("browser.startup.homepage", "about:blank"))
    print(user_pref("app.update.enabled", False))
    print(user_pref("extensions.torbutton.versioncheck_enabled", False))
    print(user_pref("", False))

if __name__=="__main__":
    main()
