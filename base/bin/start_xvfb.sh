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

# first we need our security cookie and add it to user's .Xauthority
mcookie | sed -e "s/^/add $DISPLAY MIT-MAGIC-COOKIE-1 /" | xauth -q

# now place the security cookie with FamilyWild on volume so client can use it
# see http://stackoverflow.com/25280523 for details on the following command
xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f .xserver.xauth nmerge -



# Set resolution, depth, and DPI
if [ -z "$XFB_SCREEN" ]; then
	XFB_SCREEN=1024x768x24
fi

if [ ! -z "$XFB_SCREEN_DPI" ]; then
	DPI_OPTIONS="-dpi $XFB_SCREEN_DPI"
fi

# now boot X-Server, tell it to use our cookie
Xvfb $DISPLAY -auth ~/.Xauthority $DPI_OPTIONS -screen 0 $XFB_SCREEN -nolisten tcp >> ~/logs/xvfb.log 2>&1 &

# Export Xauthority
export XAUTHORITY=$HOME/.Xauthority
# Ensure Xvfb has started
echo "Waiting for XVFB to start up"
wait_xvfb.sh >> /dev/null 2>&1
echo "XVFB has started"
