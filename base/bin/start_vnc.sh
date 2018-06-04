#!/bin/bash
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

# Set VNC log dir
if [ -z "$VNC_LOG" ]; then
	VNC_LOG=$HOME/logs/x11vnc.log
fi

# Pull the VNC password
export VNC_PASSWORD=$(cat ~/.vnc_password)

# Start a VNC server 
x11vnc -forever -passwd $VNC_PASSWORD -ncache 10 >> $VNC_LOG 2>&1 &
echo "VNC server started"

# Start an xterm so we have something to use
xterm &

# Start dbus
echo "Starting dbus"
dbus-daemon --session --fork
