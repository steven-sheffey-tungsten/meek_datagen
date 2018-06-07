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
LABEL version="0.6"
LABEL Description="Base image providing libraries necessary for headless browsing"
ENV DEBIAN_FRONTEND=noninteractive \
	DEBCONF_NONINTERACTIVE_SEEN=true \
	TZ="UTC" \
	DEFAULT_USER=user
# Add apt utils initially to get rid of a few errors
RUN apt-get update -y && \
	apt-get install -y apt-utils 
# Install all packages
RUN apt-get update -y && \
	apt-get upgrade -y && \
	apt-get install -y \
		bzip2 ca-certificates dbus-x11 firefox gnupg libgtk2.0-0 \
		python3 python3-virtualenv \
		sudo tcpdump tor tzdata unzip wget xvfb xz-utils && \
	apt-get purge -y tor
# Set timezone
RUN echo "${TZ}" > /etc/timezone && \
	dpkg-reconfigure --frontend noninteractive tzdata
# Add an untrusted user
RUN useradd -m ${DEFAULT_USER} && \
    chown -R ${DEFAULT_USER}.${DEFAULT_USER} /home/${DEFAULT_USER} && \
	chmod -R 770 /home/${DEFAULT_USER}
# Give the untrusted user permission to use sudo to	sniff packets
RUN echo "${DEFAULT_USER} ALL=NOPASSWD: /usr/local/bin/start_tcpdump.sh" >> /etc/sudoers.d/tcpdump
RUN echo "${DEFAULT_USER} ALL=NOPASSWD: /usr/local/bin/stop_tcpdump.sh" >> /etc/sudoers.d/tcpdump
# Use the user's home dir for all activities
WORKDIR /home/$DEFAULT_USER
# Download the alexa top 1M dataset
RUN mkdir data &&\
    cd data && \
	wget --no-verbose "https://s3.amazonaws.com/alexa-static/top-1m.csv.zip"	&& \
	unzip top-1m.csv.zip && \
	rm top-1m.csv.zip
# Copy all scripts into our VM's local prefix
COPY bin/* /usr/local/bin/
# Switch to user
USER $DEFAULT_USER
