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

# Add local scripts to path
PATH=$HOME/bin:$PATH

# Prefix for captures
PCAP_PREFIX=firefox

# Start XVFB
source start_xvfb.sh
# Start VNC
start_vnc.sh

# Start capturing packets
echo "Starting TCPDUMP"
# Captures all traffic on port 443
sudo tcpdump -w pcap_data/${PCAP_PREFIX}_$(date +%s).pcap port 443 &
# Get PID of tcpdump
TCPDUMP_PID=""
while [[ $TCPDUMP_PID == "" ]]; do
	export TCPDUMP_PID=`ps --ppid $! -o pid=`
done
echo "TCPDUMP started on $TCPDUMP_PID"

# Activate the python environment
source ./env3/bin/activate
# Run the capture script
./firefox_data_generator.py
# Deactivate the python environment
deactivate

# Once program is done, wait until we have cleanly killed tcpdump
echo "Waiting for TCPDUMP to exit cleanly"
while sudo kill $TCPDUMP_PID; do
	sleep 0.5
done
