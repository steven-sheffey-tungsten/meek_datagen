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

# Basis is Ubuntu LTS
FROM ubuntu:18.04

# Package metadata
LABEL version="0.4"
LABEL Description="This image starts up a browser, and navigates websites to produce packet captures"

ENV DEBIAN_FRONTEND=noninteractive \
	DEBCONF_NONINTERACTIVE_SEEN=true \
	TZ="UTC" \
	DEFAULT_USER=user

# Add apt utils to avoid errors
RUN apt-get update -y && \
	apt-get install -y apt-utils 
# Re-run update since  before this will likely change only rarely
RUN apt-get update -y && \
	apt-get upgrade -y && \
	apt-get install -y \
		bzip2 ca-certificates dbus-x11 firefox gnupg libevent-2.1-6 libgtk2.0-0 python python-virtualenv \
		python3 python3-virtualenv pulseaudio sudo tcpdump tigervnc-standalone-server tor tzdata unzip wget x11vnc \
		x11-utils x11-xserver-utils xauth xterm xvfb xz-utils && \
	apt-get purge -y tor
# Set timezone
RUN echo "${TZ}" > /etc/timezone && \
	dpkg-reconfigure --frontend noninteractive tzdata

# Add an untrusted user
RUN useradd -m ${DEFAULT_USER} && \
    chown -R ${DEFAULT_USER}.${DEFAULT_USER} /home/${DEFAULT_USER} && \
	chmod -R 770 /home/${DEFAULT_USER}

# Give the untrusted user permission to use sudo to	sniff packets
RUN echo "${DEFAULT_USER} ALL=NOPASSWD: /usr/sbin/tcpdump, /bin/kill" > /etc/sudoers.d/tcpdump


# Use the user's home dir for all activities
WORKDIR /home/$DEFAULT_USER
# Switch to user
USER $DEFAULT_USER

# Set up files needed for the X and vnc server
ENV DISPLAY=:0
RUN touch .Xauthority .xserver.xauth

# Download the alexa top 1M dataset
RUN mkdir data &&\
    cd data && \
	wget --no-verbose "https://s3.amazonaws.com/alexa-static/top-1m.csv.zip"	&& \
	unzip top-1m.csv.zip && \
	rm top-1m.csv.zip

# Copy over the VNC password
COPY vnc_password .vnc_password
# Copy miscellaneous scripts
# TODO: change this to use a variable user when it is supported
COPY --chown=user:user bin bin
