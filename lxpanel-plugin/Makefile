# Builds the kano_updater.so widget for LXPanel
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2

CC=gcc
CFLAGS=`pkg-config --cflags lxpanel gtk+-2.0`
LIBS=`pkg-config --libs lxpanel gtk+-2.0` -lkdesk-hourglass
SRC=kano_updater.c parson/parson.c
BIN=kano_updater.so
INSTALL_PATH=/usr/lib/`dpkg-architecture -qDEB_HOST_MULTIARCH`/lxpanel/plugins/

# The liblxpanel.so is not reported by pkg-config, help shlibdeps locate it
LXPANEL_RPATH=-Wl,-rpath=/usr/lib/arm-linux-gnueabihf/lxpanel

.PHONY: init

build: $(BIN)

#init:
#	cd .. && git submodule init
#	cd .. && git submodule update

install: $(BIN)
	install -p -m 0644 $(BIN) $(INSTALL_PATH)

$(BIN): $(SRC)
	$(CC) -Wall $(CFLAGS) -shared -fPIC $(SRC) -o $(BIN) $(LIBS) $(LXPANEL_RPATH)
