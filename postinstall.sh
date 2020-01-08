#!/bin/bash

#
echo "Grabbing Fedora packages"


# flatpak
echo "Grabbing flatpak packages"
flatpak install 

# python pkgs
echo "Grabbing python packages"
pip3 install black