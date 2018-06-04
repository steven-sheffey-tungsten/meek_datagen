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

# from https://github.com/elgalu/docker-selenium/blob/master/xvfb/bin/wait-xvfb.sh
# set -e: exit asap if a command exits with a non-zero status
set -e

while ! xdpyinfo -display ${DISPLAY}; do
  echo -n ''
  sleep 0.1
done
