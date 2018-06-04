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
all: build

SERVICE_NAME=firefox_trace_generator

build:
	docker-compose build $(SERVICE_NAME)

run: build
	# Create volumes
	mkdir -p pcap_data
	mkdir -p logs
	# Run image
	docker-compose up --force-recreate $(SERVICE_NAME)

vnc:
	vncpasswd -f < ../base/vnc_password > .vncpasswd
	vncviewer localhost -passwd .vncpasswd
