#!/bin/bash
# Copyright 2018 Steven Sheffey
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



# Get PID from PID file
# TODO: verify existence
export TCPDUMP_PID="$(cat /tmp/tcpdump.pid)"
# Kill tcpdump
echo "Killing tcpdump"
kill $TCPDUMP_PID
# Wait until the pidfile is gone
while [ -f "/tmp/tcpdump.pid" ]
do
	sleep 0.5
	echo "Waiting for tcpdump to be dead"
done
