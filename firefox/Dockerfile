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
# Pull from the common packet capture image
FROM packet_capture_base:latest 

# Package metadata
LABEL version="0.5"
LABEL Description="This image starts up Firefox and navigates HTTPS sites to gather samples of HTTPS traffic" 

# Download and set up geckodriver
ARG GECKODRIVER_VERSION=0.19.1
RUN  wget --no-verbose -O geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v$GECKODRIVER_VERSION/geckodriver-v$GECKODRIVER_VERSION-linux64.tar.gz && \
  tar xf geckodriver.tar.gz -C bin && \
  rm geckodriver.tar.gz && \
  chmod 755 bin/geckodriver

# Copy over the entrypoint and set it up
COPY entrypoint.sh . 
ENTRYPOINT ["./entrypoint.sh"]

# Start the python folder
# Copy over files required for building a python environment
COPY python/requirements.txt .
COPY python/install_python_dependencies.sh . 
# Set up a python virtual environment
RUN python3 -m virtualenv -p python3 env3 && \
	./install_python_dependencies.sh env3 requirements.txt && \
	rm install_python_dependencies.sh requirements.txt

# Copy over the python script
COPY python/firefox_data_generator.py .
