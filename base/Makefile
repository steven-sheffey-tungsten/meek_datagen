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

IMAGE_NAME=packet_capture_base
IMAGE_TAG=latest

,PHONY: build
build:
	# Generate a new password
	LC_CTYPE=C tr -dc "[[:print:]]" < /dev/urandom | head -c 8 > vnc_password
	# Build the image
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .
	# Generate a vncpasswd for use in tightvnc viewer
	docker run --rm -v `pwd`:/outside \
		$(IMAGE_NAME):$(IMAGE_TAG) \
		bash -c "vncpasswd -f < .vnc_password > /outside/vncpasswd"
