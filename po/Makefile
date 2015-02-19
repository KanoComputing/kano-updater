APPNAME=kano-updater

MSGLANGS=$(notdir $(wildcard *po))
MSGOBJS=$(addprefix ../locale/,$(MSGLANGS:.po=/LC_MESSAGES/$(APPNAME).mo))

.PHONY: clean messages

build: $(MSGOBJS)

update: $(MSGLANGS)

clean:
	rm -f messages.pot
	rm -rf ../locale

define run-xgettext
xgettext -f PYPOTFILES -L Python --force-po -o messages.pot
xgettext -f CPOTFILES -L C -k_ -kN_ -j -o messages.pot
endef

messages:
	$(run-xgettext)

messages.pot:
	$(run-xgettext)

%.po: messages.pot
	msgmerge -N -U $*.po messages.pot
	touch $*.po

../locale/%/LC_MESSAGES/$(APPNAME).mo: %.po
	mkdir -p $(dir $@)
	msgfmt -c -o $@ $*.po
