#!/usr/bin/env bash

# Add MongoDB to apt
apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/10gen.list

# Update and begin installing some utility tools
apt-get -y update
apt-get install -y python-software-properties python-setuptools build-essential
apt-get install -y git vim htop

# Add nodejs repo
add-apt-repository -y ppa:chris-lea/node.js
apt-get -y update

# Install requirements
cat /vagrant/ubuntu_dependencies.txt | xargs apt-get -y install
easy_install pip
pip install -r /vagrant/requirements.txt
