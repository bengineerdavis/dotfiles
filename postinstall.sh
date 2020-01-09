#!/bin/bash
# bring OS up to date


#
echo "Grabbing Fedora packages"
sudo dnf install clamav
sudo dnf install clamtk
# https://github.com/junegunn/fzf
sudo dnf install fzf
sudo dnf install geany
sudo dnf instal libreoffice

# enable virtualization and virt-manager
# https://docs.fedoraproject.org/en-US/quick-docs/getting-started-with-virtualization/

# mandatory pkgs only
# dnf install @virtualization

# with optionals
dnf group install --with-optional virtualization

# start virtualization services/daemon
systemctl start libvirtd

# enable virtualization service on startup
systemctl enable libvirtd

# confirms virtualization w/ kernel properly set:
# look for "kvm_intel" or "kvm_amd" output to confirm proper kernel confirguration
lsmod | grep kvm


# flatpak
echo "fetching flatpak utility"
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

echo "installing flatpak utility"
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

echo "Grabbing flatpak packages"
flatpak install zotero
flatpak install
flatpak install anaconda

# python pkgs
echo "Grabbing python packages"
# https://pypi.org/project/black/
pip3 install black

# https://github.com/bram85/topydo
pip3 install topydo

# 3rd Party repositories

# Atom (linux) link: https://flight-manual.atom.io/getting-started/sections/installing-atom/
# set up repo
sudo rpm --import https://packagecloud.io/AtomEditor/atom/gpgkey
sudo sh -c 'echo -e "[Atom]\nname=Atom Editor\nbaseurl=https://packagecloud.io/AtomEditor/atom/el/7/\$basearch\nenabled=1\ngpgcheck=0\nrepo_gpgcheck=1\ngpgkey=https://packagecloud.io/AtomEditor/atom/gpgkey" > /etc/yum.repos.d/atom.repo'
# Install Atom
sudo dnf install atom
# Install Atom Beta
# sudo dnf install atom-beta
