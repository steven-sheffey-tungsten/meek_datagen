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

# Set versioning for tor browser
ENV TOR_DIST_MIRROR="https://www.torproject.org" \
    TBB_PATH="/home/$DEFAULT_USER/tor_browser" \
	TBB_VERSION="8.0a7" \
	GPG_KEYSERVER="sks-keyservers.net" \
	TBB_KEYID="EF6E 286D DA85 EA2A 4BA7  DE68 4E2C 6E87 9329 8290"

# Download tor browser from the tor browser website
# Verify it with GPG
# Unzip it
# Delete the zip and gpg files
RUN wget --no-verbose "${TOR_DIST_MIRROR}/dist/torbrowser/${TBB_VERSION}/tor-browser-linux64-${TBB_VERSION}_en-US.tar.xz" -O tor_browser.tar.xz && \
    wget --no-verbose "${TOR_DIST_MIRROR}/dist/torbrowser/${TBB_VERSION}/tor-browser-linux64-${TBB_VERSION}_en-US.tar.xz.asc" -O tor_browser.tar.xz.asc && \
    gpg --keyserver "${GPG_KEYSERVER}" --recv-keys "${TBB_KEYID}" && \
    gpg --verify tor_browser.tar.xz.asc && \
    tar xf tor_browser.tar.xz && \
    mv tor-browser_en-US $TBB_PATH && \
    rm tor_browser.tar.xz tor_browser.tar.xz.asc

# Copy over files required for building a python environment
COPY python/requirements.txt .
COPY python/install_python_dependencies.sh . 
# Set up a python3 virtual environment
RUN python3 -m virtualenv -p python3 env && \
    ./install_python_dependencies.sh env requirements.txt && \
	rm -f install_python_dependencies.sh  requirements.txt

# Copy over the entrypoint and set it up
COPY entrypoint.sh . 
ENTRYPOINT ["./entrypoint.sh"]

# Copy over the python scripts into the prefix
COPY python/tor_datagen.py /usr/local/bin
