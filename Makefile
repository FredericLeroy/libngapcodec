include src/Makefile.am.libasncodec

VERSION=15.2.0

NAME=ngapcodec
LIBNAME=lib$(NAME)
PREFIX?=/usr/local

LIBS += -lm
CFLAGS += $(ASN_MODULE_CFLAGS) -DASN_PDU_COLLECTION -I. -Iinclude/asn1c
ASN_LIBRARY ?= $(LIBNAME).a

.PHONY: install uninstall

all: $(ASN_LIBRARY)

$(ASN_LIBRARY): $(ASN_MODULE_SRCS:.c=.o)
	$(AR) rcs $@ $(ASN_MODULE_SRCS:.c=.o)

.SUFFIXES:
.SUFFIXES: .c .o

.c.o:
	$(CC) $(CFLAGS) -o $@ -c $<

clean:
	rm -f $(ASN_MODULE_SRCS:.c=.o) $(ASN_LIBRARY)

install: $(ASN_LIBRARY)
	# static lib
	mkdir -p $(DESTDIR)$(PREFIX)/lib/$(NAME)/$(VERSION)/
	cp $< $(DESTDIR)$(PREFIX)/lib/$(NAME)/$(VERSION)/
	# c headers
	mkdir -p $(DESTDIR)$(PREFIX)/include/$(NAME)-$(VERSION)
	cp $(ASN_MODULE_HDRS) $(DESTDIR)$(PREFIX)/include/$(NAME)-$(VERSION)
	# asn.1 specifications
	mkdir -p $(DESTDIR)$(PREFIX)/share/libngapcodec/$(VERSION)
	cp asn.1/* $(DESTDIR)$(PREFIX)/share/libngapcodec/$(VERSION)
	# pkgconfig
	mkdir -p $(DESTDIR)$(PREFIX)/share/pkgconfig
	sed $(NAME).pc.in \
		-e "s/@VERSION@/$(VERSION)/g;s/@NAME@/$(NAME)/g;s,@PREFIX@,$(PREFIX),g;s/@LIBNAME@/$(LIBNAME)/g" \
		> $(DESTDIR)$(PREFIX)/share/pkgconfig/$(NAME)-$(VERSION).pc

uninstall:
	rm -vrf $(DESTDIR)$(PREFIX)/lib/$(NAME)/$(VERSION)
	rm -vrf $(DESTDIR)$(PREFIX)/include/$(NAME)-$(VERSION)
	rm -vrf $(DESTDIR)$(PREFIX)/share/libngapcodec/$(VERSION)
	rm -vf  $(DESTDIR)$(PREFIX)/share/pkgconfig/$(NAME)-$(VERSION).pc
