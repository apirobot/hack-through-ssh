#!/bin/sh

apt-get update && apt-get install -y \
  build-essential \
  autoconf \
  libtool \
  pkg-config \
  python-opengl \
  python-imaging \
  python-pyrex \
  python-pyside.qtopengl \
  qt4-dev-tools \
  qt4-designer \
  libqtgui4 \
  libqtcore4 \
  libqt4-xml\
  libqt4-test \
  libqt4-script \
  libqt4-network \
  libqt4-dbus \
  python-qt4 \
  python-qt4-gl \
  libgle3 \
  python-dev \
  virtualenv \
  libssl-dev
